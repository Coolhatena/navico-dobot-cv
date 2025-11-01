import serial


def switchRelay(turnOn = True):
	PORT = "/dev/ttyUSB0"
	BAUD = 9600

	cmds = {
		"ON_hex" : bytes([0xA0,0x01,0x01,0xA2]),
		"OFF_hex": bytes([0xA0,0x01,0x00,0xA1]),
	}

	state = "ON_hex" if turnOn else "OFF_hex"

	with serial.Serial(PORT, BAUD, timeout=0.2) as s:
		s.write(cmds[state])
