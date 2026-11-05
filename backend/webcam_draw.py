import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot open webcam")
    exit()

while True:

    ret, frame = camera.read()

    if not ret:
        print("Failed to read frame")
        break

    # Draw Rectangle
    cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 2)

    # Draw Circle
    cv2.circle(frame, (200, 200), 40, (255, 0, 0), 2)

    # Draw Line
    cv2.line(frame, (50, 50), (400, 50), (0, 0, 255), 2)

    # Display Text
    cv2.putText(
        frame,
        "AI Driver Safety System",
        (30, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.imshow("AI Driver Safety", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()