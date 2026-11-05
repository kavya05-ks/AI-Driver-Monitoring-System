import cv2

# Read image
image = cv2.imread("C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/person.JPG")

if image is None:
    print("Image not found!")
    exit()

# Crop image
cropped = image[150:450, 200:500]

# Display images
cv2.imshow("Original", image)
cv2.imshow("Cropped", cropped)

cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/cropped.jpg", cropped)