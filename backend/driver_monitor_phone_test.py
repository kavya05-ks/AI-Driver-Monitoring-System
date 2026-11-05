import cv2
import os
import time
import winsound
from datetime import datetime
from ultralytics import YOLO


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "yolo11n.pt"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(REPORT_DIR, exist_ok=True)


# ============================================================
# CHECK YOLO MODEL
# ============================================================

print("Starting AI Driver Phone Monitoring...")

if not os.path.exists(MODEL_PATH):

    print("ERROR: YOLO model not found!")

    print("Expected location:")
    print(MODEL_PATH)

    exit()


# ============================================================
# LOAD YOLO MODEL
# ============================================================

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded successfully.")


# ============================================================
# OPEN WEBCAM
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Unable to open webcam.")

    exit()


print("Webcam opened successfully.")
print("Phone monitoring started.")
print("Press Q to quit.")


# ============================================================
# VARIABLES
# ============================================================

# Screenshot/report timing
last_report_time = 0
REPORT_INTERVAL = 5


# Warning sound timing
last_sound_time = 0
SOUND_INTERVAL = 3


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # READ CAMERA FRAME
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:

        print("ERROR: Unable to read camera frame.")

        break


    # --------------------------------------------------------
    # YOLO DETECTION
    # --------------------------------------------------------

    results = model(
        frame,
        conf=0.40,
        verbose=False
    )


    # Initially assume no phone
    phone_detected = False


    # --------------------------------------------------------
    # CHECK DETECTED OBJECTS
    # --------------------------------------------------------

    for result in results:

        if result.boxes is None:
            continue


        for box in result.boxes:

            # Class ID
            class_id = int(box.cls[0])

            # Confidence
            confidence = float(box.conf[0])

            # Class name
            class_name = model.names[class_id]


            # ------------------------------------------------
            # PHONE DETECTED
            # ------------------------------------------------

            if class_name.lower() == "cell phone":

                phone_detected = True


                # Get bounding box
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )


                # Draw red rectangle
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    3
                )


                # Display confidence
                label = (
                    f"PHONE "
                    f"{confidence:.2f}"
                )


                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )


    # ========================================================
    # PHONE DETECTED ACTIONS
    # ========================================================

    if phone_detected:


        # ----------------------------------------------------
        # DISPLAY PHONE DETECTED
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "PHONE DETECTED",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )


        # Current time
        current_time = time.time()


        # ----------------------------------------------------
        # WARNING SOUND
        # ----------------------------------------------------

        if (
            current_time - last_sound_time
            >= SOUND_INTERVAL
        ):

            print("WARNING: PHONE DETECTED!")

            # Windows warning beep
            winsound.Beep(
                1000,   # frequency
                500     # duration in milliseconds
            )

            last_sound_time = current_time


        # ----------------------------------------------------
        # SAVE SCREENSHOT / REPORT
        # ----------------------------------------------------

        if (
            current_time - last_report_time
            >= REPORT_INTERVAL
        ):

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )


            filename = os.path.join(
                REPORT_DIR,
                f"phone_detected_{timestamp}.jpg"
            )


            cv2.imwrite(
                filename,
                frame
            )


            print(
                "Phone detection report saved:"
            )

            print(filename)


            last_report_time = current_time


    # ========================================================
    # NO PHONE
    # ========================================================

    else:

        cv2.putText(
            frame,
            "NO PHONE",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            3
        )


    # ========================================================
    # DISPLAY CAMERA
    # ========================================================

    cv2.imshow(
        "AI Driver - Phone Monitoring",
        frame
    )


    # ========================================================
    # PRESS Q TO EXIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

print("Phone monitoring stopped.")