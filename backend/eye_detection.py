import cv2
import mediapipe as mp
import math


# ============================================================
# MediaPipe Tasks
# ============================================================

BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = r"..\models\face_landmarker.task"


# ============================================================
# FACE LANDMARKER OPTIONS
# ============================================================

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
# EYE LANDMARKS
# ============================================================

LEFT_EYE = [362, 385, 387, 263, 373, 380]

RIGHT_EYE = [33, 160, 158, 133, 153, 144]


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
    ) / (2.0 * horizontal)


# ============================================================
# OPEN CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("Cannot open webcam")
    exit()


# ============================================================
# CREATE FACE LANDMARKER
# ============================================================

with FaceLandmarker.create_from_options(options) as landmarker:

    frame_timestamp = 0

    while True:

        ret, frame = camera.read()

        if not ret:

            print("Failed to capture frame")
            break


        # ----------------------------------------------------
        # Convert BGR → RGB
        # ----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # ----------------------------------------------------
        # Create MediaPipe Image
        # ----------------------------------------------------

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )


        # ----------------------------------------------------
        # Detect face landmarks
        # ----------------------------------------------------

        result = landmarker.detect_for_video(
            mp_image,
            frame_timestamp
        )

        frame_timestamp += 33


        # ----------------------------------------------------
        # Default status
        # ----------------------------------------------------

        status = "Face Not Detected"
        status_color = (0, 0, 255)

        ear = 0


        # ----------------------------------------------------
        # Face detected
        # ----------------------------------------------------

        if result.face_landmarks:

            face_landmarks = result.face_landmarks[0]

            h, w, _ = frame.shape


            # ------------------------------------------------
            # Get eye coordinates
            # ------------------------------------------------

            left_eye = []

            right_eye = []


            for index in LEFT_EYE:

                landmark = face_landmarks[index]

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                left_eye.append(
                    (x, y)
                )


            for index in RIGHT_EYE:

                landmark = face_landmarks[index]

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                right_eye.append(
                    (x, y)
                )


            # ------------------------------------------------
            # Calculate EAR
            # ------------------------------------------------

            left_ear = calculate_ear(
                left_eye
            )

            right_ear = calculate_ear(
                right_eye
            )

            ear = (
                left_ear + right_ear
            ) / 2.0


            status = "Alert"
            status_color = (0, 255, 0)


            # ------------------------------------------------
            # Draw eye landmarks
            # ------------------------------------------------

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


        # ----------------------------------------------------
        # Display EAR
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"EAR: {ear:.2f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        # ----------------------------------------------------
        # Display status
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Status: {status}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            status_color,
            3
        )


        # ----------------------------------------------------
        # Show camera
        # ----------------------------------------------------

        cv2.imshow(
            "AI Driver Eye Detection",
            frame
        )


        # ----------------------------------------------------
        # Press Q to close
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


# ============================================================
# RELEASE CAMERA
# ============================================================

camera.release()

cv2.destroyAllWindows()

print("Eye detection stopped.")