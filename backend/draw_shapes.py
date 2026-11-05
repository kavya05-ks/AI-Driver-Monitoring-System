import cv2

image = cv2.imread("C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/person.JPG")

if image is None:
    print("Image not found!")
    exit()

# Draw a blue line
cv2.line(image, (50, 50), (300, 50), (255, 0, 0), 3)

# Draw a green rectangle
cv2.rectangle(image, (80, 100), (300, 300), (0, 255, 0), 3)

# Draw a red circle
cv2.circle(image, (200, 200), 50, (0, 0, 255), 3)

# Add text
cv2.putText(
    image,
    "AI Driver Safety",
    (40, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255, 255, 255),
    2
)

cv2.imshow("Drawing Shapes", image)

cv2.waitKey(0)

cv2.destroyAllWindows()