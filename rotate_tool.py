from send_command import send_command
from send_command_with_response import send_command_with_response


speed_slow = 1
acc_slow = 1

response = send_command_with_response(f"GetPose()")
start = response.index("{") + 1
end = response.index("}")
positions = response[start:end].split(',')

tool_angle = float(positions[3])

rotation = -180 if tool_angle > -200 else 180
send_command(f"RelMovJUser(0, 0, 0, {rotation}, SpeedJ={speed_slow},AccJ={acc_slow})")