import cv2
import mediapipe as mp
import math
import os
import time
import winsound
from datetime import datetime


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "face_landmarker.task"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(REPORT_DIR, exist_ok=True)


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
# MOUTH LANDMARKS
# ============================================================

UPPER_LIP = 13
LOWER_LIP = 14

LEFT_MOUTH = 61
RIGHT_MOUTH = 291


# ============================================================
# DISTANCE FUNCTION
# ============================================================

def distance(p1, p2):

    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
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
# SETTINGS
# ============================================================

MOUTH_THRESHOLD = 0.55

YAWN_TIME = 1.0

SOUND_INTERVAL = 3

REPORT_INTERVAL = 5


# ============================================================
# VARIABLES
# ============================================================

yawn_start_time = None

last_sound_time = 0

last_report_time = 0


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)


if not camera.isOpened():

    print("ERROR: Cannot open webcam.")

    exit()


print("Webcam opened successfully.")
print("Yawn detection started.")
print("Press Q to quit.")


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


        height, width, _ = frame.shape


        # ====================================================
        # CONVERT IMAGE
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
        # FACE DETECTION
        # ====================================================

        result = landmarker.detect_for_video(
            mp_image,
            timestamp
        )


        timestamp += 33


        mouth_ratio = 0.0

        status = "Face Not Detected"

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


            mouth_ratio = calculate_mouth_ratio(
                landmarks,
                width,
                height
            )


            # ------------------------------------------------
            # MOUTH POINTS
            # ------------------------------------------------

            upper = landmarks[UPPER_LIP]
            lower = landmarks[LOWER_LIP]

            left = landmarks[LEFT_MOUTH]
            right = landmarks[RIGHT_MOUTH]


            points = [

                (
                    int(upper.x * width),
                    int(upper.y * height)
                ),

                (
                    int(lower.x * width),
                    int(lower.y * height)
                ),

                (
                    int(left.x * width),
                    int(left.y * height)
                ),

                (
                    int(right.x * width),
                    int(right.y * height)
                )
            ]


            # ------------------------------------------------
            # DRAW MOUTH POINTS
            # ------------------------------------------------

            for point in points:

                cv2.circle(
                    frame,
                    point,
                    4,
                    (255, 0, 255),
                    -1
                )


            # =================================================
            # MOUTH OPEN
            # =================================================

            if mouth_ratio > MOUTH_THRESHOLD:

                if yawn_start_time is None:

                    yawn_start_time = time.time()


                duration = (
                    time.time()
                    -
                    yawn_start_time
                )


                # =================================================
                # YAWN DETECTED
                # =================================================

                if duration >= YAWN_TIME:

                    status = "YAWN DETECTED"

                    status_color = (
                        0,
                        0,
                        255
                    )


                    current_time = time.time()


                    # =============================================
                    # WARNING SOUND
                    # =============================================

                    if (
                        current_time -
                        last_sound_time
                        >= SOUND_INTERVAL
                    ):

                        print(
                            "WARNING: YAWN DETECTED!"
                        )


                        winsound.Beep(
                            1200,
                            500
                        )


                        last_sound_time = (
                            current_time
                        )


                    # =============================================
                    # SAVE REPORT
                    # =============================================

                    if (
                        current_time -
                        last_report_time
                        >= REPORT_INTERVAL
                    ):

                        timestamp_text = (
                            datetime.now()
                            .strftime(
                                "%Y-%m-%d_%H-%M-%S"
                            )
                        )


                        image_path = os.path.join(
                            REPORT_DIR,
                            f"yawn_detected_{timestamp_text}.jpg"
                        )


                        cv2.imwrite(
                            image_path,
                            frame
                        )


                        print(
                            "Yawn report saved:"
                        )

                        print(
                            image_path
                        )


                        last_report_time = (
                            current_time
                        )


                else:

                    status = "MOUTH OPEN"

                    status_color = (
                        0,
                        165,
                        255
                    )


            else:

                yawn_start_time = None

                status = "Normal"

                status_color = (
                    0,
                    255,
                    0
                )


        else:

            yawn_start_time = None


        # ====================================================
        # DISPLAY MOUTH RATIO
        # ====================================================

        cv2.putText(
            frame,
            f"Mouth Ratio: {mouth_ratio:.2f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        # ====================================================
        # DISPLAY STATUS
        # ====================================================

        cv2.putText(
            frame,
            f"Status: {status}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            status_color,
            3
        )


        # ====================================================
        # SHOW CAMERA
        # ====================================================

        cv2.imshow(
            "AI Driver - Yawn Detection",
            frame
        )


        # ====================================================
        # PRESS Q
        # ====================================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()

print("Yawn detection stopped.")