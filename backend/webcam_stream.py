import cv2

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot open webcam")
    exit()

while True:
    # Read one frame
    ret, frame = camera.read()

    if not ret:
        print("Failed to capture frame")
        break

    # Show the frame
    cv2.imshow("Live Webcam", frame)

    # Press 'q' to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()