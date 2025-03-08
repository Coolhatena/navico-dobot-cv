from tcp_dobot import send_command_with_response

def get_dobot_position():
	response = send_command_with_response(f"GetPose()")
	start = response.index("{") + 1
	end = response.index("}")
	splitted_data = response[start:end].split(',')
	position = (float(splitted_data[0]), float(splitted_data[1]), float(splitted_data[2]), float(splitted_data[3]))

	return position


if __name__ == "__main__":
	print(get_dobot_position())