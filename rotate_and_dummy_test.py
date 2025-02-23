from dummy_test import dummy_test
from rotate_tool import rotate_tool
from tcp_dobot import send_command

import time

# Go back to reference position
# send_command('MovJ(172.87, -20.20, 201.99, -101.57, SpeedJ=1, AccJ=1)')


rotate_tool()

time.sleep(4)

dummy_test()

time.sleep(4)

rotate_tool()