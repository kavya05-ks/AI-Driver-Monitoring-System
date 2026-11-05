import cv2

# Read image
image = cv2.imread("C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/person.JPG")

if image is None:
    print("Image not found!")
    exit()

# Original size
print("Original Size:", image.shape)

# Resize image
resized = cv2.resize(image, (500, 500))

print("Resized Size:", resized.shape)

# Display both images
cv2.imshow("Original Image", image)
cv2.imshow("Resized Image", resized)

cv2.waitKey(0)
cv2.destroyAllWindows()