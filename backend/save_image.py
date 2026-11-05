import cv2

image = cv2.imread("C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/person.JPG")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

cv2.imwrite("C:/Users/kusum/OneDrive/Desktop/AI_Driver/images/gray.jpg", gray)

cv2.imshow("Gray", gray)

cv2.waitKey(0)
cv2.destroyAllWindows()