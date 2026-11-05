import cv2

# Read image
image = cv2.imread("C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/person.JPG")

if image is None:
    print("Image not found!")
    exit()

# Rotate 90 degrees clockwise
rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

# Flip horizontally
flip_horizontal = cv2.flip(image, 1)

# Flip vertically
flip_vertical = cv2.flip(image, 0)

# Display images
cv2.imshow("Original", image)
cv2.imshow("Rotated", rotated)
cv2.imshow("Horizontal Flip", flip_horizontal)
cv2.imshow("Vertical Flip", flip_vertical)

cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/rotated.jpg", rotated)
cv2.imwrite("C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/flipped.jpg", flip_horizontal)