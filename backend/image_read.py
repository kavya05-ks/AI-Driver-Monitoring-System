import cv2
import os

print("Current Folder:", os.getcwd())

path = "C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/person.JPG"

print("File Exists:", os.path.exists(path))

image = cv2.imread(path)

print("Image:", image)

if image is None:
    print("Image not found!")
    exit()

cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()