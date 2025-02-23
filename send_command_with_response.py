import socket

# Function to send a command to the robot
def send_command_with_response(command, port=30003):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect(('192.168.1.6', port))
		s.sendall(command.encode())
		response = s.recv(1024)
		response_string = response.decode()
		print('Received:', response_string)
		
		return response_string