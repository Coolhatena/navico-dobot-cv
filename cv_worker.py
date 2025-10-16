import cv2
import numpy as np
import math
import threading
import time
from collections import deque

class CVWorker:
	def __init__(
		self,
		cam_index=2,
		roi_rows=(150, 600),
		roi_cols=(90, 517),
		blue_lo=(15, 114, 0),
		blue_hi=(48, 255, 255),
		correction_x=90,
		correction_y=150,
		last_point=(95, 60),
		window=5,
		show=False,
		tol_deg=3.0,
	):
		self.cam_index = cam_index
		self.roi_rows = roi_rows
		self.roi_cols = roi_cols
		self.blue_lo = np.array(blue_lo, dtype=np.uint8)
		self.blue_hi = np.array(blue_hi, dtype=np.uint8)
		self.correction = (int(correction_x), int(correction_y))
		self.last_point = np.array(last_point, dtype=np.float32)
		self.buf = deque(maxlen=max(1, int(window)))
		self.lock = threading.Lock()
		self.running = False
		self.t = None
		self.cam = None
		self.show = bool(show)
		self.tol_deg = float(tol_deg)

		# Terminal tests
		self.terminalResults = []
		self.currentTerminal = None

	def start(self):
		if self.running:
			return
		self.cam = cv2.VideoCapture(self.cam_index)
		self.running = True
		self.t = threading.Thread(target=self._loop, daemon=True)
		self.t.start()

	def stop(self):
		self.running = False
		if self.t:
			self.t.join(timeout=1.0)
			self.t = None
		if self.cam:
			self.cam.release()
			self.cam = None
		if self.show:
			try:
				cv2.destroyAllWindows()
			except Exception:
				pass

	def latest(self):
		with self.lock:
			vals = [v for v in self.buf if v is not None]
		if not vals:
			return None
		vals.sort()
		return vals[len(vals)//2]

	def ok_90(self, tol=None):
		tol = self.tol_deg if tol is None else float(tol)
		a = self.latest()
		return (a is not None) and (abs(a - 90.0) <= tol), a
	
	def pass_condition(self, tol=None):
		tol = self.tol_deg if tol is None else float(tol)
		a = self.latest()
		return (a is None) or (abs(a - 90.0) > tol), a
	
	def initTerminal(self):
		self.terminalResults.append([])
		self.currentTerminal = 0 if self.currentTerminal == None else self.currentTerminal + 1

	def saveTerminalState(self):
		self.terminalResults[self.currentTerminal].append(self.pass_condition())

	def getTerminalResults(self):
		return self.terminalResults

	@staticmethod
	def _hsv_color_filter(image, lo, hi):
		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		msk = cv2.inRange(hsv, lo, hi)
		filt = cv2.bitwise_and(image, image, mask=msk)
		grey = cv2.cvtColor(filt, cv2.COLOR_BGR2GRAY)
		_, bw = cv2.threshold(grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
		return bw

	@staticmethod
	def _euclid(p1, p2):
		dx = float(p2[0] - p1[0])
		dy = float(p2[1] - p1[1])
		return math.hypot(dx, dy)

	@staticmethod
	def _rotate_n_deg(ox, oy, angle_deg, rad):
		r = float(rad)
		a = -math.radians(angle_deg)
		return (round(ox + r * math.cos(a)), round(oy + r * math.sin(a)))

	def _loop(self):
		r0, r1 = self.roi_rows
		c0, c1 = self.roi_cols
		cx_off, cy_off = self.correction

		while self.running:
			ok, frame = self.cam.read() if self.cam else (False, None)
			if not ok:
				time.sleep(0.01)
				continue

			roi = frame[r0:r1, c0:c1]
			img_blue = self._hsv_color_filter(roi, self.blue_lo, self.blue_hi)

			contours, _ = cv2.findContours(img_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			angle = None

			if contours:
				largest = max(contours, key=cv2.contourArea)
				rect = cv2.minAreaRect(largest)
				box = cv2.boxPoints(rect).astype(np.float32)

				cx = float(np.mean(box[:, 0]))
				cy = float(np.mean(box[:, 1]))

				edges = [
					(np.linalg.norm(box[0] - box[1]), (box[0] + box[1]) * 0.5),
					(np.linalg.norm(box[1] - box[2]), (box[1] + box[2]) * 0.5),
					(np.linalg.norm(box[2] - box[3]), (box[2] + box[3]) * 0.5),
					(np.linalg.norm(box[3] - box[0]), (box[3] + box[0]) * 0.5),
				]
				edges.sort(key=lambda x: x[0])
				side1, side2 = edges[0][1], edges[1][1]

				d1 = self._euclid(side1, self.last_point)
				d2 = self._euclid(side2, self.last_point)
				selected = side1 if d1 < d2 else side2
				self.last_point = selected.copy()

				angle = abs(math.degrees(math.atan2(selected[1] - cy, selected[0] - cx)))

				if self.show:
					box_i = np.int32(box + np.array([cx_off, cy_off], dtype=np.float32))
					cv2.drawContours(frame, [box_i], 0, (0, 255, 0), 2)

					fixed_center = (int(cx + cx_off), int(cy + cy_off))
					end_pt = self._rotate_n_deg(fixed_center[0], fixed_center[1], angle, 150)
					color = (0, 255, 0) if abs(angle - 90) > 3 else (0, 0, 255)
					cv2.line(frame, fixed_center, end_pt, color, 2)

					cv2.imshow('Frame blue', img_blue)
					frame_center_x = 330 - 35
					cv2.line(frame, (frame_center_x, 2), (frame_center_x, 170), (0, 255, 0), 2)
					cv2.imshow('Frame', frame)
					cv2.waitKey(1)

			with self.lock:
				self.buf.append(angle)

			time.sleep(0.005)


if __name__ == "__main__":
	cvw = CVWorker()
	cvw.start()

	while True:
		print(cvw.pass_condition()[0])