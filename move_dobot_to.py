from tcp_dobot import send_command
from get_dobot_position import get_dobot_position


# Position need to be compared this way because there may be a slight difference 
# in the position values when the dobot is moving
def _compare_positions(position1, position2, max_difference=0.5):
	return all(abs(x - y) < max_difference for x, y in zip(position1, position2))


def moveDobotTo(point, speed=1, acc=1, port=30003):
	x, y, z, r = point
	command = "MovJ({}, {}, {}, {}, SpeedJ={}, AccJ={})".format(x, y, z, r, speed, acc)
	send_command(command, port)

	is_position_reached = _compare_positions(point, get_dobot_position())
	while not is_position_reached:
		is_position_reached = _compare_positions(point, get_dobot_position())


def moveDobotToRelative(point, speed=1, acc=1, port=30003):
	original_position = get_dobot_position()
	x, y, z, r = point
	new_position = (original_position[0] + x, original_position[1] + y, original_position[2] + z, original_position[3] + r)

	command = "RelMovJUser({}, {}, {}, {}, SpeedJ={}, AccJ={})".format(x, y, z, r, speed, acc)
	send_command(command, port)
	
	
	is_position_reached = _compare_positions(new_position, get_dobot_position()) 
	while not is_position_reached:
		is_position_reached = _compare_positions(new_position, get_dobot_position())
		print(f"Current position: {get_dobot_position()}")
		print(f"Should be: {new_position}")

	print(f'MOVEMENT TO {point} DONE\n\n') 


if __name__ == "__main__":
	send_command("ClearError()", port=29999)
	send_command("EnableRobot()", port=29999)

	# moveDobotTo((195, -92, 202, -124), 5, 5)
	# moveDobotTo((208, -92, 202, -124), 5, 5)

	moveDobotToRelative((0, 0, 0,2), 2, 2)
	# moveDobotToRelative((0, -30, 0, 0), 2, 2)

	send_command("disableRobot()", port=29999)