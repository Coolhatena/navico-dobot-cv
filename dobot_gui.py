import tkinter as tk
import os
import json
from tcp_dobot import send_command
from get_dobot_position import get_dobot_position
from move_dobot_to import moveDobotTo

class ControlApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Coordinate Control")

		# Coordinates and initial step
		self.coords = {'x': 0, 'y': 0, 'z': 0, 'r': 0}
		self.step = 1.0

		# Create left-side frame for save buttons
		left_frame = tk.Frame(root)
		left_frame.pack(side=tk.LEFT, padx=10, pady=10)

		tk.Button(left_frame, text="Save Start Point", command=lambda: self.save_point("start")).pack(pady=5)
		tk.Button(left_frame, text="Save End Point", command=lambda: self.save_point("end")).pack(pady=5)

		# Main UI frame
		main_frame = tk.Frame(root)
		main_frame.pack(side=tk.LEFT, padx=20)

		# Right-side frame for velocity and acceleration
		self.velocity = tk.IntVar(value=5)
		self.acceleration = tk.IntVar(value=5)

		right_frame = tk.Frame(root)
		right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

		tk.Label(right_frame, text="Velocidad:", anchor="w").pack()
		tk.Entry(right_frame, textvariable=self.velocity, width=8).pack(pady=5)

		tk.Label(right_frame, text="Aceleración:", anchor="w").pack()
		tk.Entry(right_frame, textvariable=self.acceleration, width=8).pack(pady=5)


		self.label = tk.Label(main_frame, text=self.get_coord_text(), font=("Arial", 14))
		self.label.pack(pady=10)

		# Group 1: X and Y controls
		frame1 = tk.Frame(main_frame)
		frame1.pack(pady=10)
		self.create_dpad(frame1, "+x", "-x", "+y", "-y", self.update_xy)

		# Group 2: Z and R controls
		frame2 = tk.Frame(main_frame)
		frame2.pack(pady=10)
		self.create_dpad(frame2, "+z", "-z", "+r", "-r", self.update_zr)

		# Step size selector
		step_frame = tk.Frame(main_frame)
		step_frame.pack(pady=10)
		tk.Label(step_frame, text="Current step:").pack(side=tk.LEFT)

		for val in [0.1, 1, 5, 10]:
			tk.Button(step_frame, text=str(val), width=4, command=lambda v=val: self.set_step(v)).pack(side=tk.LEFT, padx=2)

		# Robot mode switch
		switch_frame = tk.Frame(main_frame)
		switch_frame.pack(pady=10)

		self.switch_var = tk.IntVar()
		self.status_label = tk.Label(switch_frame, text="Disabled", bg="red", fg="white", width=12)

		self.switch = tk.Checkbutton(
			switch_frame,
			text="Mode",
			variable=self.switch_var,
			command=self.toggle_switch
		)
		self.switch.pack(side=tk.LEFT, padx=5)
		self.status_label.pack(side=tk.LEFT)

	def save_point(self, point_type):
		file_path = "config.json"
		if not os.path.exists(file_path):
			data = {"start": {}, "end": {}}
		else:
			with open(file_path, "r") as f:
				data = json.load(f)

		# Save current coordinates to selected point
		data[point_type] = {
			"x": self.coords['x'],
			"y": self.coords['y'],
			"z": self.coords['z'],
			"r": self.coords['r']
		}

		with open(file_path, "w") as f:
			json.dump(data, f, indent=4)

		print(f"{point_type.capitalize()} point saved: {data[point_type]}")


	def toggle_switch(self):
		if self.switch_var.get():
			self.status_label.config(text="Activado", bg="green")
			send_command("ClearError()", port=29999)
			send_command("EnableRobot()", port=29999)
			position = get_dobot_position()
			print(position)
			self.coords['x'] = position[0]
			self.coords['y'] = position[1]
			self.coords['z'] = position[2]
			self.coords['r'] = position[3]
			self.update_label()
			
		else:
			self.status_label.config(text="Desactivado", bg="red")
			send_command("ClearError()", port=29999)
			send_command("DisableRobot()", port=29999)


	def set_step(self, value):
		self.step = float(value)
		self.update_label()


	def get_coord_text(self):
		return (
			f"Coordenadas actuales: x={round(self.coords['x'], 3)}  "
			f"y={round(self.coords['y'], 3)}  "
			f"z={round(self.coords['z'], 3)}  "
			f"r={round(self.coords['r'], 3)}   | Step actual: {self.step}"
		)


	def update_label(self):
		self.label.config(text=self.get_coord_text())


	def update_xy(self, direction):
		if direction == "+x":
			self.coords['x'] = round(self.coords['x'] + self.step, 3)
		elif direction == "-x":
			self.coords['x'] = round(self.coords['x'] - self.step, 3)
		elif direction == "+y":
			self.coords['y'] = round(self.coords['y'] + self.step, 3)
		elif direction == "-y":
			self.coords['y'] = round(self.coords['y'] - self.step, 3)
			
		self.moveToCoords()
		self.update_label()


	def update_zr(self, direction):
		if direction == "+z":
			self.coords['z'] = round(self.coords['z'] + self.step, 3)
		elif direction == "-z":
			self.coords['z'] = round(self.coords['z'] - self.step, 3)
		elif direction == "+r":
			self.coords['r'] = round(self.coords['r'] + self.step, 3)
		elif direction == "-r":
			self.coords['r'] = round(self.coords['r'] - self.step, 3)
			
		self.moveToCoords()
		self.update_label()

	def moveToCoords(self):
		# print(type(self.velocity.get()))
		# print(type(self.acceleration.get()))
		moveDobotTo([self.coords['x'], self.coords['y'], self.coords['z'], self.coords['r']], self.velocity.get(), self.acceleration.get())


	def create_dpad(self, frame, up, down, left, right, callback):
		# Distribución de botones en forma de cruceta
		tk.Button(frame, text=up, width=8, command=lambda: callback(up)).grid(row=0, column=1)
		tk.Button(frame, text=left, width=8, command=lambda: callback(left)).grid(row=1, column=0)
		tk.Button(frame, text=right, width=8, command=lambda: callback(right)).grid(row=1, column=2)
		tk.Button(frame, text=down, width=8, command=lambda: callback(down)).grid(row=2, column=1)


if __name__ == "__main__":
	root = tk.Tk()
	app = ControlApp(root)
	root.mainloop()
