from tcp_dobot import send_command, send_command_with_response


def enable_dobot():
	send_command("ClearError()", port=29999)
	send_command("EnableRobot()", port=29999)

def disable_dobot():
	send_command("ClearError()", port=29999)
	send_command("DisableRobot()", port=29999)

def get_dobot_status():
	response = send_command_with_response("RobotMode()", port=29999)
	error, status_raw, command = response.split(',')
	status = int(status_raw.split('{')[1].split('}')[0])
	return status

def is_dobot_enabled():
	status = get_dobot_status()
	return status == 5 or status == 7 


if __name__ == "__main__":
	disable_dobot()
	print(is_dobot_enabled())