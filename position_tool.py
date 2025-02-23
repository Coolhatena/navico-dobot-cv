import cv2
import numpy as np
import time
import math


from send_command import send_command

def click_event(event, x, y, flags, params):
   if event == cv2.EVENT_LBUTTONDOWN:
      print(f'({x},{y})')


# create a window
cv2.namedWindow('Frame')

# bind the callback function to window
cv2.setMouseCallback('Frame', click_event)

camera_index = 2
cam = cv2.VideoCapture(camera_index)

while not cam.isOpened():
	cam = cv2.VideoCapture(camera_index)
	print("Waiting for camera...")
	time.sleep(0.05)

q_unicode = ord('q')


area = ((230,310), (350, 440))

def calculate_offset(limit_1, limit_2, coord_value):
	offset = 0
	if coord_value - limit_1 < 0:
		offset = coord_value - limit_1

	if coord_value - limit_2 > 0:
		offset = coord_value - limit_2

	return offset


def in_center_area(point):
	center_area = ((265, 349), (312, 375))
	offset_x = calculate_offset(center_area[0][0], center_area[1][0], point[0])
	offset_y = calculate_offset(center_area[0][1], center_area[1][1], point[1])
	# print(f'Offset in x: {offset_x}')
	# print(f'Offset in y: {offset_y}')
	# print('\n')
	is_in_center = (offset_x == 0) and (offset_y == 0)
	return [is_in_center, [offset_x, offset_y]]



send_command("ClearError()", port=29999)
send_command("EnableRobot()", port=29999)

start = time.time()

detection = True

while True:
	# Calculate interval between commands
	elapsed_time = time.time() - start
	# print(elapsed_time)

	_, frame = cam.read()

	if detection:
		crop = frame[area[0][1]:area[1][1], area[0][0]:area[1][0]]
		cv2.rectangle(frame, area[0], area[1], (255, 0 , 0), 2)

		hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
		msk = cv2.inRange(hsv, np.array([0, 0, 85]), np.array([28, 255, 255]))
		filtered = cv2.bitwise_and(crop,crop, mask= msk)
		filtered_grey = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)

		kernel = np.ones((5, 5), np.uint8) 
		filtered_grey = cv2.dilate(filtered_grey, kernel, iterations=2) 
		threshF = cv2.threshold(filtered_grey, 5, 255, cv2.THRESH_BINARY)[1]
		contours, _ = cv2.findContours(threshF, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		
		cv2.imshow('filtered', filtered_grey)

		if contours:
			c = max(contours, key = cv2.contourArea)
			M = cv2.moments(c)
			if not (M['m00'] != 0):
				continue

			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])

			center = (cx + area[0][0], cy + area[0][1])
			is_in_center_area, offsets = in_center_area(center)
			center_color = (0, 255, 0) if is_in_center_area else (0, 0, 255)


			cv2.circle(frame, center, 3, center_color, -1)

			# Approximate the contour to a polygon
			epsilon = 0.01 * cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, epsilon, True)

			corrected_approx = []
			for point in approx:
				new_point = [ int(point[0][0] + area[0][0]), int(point[0][1] + area[0][1]) ]
				corrected_approx.append(new_point)

			corrected_approx = np.array(corrected_approx)
			# Draw the approximated polygon
			cv2.drawContours(frame, [corrected_approx], 0, (0, 255, 0), 2)

			if elapsed_time > 2:
				dec_places = 2
				print(offsets)
				print(f'Offset in x: {offsets[0]}')
				print(f'Offset in y: {offsets[1]}')
				movement_x = round(offsets[0] / 10, dec_places)
				movement_y = round(offsets[1] / 10, dec_places)

				print(f'The robot has to move {movement_x} in x and {movement_y} in y')

				if movement_x or movement_y:
				# if False:
					# Define the options
					print('MOVING')
					speed_slow = 1
					acc_slow = 1
					send_command(f"RelMovJUser({movement_y}, {movement_x}, 0, 0, SpeedJ={speed_slow},AccJ={acc_slow})")

				print('\n')
				start = time.time()


	height_frame, width_frame, _ = frame.shape
	cv2.circle(frame, ( width_frame//2, height_frame//2 ), 3, (0, 255, 0), -1)
	cv2.imshow('Frame', frame)

	key = cv2.waitKey(1)
	if key == q_unicode: # If 'q' is pressed, close program (Its case sensitive)
		break

	if key == ord('b'):
		detection = not detection

cam.release()
cv2.destroyAllWindows()
