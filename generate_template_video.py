""" A template script for computer vision projects """
import cv2
from time import sleep
import numpy as np

camera_index = 2
cam = cv2.VideoCapture(camera_index)

while not cam.isOpened():
	cam = cv2.VideoCapture(camera_index)
	print("Waiting for camera...")
	sleep(0.05)

# frame = cv2.imread('img0.png')

q_unicode = ord('q')

roi = ((230, 170), (360, 270))

while True:
	_, frame = cam.read()

	crop_img = frame[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]

	hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
	msk = cv2.inRange(hsv, np.array([110, 0, 85]), np.array([180, 58, 255]))
	filtered = cv2.bitwise_and(crop_img, crop_img, mask= msk)

	kernel = np.ones((5, 5), np.uint8)
	kernel_erode = np.ones((1, 1), np.uint8) 
	
	img_erosion = cv2.erode(filtered, kernel_erode, iterations=1) 
	cv2.imshow('Frame eroded', img_erosion)
	img_dilation = cv2.dilate(img_erosion, kernel, iterations=1)
	cv2.imshow('Frame dilated', img_dilation)

	grayF = cv2.cvtColor(img_erosion, cv2.COLOR_BGR2GRAY)# Load image, grayscale, Gaussian blur, Otsu's threshold
	blurF = cv2.GaussianBlur(grayF, (3,3), 0)
	threshF = cv2.threshold(blurF, 0, 255, cv2.THRESH_BINARY)[1]
	

	cv2.imshow('Frame', frame)
	cv2.imshow('Frame Filtered', threshF)


	key = cv2.waitKey(1)
	if key == q_unicode: # If 'q' is pressed, close program (Its case sensitive)
		break

	if key == ord('b'):
		cv2.imwrite('template0.png', threshF)

cv2.destroyAllWindows()
