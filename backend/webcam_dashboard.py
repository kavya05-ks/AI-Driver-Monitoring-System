import cv2
import time

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot open webcam")
    exit()

previous_time = time.time()
frame_count = 0

while True:

    ret, frame = camera.read()

    if not ret:
        break

    frame_count += 1

    # FPS Calculation
    current_time = time.time()
    fps = 1 / (current_time - previous_time)
    previous_time = current_time

    # Current Time
    current_clock = time.strftime("%H:%M:%S")

    # Project Title
    cv2.putText(
        frame,
        "AI Driver Safety System",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    # FPS
    cv2.putText(
        frame,
        f"FPS : {int(fps)}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    # Time
    cv2.putText(
        frame,
        f"Time : {current_clock}",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    # Frame Count
    cv2.putText(
        frame,
        f"Frames : {frame_count}",
        (20, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 0, 0),
        2
    )

    # Camera Status
    cv2.putText(
        frame,
        "Status : Camera Running",
        (20, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("AI Driver Dashboard", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()