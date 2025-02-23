import socket

from tcp_dobot import send_command

# Clear errors and enable the robot
send_command("ClearError()", port=29999)
# Send command to disable robot
send_command("DisableRobot()", port=29999)
