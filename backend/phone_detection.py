import cv2
from ultralytics import YOLO
import os

# ============================================================
# PHONE DETECTION TEST
# ============================================================

# Path to YOLO model
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "models",
    "yolo11n.pt"
)

# Load YOLO model
print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded successfully.")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Unable to open webcam.")
    exit()

print("Webcam opened successfully.")
print("Show your phone in front of the camera.")
print("Press Q to quit.")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Unable to read frame.")
        break

    # Run YOLO detection
    results = model(
        frame,
        conf=0.40,
        verbose=False
    )

    # Get first result
    result = results[0]

    # Create copy for displaying
    display_frame = frame.copy()

    phone_detected = False

    # ========================================================
    # CHECK DETECTED OBJECTS
    # ========================================================

    if result.boxes is not None:

        for box in result.boxes:

            # Get class ID
            class_id = int(box.cls[0])

            # Get class name
            class_name = model.names[class_id]

            # Get confidence
            confidence = float(box.conf[0])

            # Check for cell phone
            if class_name.lower() == "cell phone":

                phone_detected = True

                # Get bounding box coordinates
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                # Draw rectangle
                cv2.rectangle(
                    display_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    2
                )

                # Display label
                label = f"PHONE {confidence:.2f}"

                cv2.putText(
                    display_frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

    # ========================================================
    # DISPLAY STATUS
    # ========================================================

    if phone_detected:

        status = "PHONE DETECTED"

        cv2.putText(
            display_frame,
            status,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

    else:

        status = "NO PHONE"

        cv2.putText(
            display_frame,
            status,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            3
        )

    # ========================================================
    # SHOW CAMERA
    # ========================================================

    cv2.imshow(
        "AI Driver - Phone Detection Test",
        display_frame
    )

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# RELEASE RESOURCES
# ============================================================

cap.release()
cv2.destroyAllWindows()

print("Phone detection test stopped.")