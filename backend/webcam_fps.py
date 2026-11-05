import cv2
import time

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot open webcam")
    exit()

previous_time = time.time()

while True:

    ret, frame = camera.read()

    if not ret:
        break

    # Current time
    current_time = time.time()

    # Calculate FPS
    fps = 1 / (current_time - previous_time)

    previous_time = current_time

    # Display FPS
    cv2.putText(
        frame,
        f"FPS: {int(fps)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("AI Driver Safety", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()