from tcp_dobot import send_command_with_response


def setArmOrientation(y_coord):
	if (y_coord < 0):
		send_command_with_response("SetArmOrientation(0)")
	else:
		send_command_with_response("SetArmOrientation(1)")