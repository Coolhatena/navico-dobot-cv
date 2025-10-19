import serial, time

PORT = "/dev/ttyUSB0"
BAUD = 9600

cmds = {
    "ON_hex" : bytes([0xA0,0x01,0x01,0xA2]),
    "OFF_hex": bytes([0xA0,0x01,0x00,0xA1]),
}

with serial.Serial(PORT, BAUD, timeout=0.2) as s:
    s.write(cmds["ON_hex"])  
    time.sleep(1)
    s.write(cmds["OFF_hex"]) 
    time.sleep(1)
