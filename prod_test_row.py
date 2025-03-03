import time

from tcp_dobot import send_command
from prod_position_tool import position_tool_and_test
from get_dobot_position import get_dobot_position


def test_row(row):
	speed = 5
	acc = 5

	send_command(f"MovJ({row[0]},{row[1]},{row[2]},{row[3]},SpeedJ={speed},AccJ={acc})")

	terminal_index = 0

	while(terminal_index < 3):
		time.sleep(1)
		original_position = get_dobot_position()
		time.sleep(1)
		position_tool_and_test()
		time.sleep(1)
		send_command(f"MovJ({original_position[0]},{original_position[1]},{original_position[2]},{original_position[3]},SpeedJ={speed},AccJ={acc})")
		time.sleep(1)
		send_command(f"RelMovJUser(0, 12, 0, 0, SpeedJ=2,AccJ=2)")
		terminal_index += 1
		print(f"Terminal index: {terminal_index}")
	

