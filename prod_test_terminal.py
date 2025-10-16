from move_dobot_to import moveDobotToRelative

def prod_test_terminal(down_movement, side_movement, cv_worker):
	# Define the options
	speed_slow = 1
	acc_slow = 1

	cv_worker.initTerminal()

	# Move torquemeter down
	moveDobotToRelative((0, 0, -down_movement, 0), speed_slow, acc_slow)

	# # Move torquimeter to the sides
	# Right
	moveDobotToRelative((0, side_movement, 0, 0), speed_slow, acc_slow)
	cv_worker.saveTerminalState()
	moveDobotToRelative((0, -side_movement, 1, 0), speed_slow, acc_slow)

	# Pressure Relief
	moveDobotToRelative((0, 0, 3, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, 0, -3, 0), speed_slow, acc_slow)

	# Left
	moveDobotToRelative((0, -side_movement, -1, 0), speed_slow, acc_slow)
	cv_worker.saveTerminalState()
	moveDobotToRelative((0, side_movement, 0, 0), speed_slow, acc_slow)


	# # Move torquemeter up
	moveDobotToRelative((0, 0, down_movement, 0), speed_slow, acc_slow)