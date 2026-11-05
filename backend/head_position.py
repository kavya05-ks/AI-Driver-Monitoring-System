import cv2
import mediapipe as mp
import os
import time
import winsound
import threading
from datetime import datetime


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "face_landmarker.task"
)

REPORTS_FOLDER = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(REPORTS_FOLDER, exist_ok=True)


# ============================================================
# CHECK MODEL
# ============================================================

if not os.path.exists(MODEL_PATH):

    print("ERROR: face_landmarker.task not found!")
    print(MODEL_PATH)

    exit()


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
        model_asset_path=MODEL_PATH
    ),

    running_mode=VisionRunningMode.VIDEO,

    num_faces=1,

    min_face_detection_confidence=0.5,

    min_face_presence_confidence=0.5,

    min_tracking_confidence=0.5
)


# ============================================================
# WARNING SOUND
# ============================================================

def head_warning():

    print("WARNING: DRIVER DISTRACTED!")

    for i in range(2):

        winsound.Beep(
            1400,
            500
        )

        time.sleep(0.2)


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(frame):

    report_time = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    report_path = os.path.join(
        REPORTS_FOLDER,
        f"driver_distracted_{report_time}.jpg"
    )

    cv2.imwrite(
        report_path,
        frame
    )

    print("Distraction report saved:")
    print(report_path)


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)


if not camera.isOpened():

    print("ERROR: Cannot open webcam.")

    exit()


print("========================================")
print("HEAD POSITION MONITORING")
print("========================================")
print("HEAD: FORWARD  -> Normal")
print("HEAD: LEFT     -> Monitoring")
print("HEAD: RIGHT    -> Monitoring")
print("HEAD: DOWN     -> Monitoring")
print("Look away for 2 seconds -> Alert")
print("Press Q to quit")
print("========================================")


# ============================================================
# DISTRACTION SETTINGS
# ============================================================

DISTRACTION_TIME = 2.0

ALARM_COOLDOWN = 3.0

REPORT_COOLDOWN = 5.0

last_alarm_time = 0

last_report_time = 0

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
        # READ CAMERA
        # ====================================================

        ret, frame = camera.read()


        if not ret:

            print("ERROR: Cannot read camera.")

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
        # CONVERT TO RGB
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
        # DEFAULT STATUS
        # ====================================================

        head_status = "FACE NOT DETECTED"

        status_color = (
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
            # LANDMARKS
            # =================================================

            nose = landmarks[1]

            left_face = landmarks[234]

            right_face = landmarks[454]

            forehead = landmarks[10]

            chin = landmarks[152]


            # =================================================
            # CONVERT TO PIXELS
            # =================================================

            nose_x = nose.x * width

            nose_y = nose.y * height

            left_x = left_face.x * width

            right_x = right_face.x * width

            forehead_y = forehead.y * height

            chin_y = chin.y * height


            # =================================================
            # FACE WIDTH
            # =================================================

            face_width = (
                right_x - left_x
            )


            if face_width > 0:

                nose_position = (
                    nose_x - left_x
                ) / face_width


                # =============================================
                # FACE HEIGHT
                # =============================================

                face_height = (
                    chin_y - forehead_y
                )


                if face_height > 0:

                    nose_vertical = (
                        nose_y - forehead_y
                    ) / face_height


                    # =========================================
                    # HEAD LEFT
                    # =========================================

                    if nose_position < 0.38:

                        head_status = "HEAD: LEFT"

                        status_color = (
                            0,
                            165,
                            255
                        )


                    # =========================================
                    # HEAD RIGHT
                    # =========================================

                    elif nose_position > 0.62:

                        head_status = "HEAD: RIGHT"

                        status_color = (
                            0,
                            165,
                            255
                        )


                    # =========================================
                    # HEAD DOWN
                    # =========================================

                    elif nose_vertical > 0.58:

                        head_status = "HEAD: DOWN"

                        status_color = (
                            0,
                            0,
                            255
                        )


                    # =========================================
                    # HEAD FORWARD
                    # =========================================

                    else:

                        head_status = "HEAD: FORWARD"

                        status_color = (
                            0,
                            255,
                            0
                        )


            # =================================================
            # DRAW NOSE
            # =================================================

            nose_point = (
                int(nose_x),
                int(nose_y)
            )


            cv2.circle(
                frame,
                nose_point,
                6,
                (255, 0, 255),
                -1
            )


        # ====================================================
        # TIME-BASED DISTRACTION DETECTION
        # ====================================================

        dangerous_positions = [

            "HEAD: LEFT",

            "HEAD: RIGHT",

            "HEAD: DOWN"

        ]


        if head_status in dangerous_positions:

            current_time = time.time()


            # ================================================
            # START DISTRACTION TIMER
            # ================================================

            if distraction_start_time is None:

                distraction_start_time = current_time

                current_head_direction = head_status


            # ================================================
            # DIRECTION CHANGED - RESTART TIMER
            # ================================================

            elif current_head_direction != head_status:

                distraction_start_time = current_time

                current_head_direction = head_status


            # ================================================
            # CALCULATE DISTRACTION TIME
            # ================================================

            distraction_duration = (
                current_time -
                distraction_start_time
            )


            # ================================================
            # DRIVER DISTRACTED
            # ================================================

            if distraction_duration >= DISTRACTION_TIME:

                cv2.putText(
                    frame,
                    "DRIVER DISTRACTED!",
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    3
                )


                # ============================================
                # WARNING SOUND
                # ============================================

                if (
                    current_time -
                    last_alarm_time
                    >= ALARM_COOLDOWN
                ):

                    last_alarm_time = current_time

                    threading.Thread(
                        target=head_warning,
                        daemon=True
                    ).start()


                # ============================================
                # SAVE REPORT
                # ============================================

                if (
                    current_time -
                    last_report_time
                    >= REPORT_COOLDOWN
                ):

                    save_report(
                        frame
                    )

                    last_report_time = current_time


        else:

            # ================================================
            # DRIVER LOOKING FORWARD
            # RESET TIMER
            # ================================================

            distraction_start_time = None

            current_head_direction = None


        # ====================================================
        # DISPLAY STATUS
        # ====================================================

        cv2.putText(
            frame,
            head_status,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            status_color,
            3
        )


        # ====================================================
        # DISPLAY TIMER
        # ====================================================

        if distraction_start_time is not None:

            elapsed_time = (
                time.time() -
                distraction_start_time
            )

            cv2.putText(
                frame,
                f"Distraction Time: {elapsed_time:.1f}s",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )


        # ====================================================
        # DISPLAY INFORMATION
        # ====================================================

        cv2.putText(
            frame,
            "Forward = Normal",
            (20, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )


        # ====================================================
        # DISPLAY CAMERA
        # ====================================================

        cv2.imshow(
            "AI Driver - Head Position",
            frame
        )


        # ====================================================
        # PRESS Q TO QUIT
        # ====================================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()

print("Head position monitoring stopped.")