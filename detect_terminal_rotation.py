import cv2
from time import sleep
import numpy as np
import math

def rotarGrad(originx, originy, angle, rad):
	return (round(originx+rad*math.cos(-math.radians(angle))), round(originy+rad*math.sin(-math.radians(angle))))

cap = cv2.VideoCapture(2)
roi = ((220, 160), (370, 270))
roi_center = (int(roi[0][0] + (roi[1][0] - roi[0][0])/2), int(roi[0][1] + (roi[1][1] - roi[0][1])/2))
template = cv2.imread('template_camera.png')
is_detect = False

q_unicode = ord('q')
b_unicode = ord('b')

while(cap.isOpened()):
	ret, frame = cap.read()

	if is_detect == True:
		crop_img = frame[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]

		hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
		msk = cv2.inRange(hsv, np.array([110, 0, 85]), np.array([180, 58, 255]))
		filtered = cv2.bitwise_and(crop_img, crop_img, mask= msk)

		kernel = np.ones((2, 2), np.uint8)
		kernel_erode = np.ones((1, 1), np.uint8) 
		img_erosion = cv2.erode(filtered, kernel_erode, iterations=1) 

		grayF = cv2.cvtColor(img_erosion, cv2.COLOR_BGR2GRAY)
		blurF = cv2.GaussianBlur(grayF, (3,3), 0)
		threshF = cv2.threshold(blurF, 0, 255, cv2.THRESH_BINARY)[1]

		template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
		cv2.imshow('gray_image', threshF)

		best_angle = 0
		best_match = -1
		best_template = None
		
		for angle in range(0, 360, 1):
			template_height, template_width = template_gray.shape
			rotation_matrix = cv2.getRotationMatrix2D((template_width / 2, template_height / 2), angle, 1)
			rotated_template = cv2.warpAffine(template_gray, rotation_matrix, (template_width, template_height))
			cv2.imshow('rotated_template', rotated_template)

			result = cv2.matchTemplate(threshF, rotated_template, cv2.TM_CCOEFF_NORMED)

			_, max_val, _, _ = cv2.minMaxLoc(result)
			if max_val > best_match:
				best_match = max_val
				best_angle = angle
				best_template = rotated_template

	
		cv2.imshow('rotated_template', best_template)
		print(f"Best angle: {best_angle}")
		print(f"Best match: {best_match}")
		cv2.line(frame, roi_center, rotarGrad(roi_center[0], roi_center[1], best_angle + 90, 50), (0, 0, 255), 2)


	cv2.circle(frame, roi_center, 3, (0, 255, 0), -1)
	cv2.imshow('Frame', frame)
	
	key = cv2.waitKey(25)
	# Press q to exit
	if key == q_unicode:
		break
	# Press b to start test
	if key == b_unicode:
		is_detect = not is_detect


cv2.destroyAllWindows()

