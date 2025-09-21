import cv2
import numpy as np
import math

# video_path = 'rect.mp4'
# cam = cv2.VideoCapture(video_path)

cam_index = 2
cam = cv2.VideoCapture(cam_index)

grey_filter = [np.array([12, 0, 106]), np.array([72, 75, 211])]
# blue_filter = [np.array([83, 150, 89]), np.array([180, 239, 255])]
blue_filter = [np.array([105, 50, 75]), np.array([119, 141, 205])]

q_unicode = ord('q')

is_pause = False

# Get euclidean distance between two points
def get_distance_between_points(p1, p2):
	dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
	return dis


def rotate_n_deg(originx, originy, angle, rad):
	return (round(originx+rad*math.cos(-math.radians(angle))), round(originy+rad*math.sin(-math.radians(angle))))


def hsv_color_filter(image, min_hsv, max_hsv):
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	msk = cv2.inRange(hsv, min_hsv, max_hsv)
	filtered = cv2.bitwise_and(image, image, mask= msk)
	filtered_grey = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
	(thresh, image_bw) = cv2.threshold(filtered_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
	
	return image_bw


correction_x = 95
correction_y = 300
last_point = (95, 60)

while True:
	if not is_pause:
		_, frame = cam.read()
	else:
		cv2.imshow('Frame', frame)
		key = cv2.waitKey(30)
		if key == ord('p'):
			is_pause = not is_pause
		continue

	# img_grey = hsv_color_filter(frame[0:170 , 260:390], grey_filter[0], grey_filter[1])
	img_blue = hsv_color_filter(frame[300:600 , 95:517], blue_filter[0], blue_filter[1])

	# # Creating kernel 
	# kernel = np.ones((5, 5), np.uint8) 
	
	# # Using cv2.erode() method  
	# img_grey = cv2.erode(img_grey, kernel, iterations=1)
	# img_grey = cv2.dilate(img_grey, kernel, iterations=3) 

	contours, _ = cv2.findContours(img_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	if contours:
		largest_contour = max(contours, key=cv2.contourArea)
		rect = cv2.minAreaRect(largest_contour)

		box = cv2.boxPoints(rect)
		box = np.int0(box)

		center_x = np.mean(box[:, 0])
		center_y = np.mean(box[:, 1])
		center = (int(center_x), int(center_y))

		distances = [
			(np.linalg.norm(box[0] - box[1]), (box[0] + box[1]) // 2),
			(np.linalg.norm(box[1] - box[2]), (box[1] + box[2]) // 2),
			(np.linalg.norm(box[2] - box[3]), (box[2] + box[3]) // 2),
			(np.linalg.norm(box[3] - box[0]), (box[3] + box[0]) // 2)
		]

		distances.sort(key=lambda x: x[0])
		shortest_face_centers = [distances[0][1], distances[1][1]]

		side1, side2 = shortest_face_centers

		distance1 = get_distance_between_points(side1, last_point)
		distance2 = get_distance_between_points(side2, last_point)

		if distance1 < distance2:
			last_point = side1
			selected_point = side1
		else:
			last_point = side2
			selected_point = side2

		# DEBUG: Draw rectangle
		corrected_box = []
		for pt in box:
			corrected_box.append([int(pt[0]+correction_x), int(pt[1]+correction_y)])
		corrected_box = np.array(corrected_box)
		cv2.drawContours(frame, [corrected_box], 0, (0, 255, 0), 2)

		corrected_selected_point = (selected_point[0] + correction_x, selected_point[1] + correction_y)
		corrected_fixed_center = (center[0] + correction_x, center[1] + correction_y)
		
		angle_rad = math.atan2(selected_point[1] - center[1], selected_point[0] - center[0])
		angle = abs(math.degrees(angle_rad))

		print(angle)
		line_color = (0, 255, 0) if abs(angle - 90) > 3 else (0, 0, 255)
		cv2.line(frame, corrected_fixed_center, rotate_n_deg(center[0] + correction_x, center[1] + correction_y, angle, 150), line_color, 2)
		

		# cv2.imshow('Frame grey', img_grey)
		cv2.imshow('Frame blue', img_blue)
		frame_center_x = 330 - 90 # 330 is the real center, the substract is a compensation
		cv2.line(frame, (frame_center_x, 2), (frame_center_x, 170), (0, 255, 0), 2)

	cv2.imshow('Frame', frame)

	key = cv2.waitKey(30)
	if key == ord('p'):
		is_pause = not is_pause

	if key == q_unicode: # If 'q' is pressed, close program (Its case sensitive)
		break

cam.release()
cv2.destroyAllWindows()