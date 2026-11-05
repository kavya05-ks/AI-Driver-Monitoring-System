import cv2

camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()

    if not success:
        print("Failed to open camera")
        break

    cv2.imshow("AI Driver Safety System", frame)

    key = cv2.waitKey(1)

    if key == ord('q') or key == 27:   # q or ESC
        print("Closing...")
        break

camera.release()
cv2.destroyAllWindows()