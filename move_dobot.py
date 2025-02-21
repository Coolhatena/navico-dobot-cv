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
send_command("EnableRobot()", port=29999)

# Define the positions
initial_pose = (157, -123, 213, 245)
start_point = (157, -123, 213, 245)
engaged_point = (157, -123, 184, 245)
left_point = (157, -143, 184, 245)
right_point = (157, -103, 184, 245)

# Define the options
speed_fast = 5
acc_fast = 5
speed_slow = 1
acc_slow = 1

# Send commands to move the robot
send_command(f"MovJ({start_point[0]},{start_point[1]},{start_point[2]},{start_point[3]},SpeedJ={speed_slow},AccJ={acc_slow})")
send_command(f"MovJ({engaged_point[0]},{engaged_point[1]},{engaged_point[2]},{engaged_point[3]},SpeedJ={speed_slow},AccJ={acc_slow})")
send_command(f"MovJ({left_point[0]},{left_point[1]},{left_point[2]},{left_point[3]},SpeedJ={speed_fast},AccJ={acc_fast})")
send_command(f"MovJ({engaged_point[0]},{engaged_point[1]},{engaged_point[2]},{engaged_point[3]},SpeedJ={speed_fast},AccJ={acc_fast})")
send_command(f"MovJ({right_point[0]},{right_point[1]},{right_point[2]},{right_point[3]},SpeedJ={speed_fast},AccJ={acc_fast})")
send_command(f"MovJ({engaged_point[0]},{engaged_point[1]},{engaged_point[2]},{engaged_point[3]},SpeedJ={speed_fast},AccJ={acc_fast})")
send_command(f"MovJ({start_point[0]},{start_point[1]},{start_point[2]},{start_point[3]},SpeedJ={speed_fast},AccJ={acc_fast})")

