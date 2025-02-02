import socket

# Function to send a command to the robot
def send_command(command, port=30003):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('192.168.1.6', port))
        s.sendall(command.encode())
        response = s.recv(1024)
        print('Received:', response.decode())

# Clear errors and enable the robot
send_command("ClearError()", port=29999)
# Send command to disable robot
send_command("DisableRobot()", port=29999)
