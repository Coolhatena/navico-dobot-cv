from tcp_dobot import send_command
from get_dobot_position import get_dobot_position
from move_dobot_to import moveDobotToRelative

def rotate_tool():
	speed_slow = 1
	acc_slow = 1

	positions = get_dobot_position()

	tool_angle = positions[3]

	rotation = -180 if tool_angle > -200 else 180
	moveDobotToRelative((0, 0, 0, rotation), speed_slow, acc_slow)
	print(f"TOOL ROTATED\n\n")

if __name__ == "__main__":
	rotate_tool()