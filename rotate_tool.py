from tcp_dobot import send_command
from get_dobot_position import get_dobot_position

def rotate_tool():
	speed_slow = 1
	acc_slow = 1

	positions = get_dobot_position()

	tool_angle = positions[3]

	rotation = -180 if tool_angle > -200 else 180
	send_command(f"RelMovJUser(0, 0, 0, {rotation}, SpeedJ={speed_slow},AccJ={acc_slow})")

if __name__ == "__main__":
	rotate_tool()