import math
from move_dobot_to import moveDobotTo
from get_dobot_position import get_dobot_position

def recorrer_limite_circular_xy():
	speed = 25
	acc = 25
	x_cur, y_cur, z_cur, r_cur = get_dobot_position()

	moveDobotTo((150, 50, z_cur, r_cur), speed, acc)
	
	moveDobotTo((150, 250, z_cur, r_cur), speed, acc)

	moveDobotTo((300, 250, z_cur, r_cur), speed, acc)

	moveDobotTo((300, 50, z_cur, r_cur), speed, acc)

	moveDobotTo((300, -50, z_cur, r_cur), speed, acc)

	moveDobotTo((300, -250, z_cur, r_cur), speed, acc)

	moveDobotTo((150, -250, z_cur, r_cur), speed, acc)

	moveDobotTo((150, -50, z_cur, r_cur), speed, acc)

	moveDobotTo((150, 50, z_cur, r_cur), speed, acc)


if __name__ == "__main__":
	recorrer_limite_circular_xy()
