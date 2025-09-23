from prod_position_tool import position_tool_and_test
from dummy_test import modular_full_dummy_test
from get_dobot_position import get_dobot_position
from move_dobot_to import moveDobotTo, moveDobotToRelative


def test_row(row):
	speed = 5
	acc = 5

	moveDobotTo(row, speed, acc)

	terminal_index = 0

	while(terminal_index < 15):
		original_position = get_dobot_position()
		position_tool_and_test()

		moveDobotTo(original_position, speed, acc)
		moveDobotToRelative((0, 12, 0, 0), speed, acc)
		terminal_index += 1
		print(f"Terminal index: {terminal_index}")


def modular_test_row(row, down_movement, side_movement):
	speed = 5
	acc = 5

	moveDobotTo(row, speed, acc)

	terminal_index = 0

	while(terminal_index < 3):
		original_position = get_dobot_position()
		modular_full_dummy_test(down_movement, side_movement)

		moveDobotTo(original_position, speed, acc)
		moveDobotToRelative((0, 11.9, 0, 0), speed, acc)
		terminal_index += 1
		print(f"Terminal index: {terminal_index}")
	

def modular_test_row_between(start_pt, end_pt, n, down_movement, side_movement, speed=5, acc=5, skips=None):
	# start_pt/end_pt: (x, y, z, r)
	# n: número de terminales (>=1)
	# skips: conjunto/lista de índices 1-basados que se deben omitir
	if n < 1:
		raise ValueError("n debe ser >= 1")

	if skips is None:
		skips = set()
	else:
		skips = set(skips)

	def lerp(a, b, t):
		return a + (b - a) * t

	def point_at(t):
		return (
			lerp(float(start_pt[0]), float(end_pt[0]), t),
			lerp(float(start_pt[1]), float(end_pt[1]), t),
			lerp(float(start_pt[2]), float(end_pt[2]), t),
			lerp(float(start_pt[3]), float(end_pt[3]), t),
		)

	# caso n == 1: solo inicio
	ts = [0.0] if n == 1 else [i / (n - 1) for i in range(n)]

	for idx, t in enumerate(ts, start=1):
		if idx in skips:
			print(f"Skip terminal {idx}/{n}")
			continue

		target = point_at(t)
		moveDobotTo(target, speed, acc)

		original_position = get_dobot_position()
		modular_full_dummy_test(down_movement, side_movement)
		moveDobotTo(original_position, speed, acc)

		print(f"Terminal index: {idx}/{n}")


