import cv2
import mediapipe as mp
import math
import time
import winsound
import threading
import os
import sys

from datetime import datetime
from ultralytics import YOLO

from event_logger import log_event
from sms_alert import send_alert


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODELS_FOLDER = os.path.join(
    BASE_DIR,
    "models"
)

REPORTS_FOLDER = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(REPORTS_FOLDER, exist_ok=True)


# ============================================================
# CURRENT DRIVER
# ============================================================

if len(sys.argv) > 1:

    CURRENT_USERNAME = sys.argv[1]

else:

    CURRENT_USERNAME = None


print()
print(
    "Current Driver:",
    CURRENT_USERNAME
)


# ============================================================
# MODEL PATHS
# ============================================================

FACE_MODEL_PATH = os.path.join(
    MODELS_FOLDER,
    "face_landmarker.task"
)

YOLO_MODEL_PATH = os.path.join(
    MODELS_FOLDER,
    "yolo11n.pt"
)


# ============================================================
# CHECK MODELS
# ============================================================

if not os.path.exists(FACE_MODEL_PATH):

    print("ERROR: face_landmarker.task not found!")
    print(FACE_MODEL_PATH)
    exit()


if not os.path.exists(YOLO_MODEL_PATH):

    print("ERROR: yolo11n.pt not found!")
    print(YOLO_MODEL_PATH)
    exit()


# ============================================================
# EVENT LOGGER
# ============================================================

last_logged = {}

EVENT_COOLDOWN = 5


def log_once(event_name, severity="INFO"):

    current_time = time.time()

    if event_name not in last_logged:

        log_event(
            event_name,
            severity,
            CURRENT_USERNAME
        )

        last_logged[event_name] = current_time

    elif (
        current_time - last_logged[event_name]
        >= EVENT_COOLDOWN
    ):

        log_event(
            event_name,
            severity,
            CURRENT_USERNAME
        )

        last_logged[event_name] = current_time


# ============================================================
# SMS ALERT COOLDOWN
# ============================================================

last_sms_sent = {}

SMS_COOLDOWN = 10


def send_sms_once(alert_type):

    if not CURRENT_USERNAME:

        print(
            "No driver username received."
        )

        return


    current_time = time.time()


    # ========================================================
    # FIRST SMS
    # ========================================================

    if alert_type not in last_sms_sent:

        last_sms_sent[
            alert_type
        ] = current_time


        threading.Thread(

            target=send_alert,

            args=(

                CURRENT_USERNAME,

                alert_type

            ),

            daemon=True

        ).start()


        print(
            f"SMS ALERT SENT: {alert_type}"
        )


    # ========================================================
    # SEND AGAIN ONLY AFTER 10 SECONDS
    # ========================================================

    elif (

        current_time
        -
        last_sms_sent[alert_type]

        >=
        SMS_COOLDOWN

    ):

        last_sms_sent[
            alert_type
        ] = current_time


        threading.Thread(

            target=send_alert,

            args=(

                CURRENT_USERNAME,

                alert_type

            ),

            daemon=True

        ).start()


        print(
            f"SMS ALERT SENT: {alert_type}"
        )


# ============================================================
# LOAD YOLO
# ============================================================

print("Loading YOLO model...")

phone_model = YOLO(
    YOLO_MODEL_PATH
)

print("YOLO model loaded successfully.")


# ============================================================
# MEDIAPIPE
# ============================================================

BaseOptions = mp.tasks.BaseOptions

VisionRunningMode = mp.tasks.vision.RunningMode

FaceLandmarker = mp.tasks.vision.FaceLandmarker

FaceLandmarkerOptions = (
    mp.tasks.vision.FaceLandmarkerOptions
)


options = FaceLandmarkerOptions(

    base_options=BaseOptions(
        model_asset_path=FACE_MODEL_PATH
    ),

    running_mode=VisionRunningMode.VIDEO,

    num_faces=1,

    min_face_detection_confidence=0.5,

    min_face_presence_confidence=0.5,

    min_tracking_confidence=0.5
)


# ============================================================
# EYE LANDMARKS
# ============================================================

LEFT_EYE = [
    362,
    385,
    387,
    263,
    373,
    380
]

RIGHT_EYE = [
    33,
    160,
    158,
    133,
    153,
    144
]


# ============================================================
# MOUTH LANDMARKS
# ============================================================

UPPER_LIP = 13
LOWER_LIP = 14

LEFT_MOUTH = 61
RIGHT_MOUTH = 291


# ============================================================
# DISTANCE
# ============================================================

def distance(p1, p2):

    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


# ============================================================
# EAR CALCULATION
# ============================================================

def calculate_ear(eye):

    vertical_1 = distance(
        eye[1],
        eye[5]
    )

    vertical_2 = distance(
        eye[2],
        eye[4]
    )

    horizontal = distance(
        eye[0],
        eye[3]
    )

    if horizontal == 0:
        return 0

    return (
        vertical_1 + vertical_2
    ) / (
        2.0 * horizontal
    )


# ============================================================
# MOUTH RATIO
# ============================================================

def calculate_mouth_ratio(
    landmarks,
    width,
    height
):

    upper = landmarks[UPPER_LIP]
    lower = landmarks[LOWER_LIP]

    left = landmarks[LEFT_MOUTH]
    right = landmarks[RIGHT_MOUTH]

    upper_point = (
        int(upper.x * width),
        int(upper.y * height)
    )

    lower_point = (
        int(lower.x * width),
        int(lower.y * height)
    )

    left_point = (
        int(left.x * width),
        int(left.y * height)
    )

    right_point = (
        int(right.x * width),
        int(right.y * height)
    )

    vertical = distance(
        upper_point,
        lower_point
    )

    horizontal = distance(
        left_point,
        right_point
    )

    if horizontal == 0:
        return 0

    return vertical / horizontal


# ============================================================
# WARNING SOUNDS
# ============================================================

def drowsiness_alarm():

    print("WARNING: DROWSINESS!")

    for _ in range(3):

        winsound.Beep(
            1000,
            500
        )

        time.sleep(0.2)


def phone_alarm():

    print("WARNING: PHONE DETECTED!")

    for _ in range(2):

        winsound.Beep(
            1500,
            400
        )

        time.sleep(0.2)


def yawn_alarm():

    print("WARNING: YAWN DETECTED!")

    for _ in range(2):

        winsound.Beep(
            1200,
            500
        )

        time.sleep(0.2)


def head_alarm():

    print("WARNING: DRIVER DISTRACTED!")

    for _ in range(2):

        winsound.Beep(
            1400,
            500
        )

        time.sleep(0.2)


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(
    frame,
    report_type
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    filename = (
        f"{report_type}_{timestamp}.jpg"
    )

    path = os.path.join(
        REPORTS_FOLDER,
        filename
    )

    cv2.imwrite(
        path,
        frame
    )

    print(
        f"{report_type.upper()} report saved:"
    )

    print(path)


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)


if not camera.isOpened():

    print("ERROR: Cannot open webcam.")
    exit()


print()
print("============================================")
print("       AI DRIVER MONITORING SYSTEM")
print("============================================")
print(
    "Current Driver   :",
    CURRENT_USERNAME
)
print("Drowsiness       : ON")
print("Phone Detection  : ON")
print("Yawn Detection   : ON")
print("Head Position    : ON")
print("Distraction      : ON")
print("Event Logging    : ON")
print("SMS Alert        : ON")
print("SMS Cooldown     : 10 seconds")
print("Warning Sound    : ON")
print("Reports          : ON")
print("============================================")
print("Press Q to exit.")
print()


# ============================================================
# DROWSINESS SETTINGS
# ============================================================

EAR_THRESHOLD = 0.21

CLOSED_TIME = 2.0

eyes_closed_start = None

drowsy_alarm_running = False


# ============================================================
# YAWN SETTINGS
# ============================================================

MOUTH_THRESHOLD = 0.55

YAWN_TIME = 1.0

yawn_start_time = None

yawn_alarm_running = False


# ============================================================
# PHONE SETTINGS
# ============================================================

PHONE_CONFIDENCE = 0.40

phone_alarm_running = False


# ============================================================
# HEAD / DISTRACTION SETTINGS
# ============================================================

DISTRACTION_TIME = 2.0

HEAD_ALARM_COOLDOWN = 3.0

HEAD_REPORT_COOLDOWN = 5.0

last_head_alarm = 0

last_head_report = 0

distraction_start_time = None

current_head_direction = None


# ============================================================
# FACE LANDMARKER
# ============================================================

with FaceLandmarker.create_from_options(
    options
) as landmarker:

    timestamp = 0

    while True:

        # ====================================================
        # CAMERA FRAME
        # ====================================================

        ret, frame = camera.read()

        if not ret:

            print(
                "ERROR: Failed to capture frame."
            )

            break


        # ====================================================
        # FLIP CAMERA
        # ====================================================

        frame = cv2.flip(
            frame,
            1
        )

        height, width, _ = frame.shape


        # ====================================================
        # PHONE DETECTION
        # ====================================================

        phone_detected = False

        phone_results = phone_model(
            frame,
            conf=PHONE_CONFIDENCE,
            verbose=False
        )

        for result in phone_results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )

                confidence = float(
                    box.conf[0]
                )

                class_name = (
                    phone_model.names[class_id]
                )

                if (
                    class_name.lower()
                    == "cell phone"
                ):

                    phone_detected = True

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0]
                    )

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
                        3
                    )

                    cv2.putText(
                        frame,
                        f"PHONE {confidence:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )


        # ====================================================
        # MEDIAPIPE IMAGE
        # ====================================================

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )


        # ====================================================
        # FACE LANDMARK DETECTION
        # ====================================================

        result = landmarker.detect_for_video(
            mp_image,
            timestamp
        )

        timestamp += 33


        # ====================================================
        # DEFAULT VALUES
        # ====================================================

        ear = 0.0

        mouth_ratio = 0.0

        main_status = "FACE NOT DETECTED"

        main_status_color = (
            0,
            0,
            255
        )

        head_status = "HEAD: UNKNOWN"

        head_color = (
            0,
            0,
            255
        )


        # ====================================================
        # FACE FOUND
        # ====================================================

        if result.face_landmarks:

            landmarks = result.face_landmarks[0]


            # =================================================
            # EYE POINTS
            # =================================================

            left_eye = []

            right_eye = []

            for index in LEFT_EYE:

                landmark = landmarks[index]

                point = (
                    int(landmark.x * width),
                    int(landmark.y * height)
                )

                left_eye.append(point)


            for index in RIGHT_EYE:

                landmark = landmarks[index]

                point = (
                    int(landmark.x * width),
                    int(landmark.y * height)
                )

                right_eye.append(point)


            # =================================================
            # EAR
            # =================================================

            left_ear = calculate_ear(
                left_eye
            )

            right_ear = calculate_ear(
                right_eye
            )

            ear = (
                left_ear +
                right_ear
            ) / 2.0


            # =================================================
            # MOUTH RATIO
            # =================================================

            mouth_ratio = calculate_mouth_ratio(
                landmarks,
                width,
                height
            )


            # =================================================
            # DROWSINESS
            # =================================================

            if ear < EAR_THRESHOLD:

                if eyes_closed_start is None:

                    eyes_closed_start = time.time()


                closed_duration = (
                    time.time()
                    -
                    eyes_closed_start
                )


                if closed_duration >= CLOSED_TIME:

                    main_status = "DROWSY"

                    main_status_color = (
                        0,
                        0,
                        255
                    )


                    if not drowsy_alarm_running:

                        save_report(
                            frame,
                            "drowsy"
                        )

                        log_once(
                            "DROWSINESS",
                            "HIGH"
                        )

                        send_sms_once(
                            "DROWSINESS DETECTED"
                        )

                        drowsy_alarm_running = True

                        threading.Thread(
                            target=drowsiness_alarm,
                            daemon=True
                        ).start()


                else:

                    main_status = "EYES CLOSED"

                    main_status_color = (
                        0,
                        165,
                        255
                    )


            else:

                eyes_closed_start = None

                drowsy_alarm_running = False

                main_status = "ALERT"

                main_status_color = (
                    0,
                    255,
                    0
                )


            # =================================================
            # YAWN
            # =================================================

            if mouth_ratio > MOUTH_THRESHOLD:

                if yawn_start_time is None:

                    yawn_start_time = time.time()


                yawn_duration = (
                    time.time()
                    -
                    yawn_start_time
                )


                if yawn_duration >= YAWN_TIME:

                    if main_status != "DROWSY":

                        main_status = "YAWN DETECTED"

                        main_status_color = (
                            0,
                            0,
                            255
                        )


                    if not yawn_alarm_running:

                        save_report(
                            frame,
                            "yawn_detected"
                        )

                        log_once(
                            "YAWN DETECTED",
                            "MEDIUM"
                        )

                        send_sms_once(
                            "YAWN DETECTED"
                        )

                        yawn_alarm_running = True

                        threading.Thread(
                            target=yawn_alarm,
                            daemon=True
                        ).start()


                else:

                    if main_status != "DROWSY":

                        main_status = "MOUTH OPEN"

                        main_status_color = (
                            0,
                            165,
                            255
                        )


            else:

                yawn_start_time = None

                yawn_alarm_running = False


            # =================================================
            # HEAD POSITION
            # =================================================

            nose = landmarks[1]

            left_face = landmarks[234]

            right_face = landmarks[454]

            forehead = landmarks[10]

            chin = landmarks[152]


            nose_x = nose.x * width

            nose_y = nose.y * height

            left_x = left_face.x * width

            right_x = right_face.x * width

            forehead_y = forehead.y * height

            chin_y = chin.y * height


            face_width = (
                right_x - left_x
            )


            if face_width > 0:

                nose_position = (
                    nose_x - left_x
                ) / face_width


                face_height = (
                    chin_y - forehead_y
                )


                if face_height > 0:

                    nose_vertical = (
                        nose_y - forehead_y
                    ) / face_height


                    if nose_position < 0.38:

                        head_status = "HEAD: LEFT"

                        head_color = (
                            0,
                            165,
                            255
                        )


                    elif nose_position > 0.62:

                        head_status = "HEAD: RIGHT"

                        head_color = (
                            0,
                            165,
                            255
                        )


                    elif nose_vertical > 0.58:

                        head_status = "HEAD: DOWN"

                        head_color = (
                            0,
                            0,
                            255
                        )


                    else:

                        head_status = "HEAD: FORWARD"

                        head_color = (
                            0,
                            255,
                            0
                        )


            # =================================================
            # DRAW EYES
            # =================================================

            for point in left_eye:

                cv2.circle(
                    frame,
                    point,
                    3,
                    (0, 255, 255),
                    -1
                )


            for point in right_eye:

                cv2.circle(
                    frame,
                    point,
                    3,
                    (0, 255, 255),
                    -1
                )


            # =================================================
            # DRAW MOUTH
            # =================================================

            mouth_points = [

                landmarks[UPPER_LIP],
                landmarks[LOWER_LIP],
                landmarks[LEFT_MOUTH],
                landmarks[RIGHT_MOUTH]

            ]


            for landmark in mouth_points:

                point = (
                    int(landmark.x * width),
                    int(landmark.y * height)
                )

                cv2.circle(
                    frame,
                    point,
                    4,
                    (255, 0, 255),
                    -1
                )


            # =================================================
            # DRAW NOSE
            # =================================================

            cv2.circle(
                frame,
                (
                    int(nose_x),
                    int(nose_y)
                ),
                6,
                (255, 0, 255),
                -1
            )


        else:

            eyes_closed_start = None

            yawn_start_time = None

            drowsy_alarm_running = False

            yawn_alarm_running = False


        # ====================================================
        # PHONE WARNING + EVENT LOGGING + SMS
        # ====================================================

        if phone_detected:

            cv2.putText(
                frame,
                "PHONE DETECTED",
                (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.85,
                (0, 0, 255),
                3
            )


            if not phone_alarm_running:

                save_report(
                    frame,
                    "phone_detected"
                )

                log_once(
                    "PHONE DETECTED",
                    "HIGH"
                )

                send_sms_once(
                    "PHONE DETECTED"
                )

                phone_alarm_running = True

                threading.Thread(
                    target=phone_alarm,
                    daemon=True
                ).start()


        else:

            phone_alarm_running = False


        # ====================================================
        # TIME-BASED HEAD DISTRACTION DETECTION
        # ====================================================

        dangerous_head_positions = [

            "HEAD: LEFT",
            "HEAD: RIGHT",
            "HEAD: DOWN"

        ]


        if head_status in dangerous_head_positions:

            current_time = time.time()


            if distraction_start_time is None:

                distraction_start_time = current_time

                current_head_direction = head_status


            elif current_head_direction != head_status:

                distraction_start_time = current_time

                current_head_direction = head_status


            distraction_duration = (
                current_time
                -
                distraction_start_time
            )


            if distraction_duration >= DISTRACTION_TIME:

                cv2.putText(
                    frame,
                    "DRIVER DISTRACTED!",
                    (20, 190),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.85,
                    (0, 0, 255),
                    3
                )


                # =================================================
                # HEAD ALARM
                # =================================================

                if (
                    current_time
                    -
                    last_head_alarm
                    >= HEAD_ALARM_COOLDOWN
                ):

                    last_head_alarm = current_time

                    threading.Thread(
                        target=head_alarm,
                        daemon=True
                    ).start()


                # =================================================
                # HEAD REPORT + EVENT LOG + SMS
                # =================================================

                if (
                    current_time
                    -
                    last_head_report
                    >= HEAD_REPORT_COOLDOWN
                ):

                    save_report(
                        frame,
                        "driver_distracted"
                    )

                    log_once(
                        "DRIVER DISTRACTED",
                        "HIGH"
                    )

                    send_sms_once(
                        "DRIVER DISTRACTED"
                    )

                    last_head_report = current_time


        else:

            distraction_start_time = None

            current_head_direction = None


        # ====================================================
        # DISPLAY EAR
        # ====================================================

        cv2.putText(
            frame,
            f"EAR: {ear:.2f}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        # ====================================================
        # DISPLAY MOUTH
        # ====================================================

        cv2.putText(
            frame,
            f"Mouth: {mouth_ratio:.2f}",
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        # ====================================================
        # MAIN STATUS
        # ====================================================

        cv2.putText(
            frame,
            f"Status: {main_status}",
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            main_status_color,
            3
        )


        # ====================================================
        # HEAD STATUS
        # ====================================================

        cv2.putText(
            frame,
            head_status,
            (20, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            head_color,
            3
        )


        # ====================================================
        # CURRENT DRIVER DISPLAY
        # ====================================================

        cv2.putText(
            frame,
            f"Driver: {CURRENT_USERNAME if CURRENT_USERNAME else 'Unknown'}",
            (20, 225),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        # ====================================================
        # CAMERA WINDOW
        # ====================================================

        cv2.imshow(
            "AI Driver Monitoring - All Features",
            frame
        )


        # ====================================================
        # QUIT
        # ====================================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()

print()
print("============================================")
print("AI DRIVER MONITORING STOPPED")
print("============================================")