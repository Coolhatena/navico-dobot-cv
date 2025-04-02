from move_dobot_to import moveDobotToRelative

def dummy_test():
	# Define the options
	speed_slow = 2
	acc_slow = 2

	test_movement = 9

	moveDobotToRelative((0, 0, -test_movement, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, 0, test_movement, 0), speed_slow, acc_slow)
	

def full_dummy_test():
	# Define the options
	speed_slow = 2
	acc_slow = 2

	down_movement = 3
	side_movement = 30

	# Move torquemeter down
	moveDobotToRelative((0, 0, -down_movement, 0), speed_slow, acc_slow)

	# # Move torquimeter to the sides
	moveDobotToRelative((0, side_movement, 0, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, -side_movement, 0, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, -side_movement, 0, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, side_movement, 0, 0), speed_slow, acc_slow)


	# # Move torquemeter up
	moveDobotToRelative((0, 0, down_movement, 0), speed_slow, acc_slow)


if __name__ == "__main__":
	full_dummy_test()