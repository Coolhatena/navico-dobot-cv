import time

from tcp_dobot import send_command
from prod_position_tool import position_tool_and_test
from get_dobot_position import get_dobot_position
from move_dobot_to import moveDobotTo, moveDobotToRelative


def test_row(row):
	speed = 5
	acc = 5

	moveDobotTo(row, speed, acc)

	terminal_index = 0

	while(terminal_index < 3):
		original_position = get_dobot_position()
		position_tool_and_test()

		moveDobotTo(original_position, speed, acc)
		moveDobotToRelative((0, 12, 0, 0), speed, acc)
		terminal_index += 1
		print(f"Terminal index: {terminal_index}")
	

