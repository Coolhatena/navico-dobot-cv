import os
import json
from tcp_dobot import send_command
from prod_test_row import test_row

# TODO: Add integration for torquemeter detection

file_path = "config.json"
with open(file_path, "r") as f:
	data = json.load(f)
	initial_coords = (data["start"]['x'], data["start"]['y'], data["start"]['z'], data["start"]['r'])
	print(data["start"])

# Clear errors and enable the robot
send_command("ClearError()", port=29999)
send_command("EnableRobot()", port=29999)

# Define the positions
# (X, Y, Z, R)

# row1 = (195, -92, 202, -124)
row1 = initial_coords
row2 = (208, -92, 202, -124)
row3 = (219, -92, 202, -124)


# Define the options
speed_fast = 5
acc_fast = 5
speed_slow = 1
acc_slow = 1

test_row(row1)
# Send commands to move the robot
# send_command(f"MovJ({row1[0]},{row1[1]},{row1[2]},{row1[3]},SpeedJ={speed_fast},AccJ={acc_slow})")
# send_command(f"MovJ({row2[0]},{row2[1]},{row2[2]},{row2[3]},SpeedJ={speed_fast},AccJ={acc_slow})")
# send_command(f"MovJ({row3[0]},{row3[1]},{row3[2]},{row3[3]},SpeedJ={speed_fast},AccJ={acc_slow})")

