import time

from tcp_dobot import send_command
from move_dobot_to import moveDobotToRelative

def dummy_test():
	# Define the options
	speed_slow = 2
	acc_slow = 2

	test_movement = 9

	moveDobotToRelative((0, 0, -test_movement, 0), speed_slow, acc_slow)
	moveDobotToRelative((0, 0, test_movement, 0), speed_slow, acc_slow)
	

if __name__ == "__main__":
	dummy_test()