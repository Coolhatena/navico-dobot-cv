import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os
import json
from tcp_dobot import send_command
from get_dobot_position import get_dobot_position
from move_dobot_to import moveDobotTo
from dummy_test import modular_full_dummy_test
from prod_test_row import modular_test_row_between

CONFIG_PATH = "config.json"

def load_config():
	if not os.path.exists(CONFIG_PATH):
		return {"rows": {}}
	with open(CONFIG_PATH, "r") as f:
		data = json.load(f) or {}
	if "rows" not in data or not isinstance(data["rows"], dict):
		data["rows"] = {}
	return data

def ensure_profile(data, profile_key):
	rows = data.setdefault("rows", {})
	if profile_key not in rows:
		rows[profile_key] = {"start": {}, "end": {}, "skips": ""}
	if "start" not in rows[profile_key]:
		rows[profile_key]["start"] = {}
	if "end" not in rows[profile_key]:
		rows[profile_key]["end"] = {}
	if "skips" not in rows[profile_key]:
		rows[profile_key]["skips"] = ""
	return data

def save_config(data):
	with open(CONFIG_PATH, "w") as f:
		json.dump(data, f, indent=4)

def _parse_skips(s, n):
	if not isinstance(s, str):
		return set()
	out = set()
	for part in s.split(","):
		part = part.strip()
		if not part:
			continue
		try:
			val = int(part)
			if 1 <= val <= n:
				out.add(val)
		except ValueError:
			pass
	return out

class ControlApp:
	def __init__(self, root):
		send_command("ClearError()", port=29999)
		send_command("DisableRobot()", port=29999)
		self.root = root
		self.root.title("Control de Dobot")

		self.root.rowconfigure(0, weight=1)
		self.root.columnconfigure(0, weight=1)

		self.nb = ttk.Notebook(self.root)
		self.nb.grid(row=0, column=0, sticky="nsew")
		page1 = tk.Frame(self.nb)
		page2 = tk.Frame(self.nb)
		self.nb.add(page1, text="Configuración")
		self.nb.add(page2, text="Prueba")

		page1.rowconfigure(0, weight=1)
		page1.columnconfigure(0, weight=1)
		container = tk.Frame(page1)
		container.grid(row=0, column=0)
		
		container.columnconfigure(0, weight=1)
		container.columnconfigure(1, weight=0)
		container.columnconfigure(2, weight=1)
		container.rowconfigure(0, weight=1)
		container.rowconfigure(1, weight=0)
		container.rowconfigure(2, weight=1)

		self.coords = {'x': 0, 'y': 0, 'z': 0, 'r': 0}
		self.step = 1.0
		self.velocity = tk.IntVar(value=5)
		self.acceleration = tk.IntVar(value=5)
		self.profile_var = tk.StringVar(value="1")

		left_frame = tk.Frame(container)
		left_frame.grid(row=1, column=0, sticky="n", padx=20, pady=20)

		self.down_movement_var = tk.DoubleVar(value=15.0)
		self.side_movement_var = tk.DoubleVar(value=25.0)
		self.terminals_var = tk.IntVar(value=16)
		self.skips_var = tk.StringVar(value="")

		tk.Label(left_frame, text="Movimiento hacia abajo:").pack(anchor="w")
		tk.Entry(left_frame, textvariable=self.down_movement_var, width=10).pack(pady=(0, 8))

		tk.Label(left_frame, text="Movimiento lateral:").pack(anchor="w")
		tk.Entry(left_frame, textvariable=self.side_movement_var, width=10).pack(pady=(0, 12))

		tk.Label(left_frame, text="Terminales:").pack(anchor="w")
		tk.Entry(left_frame, textvariable=self.terminals_var, width=10).pack(pady=(0, 12))

		tk.Button(left_frame, text="Guardar Movimientos/Terminales", command=self.save_motion_settings).pack(pady=(0, 12))

		tk.Label(left_frame, text="Skips:").pack(anchor="w")
		tk.Entry(left_frame, textvariable=self.skips_var, width=18).pack(pady=(0, 12))

		tk.Button(left_frame, text="Probar Terminal", command=self.test_terminal).pack(pady=5)
		tk.Button(left_frame, text="Probar Fila", command=self.test_row).pack(pady=5)

		tk.Label(left_frame, text="Fila:").pack(anchor="w")
		profile_select = ttk.Combobox(left_frame, textvariable=self.profile_var, values=["1", "2", "3"], state="readonly", width=6)
		profile_select.pack(pady=(0, 12))
		profile_select.bind("<<ComboboxSelected>>", self.on_profile_change)
		
		tk.Label(left_frame, text="Punto inicial").pack(anchor="w", pady=(10, 0))
		start_frame = tk.Frame(left_frame)
		start_frame.pack(pady=5, anchor="w")
		tk.Button(start_frame, text="Guardar", command=lambda: self.save_point("start")).pack(side=tk.LEFT, padx=2)
		tk.Button(start_frame, text="Ir", command=lambda: self.goto_point("start")).pack(side=tk.LEFT, padx=2)

		tk.Label(left_frame, text="Punto final").pack(anchor="w", pady=(10, 0))
		end_frame = tk.Frame(left_frame)
		end_frame.pack(pady=5, anchor="w")
		tk.Button(end_frame, text="Guardar", command=lambda: self.save_point("end")).pack(side=tk.LEFT, padx=2)
		tk.Button(end_frame, text="Ir", command=lambda: self.goto_point("end")).pack(side=tk.LEFT, padx=2)

		main_frame = tk.Frame(container)
		main_frame.grid(row=1, column=1, sticky="n", padx=20, pady=20)

		right_frame = tk.Frame(container)
		right_frame.grid(row=1, column=2, sticky="n", padx=20, pady=20)

		tk.Label(right_frame, text="Velocidad:", anchor="w").pack()
		tk.Entry(right_frame, textvariable=self.velocity, width=8).pack(pady=5)

		tk.Label(right_frame, text="Aceleración:", anchor="w").pack()
		tk.Entry(right_frame, textvariable=self.acceleration, width=8).pack(pady=5)

		tk.Button(right_frame, text="Guardar Vel/Acel", command=self.save_speed_settings).pack(pady=(0, 12))

		self.label = tk.Label(main_frame, text=self.get_coord_text(), font=("Arial", 14))
		self.label.pack(pady=10)

		frame1 = tk.Frame(main_frame)
		frame1.pack(pady=10)
		self.create_dpad(frame1, "+x", "-x", "+y", "-y", self.update_xy)

		frame2 = tk.Frame(main_frame)
		frame2.pack(pady=10)
		self.create_dpad(frame2, "+z", "-z", "+r", "-r", self.update_zr)

		step_frame = tk.Frame(main_frame)
		step_frame.pack(pady=10)
		tk.Label(step_frame, text="Step actual:").pack(side=tk.LEFT)

		for val in [0.1, 1, 5, 10]:
			tk.Button(step_frame, text=str(val), width=4, command=lambda v=val: self.set_step(v)).pack(side=tk.LEFT, padx=2)

		switch_frame = tk.Frame(main_frame)
		switch_frame.pack(pady=10)

		self.switch_var = tk.IntVar()
		self.status_label = tk.Label(switch_frame, text="Desactivado", bg="red", fg="white", width=12)

		self.switch = tk.Checkbutton(
			switch_frame,
			text="Modo",
			variable=self.switch_var,
			command=self.toggle_switch
		)
		self.switch.pack(side=tk.LEFT, padx=5)
		self.status_label.pack(side=tk.LEFT)

		page2.rowconfigure(0, weight=1)
		page2.columnconfigure(0, weight=1)
		prueba_frame = tk.Frame(page2)
		prueba_frame.grid(row=0, column=0)

		tk.Button(prueba_frame, text="Iniciar Prueba", command=lambda: self.complete_test()).pack(pady=10, padx=20)
		tk.Button(prueba_frame, text="Calcular Coordenadas").pack(pady=10, padx=20)

		self._load_skips_into_entry()
		self._load_settings_into_entries()

	def on_profile_change(self, _event=None):
		self._load_skips_into_entry()
		self._load_settings_into_entries()

	def _load_skips_into_entry(self):
		data = load_config()
		rows = data.get("rows", {})
		profile = self.profile_var.get()
		val = ""
		if profile in rows:
			val = rows[profile].get("skips", "")
		self.skips_var.set(val if isinstance(val, str) else "")

	def _load_settings_into_entries(self):
		data = load_config()
		if isinstance(data.get("down_movement"), (int, float)):
			self.down_movement_var.set(data["down_movement"])
		if isinstance(data.get("side_movement"), (int, float)):
			self.side_movement_var.set(data["side_movement"])
		if isinstance(data.get("terminals"), int):
			self.terminals_var.set(data["terminals"])
		if isinstance(data.get("velocity"), int):
			self.velocity.set(data["velocity"])
		if isinstance(data.get("acceleration"), int):
			self.acceleration.set(data["acceleration"])

	def _save_skips_from_entry(self):
		profile = self.profile_var.get()
		data = load_config()
		data = ensure_profile(data, profile)
		data["rows"][profile]["skips"] = self.skips_var.get()
		save_config(data)

	def save_motion_settings(self):
		try:
			down = float(self.down_movement_var.get())
			side = float(self.side_movement_var.get())
			n = int(self.terminals_var.get())
		except (ValueError, tk.TclError):
			messagebox.showerror("Error", "Ingresa valores válidos para movimientos y terminales.")
			return
		data = load_config()
		data["down_movement"] = down
		data["side_movement"] = side
		data["terminals"] = n
		save_config(data)

	def save_speed_settings(self):
		try:
			vel = int(self.velocity.get())
			acc = int(self.acceleration.get())
		except (ValueError, tk.TclError):
			messagebox.showerror("Error", "Ingresa valores válidos para velocidad y aceleración.")
			return
		data = load_config()
		data["velocity"] = vel
		data["acceleration"] = acc
		save_config(data)

	def save_point(self, point_type):
		profile = self.profile_var.get()
		data = load_config()
		data = ensure_profile(data, profile)
		data["rows"][profile][point_type] = {
			"x": self.coords['x'],
			"y": self.coords['y'],
			"z": self.coords['z'],
			"r": self.coords['r']
		}
		save_config(data)

	def goto_point(self, point_type):
		profile = self.profile_var.get()
		data = load_config()
		rows = data.get("rows", {})
		if profile not in rows or point_type not in rows[profile] or not rows[profile][point_type]:
			messagebox.showerror("Error", f"No hay punto '{point_type}' guardado para la fila {profile}.")
			return
		pt = rows[profile][point_type]
		try:
			self.coords['x'] = float(pt['x'])
			self.coords['y'] = float(pt['y'])
			self.coords['z'] = float(pt['z'])
			self.coords['r'] = float(pt['r'])
		except (KeyError, ValueError, TypeError):
			messagebox.showerror("Error", f"Datos inválidos en '{point_type}' de la fila {profile}.")
			return
		self.update_label()
		self.moveToCoords()

	def toggle_switch(self):
		if self.switch_var.get():
			self.status_label.config(text="Activado", bg="green")
			send_command("ClearError()", port=29999)
			send_command("EnableRobot()", port=29999)
			position = get_dobot_position()
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
			f"r={round(self.coords['r'], 3)}   | Step actual: {self.step} | Fila: {self.profile_var.get()}"
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
		moveDobotTo(
			[self.coords['x'], self.coords['y'], self.coords['z'], self.coords['r']],
			self.velocity.get(),
			self.acceleration.get()
		)

	def create_dpad(self, frame, up, down, left, right, callback):
		tk.Button(frame, text=up, width=8, command=lambda: callback(up)).grid(row=0, column=1)
		tk.Button(frame, text=left, width=8, command=lambda: callback(left)).grid(row=1, column=0)
		tk.Button(frame, text=right, width=8, command=lambda: callback(right)).grid(row=1, column=2)
		tk.Button(frame, text=down, width=8, command=lambda: callback(down)).grid(row=2, column=1)

	def test_terminal(self):
		try:
			down = float(self.down_movement_var.get())
			side = float(self.side_movement_var.get())
		except (ValueError, tk.TclError):
			messagebox.showerror("Error", "Ingresa valores numéricos válidos para abajo y lateral.")
			return
		modular_full_dummy_test(down, side)

	def test_row(self):
		self._save_skips_from_entry()

		profile = self.profile_var.get()
		data = load_config()
		rows = data.get("rows", {})
		if profile not in rows:
			messagebox.showerror("Error", f"No hay datos para la fila {profile}.")
			return
		if "start" not in rows[profile] or not rows[profile]["start"]:
			messagebox.showerror("Error", f"No hay punto inicial guardado para la fila {profile}.")
			return
		if "end" not in rows[profile] or not rows[profile]["end"]:
			messagebox.showerror("Error", f"No hay punto final guardado para la fila {profile}.")
			return

		start = rows[profile]["start"]
		end = rows[profile]["end"]

		start_coords = (start.get('x', 0), start.get('y', 0), start.get('z', 0), start.get('r', 0))
		end_coords   = (end.get('x', 0),   end.get('y', 0),   end.get('z', 0),   end.get('r', 0))
		try:
			down = float(data.get("down_movement", self.down_movement_var.get()))
			side = float(data.get("side_movement", self.side_movement_var.get()))
			n = int(data.get("terminals", self.terminals_var.get()))
			skips_str = rows[profile].get("skips", "")
			speed = int(data.get("velocity", self.velocity.get()))
			acc = int(data.get("acceleration", self.acceleration.get()))
		except (ValueError, tk.TclError):
			messagebox.showerror("Error", "Ingresa valores válidos para abajo, lateral y terminales.")
			return
		if n < 1:
			messagebox.showerror("Error", "Terminales debe ser >= 1.")
			return

		skips = _parse_skips(skips_str, n)
		modular_test_row_between(
			start_coords,
			end_coords,
			n,
			down_movement=down,
			side_movement=side,
			speed=speed,
			acc=acc,
			skips=skips
		)

	def complete_test(self):
		data = load_config()
		print(data)

if __name__ == "__main__":
	root = tk.Tk()
	root.attributes("-zoomed", True)
	root.bind("<F11>", lambda e: root.attributes("-fullscreen", not root.attributes("-fullscreen")))
	root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

	app = ControlApp(root)
	root.mainloop()
