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
	speed_slow = 1
	acc_slow = 1

	down_movement = 12
	side_movement = 35

	# Move torquemeter down
	moveDobotToRelative((0, 0, -down_movement, 0), speed_slow, acc_slow)

	# # Move torquimeter to the sides
	moveDobotToRelative((0, side_movement, 0, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, -side_movement, 1, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, -side_movement, -1, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, side_movement, 0, 0), speed_slow, acc_slow)


	# # Move torquemeter up
	moveDobotToRelative((0, 0, down_movement, 0), speed_slow, acc_slow)


def modular_full_dummy_test(down_movement, side_movement):
	# Define the options
	speed_slow = 1
	acc_slow = 1

	# Move torquemeter down
	moveDobotToRelative((0, 0, -down_movement, 0), speed_slow, acc_slow)

	# # Move torquimeter to the sides
	# Right
	moveDobotToRelative((0, side_movement, 0, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, -side_movement, 1, 0), speed_slow, acc_slow)
	# Left
	moveDobotToRelative((0, -side_movement, -1, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, side_movement, 0, 0), speed_slow, acc_slow)


	# # Move torquemeter up
	moveDobotToRelative((0, 0, down_movement, 0), speed_slow, acc_slow)


if __name__ == "__main__":
	full_dummy_test()