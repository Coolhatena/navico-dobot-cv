from tcp_dobot import send_command

import time

def dummy_test():
	# Define the options
	speed_slow = 1
	acc_slow = 1

	test_movement = 10

	send_command(f"RelMovJUser(0, 0, -{test_movement}, 0, SpeedJ={speed_slow},AccJ={acc_slow})")
	time.sleep(1)
	send_command(f"RelMovJUser(0, 0, {test_movement}, 0, SpeedJ={speed_slow},AccJ={acc_slow})")

if __name__ == "__main__":
	dummy_test()