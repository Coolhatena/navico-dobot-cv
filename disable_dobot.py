from tcp_dobot import send_command

send_command("ClearError()", port=29999)
send_command("DisableRobot()", port=29999)
