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
		roi_rows=(215, 295),
		roi_cols=(283, 338),
		blue_lo=(0, 0, 229),
		blue_hi=(180, 30, 255),
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

	def _loop(self):
		r0, r1 = self.roi_rows
		c0, c1 = self.roi_cols

		while self.running:
			ok, frame = self.cam.read() if self.cam else (False, None)
			print(ok)
			if not ok:
				time.sleep(0.01)
				continue

			roi = frame[r0:r1, c0:c1]
			img_blue = self._hsv_color_filter(roi, self.blue_lo, self.blue_hi)


			if self.show:
				cv2.imshow('Frame blue', img_blue)
				cv2.imshow('Frame', frame)
				cv2.waitKey(1)

			time.sleep(0.005)


if __name__ == "__main__":
	cvw = CVWorker(show=True)
	cvw.start()

	while True:
		...