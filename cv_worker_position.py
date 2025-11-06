import cv2
import numpy as np
import math
import threading
import time
from collections import deque

class CVWorkerPositioning:
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
		template_paths=None,
		match_thresh=0.75,
		rotate_step_deg=None,
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

		# ahora lista
		self.template_paths = template_paths or []
		self.match_thresh = float(match_thresh)
		self.rotate_step_deg = rotate_step_deg

		# guardamos (tpl_img, angle, name)
		self.templates = []

	@staticmethod
	def _binarize_u8(img_gray):
		_, bw = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
		return bw

	@staticmethod
	def _hsv_color_filter(image, lo, hi):
		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		msk = cv2.inRange(hsv, lo, hi)
		grey = cv2.cvtColor(cv2.bitwise_and(image, image, mask=msk), cv2.COLOR_BGR2GRAY)
		return CVWorkerPositioning._binarize_u8(grey)  # CAMBIO: ahora devuelvo binario directo

	def _prepare_templates(self):
		self.templates.clear()
		if not self.template_paths:
			return

		for path in self.template_paths:
			tpl = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
			if tpl is None:
				print(f"Advertencia: no se pudo leer {path}")
				continue
			tpl_bw = self._binarize_u8(tpl)
			base_name = path.split("/")[-1]
			self.templates.append((tpl_bw, 0, base_name))

			if self.rotate_step_deg and self.rotate_step_deg > 0:
				h, w = tpl_bw.shape
				center = (w / 2, h / 2)
				angle = self.rotate_step_deg
				while angle < 180:
					M = cv2.getRotationMatrix2D(center, angle, 1.0)
					rot = cv2.warpAffine(tpl_bw, M, (w, h), flags=cv2.INTER_NEAREST, borderValue=0)
					self.templates.append((rot, angle, base_name))
					angle += self.rotate_step_deg

	def _find_template(self, img_bw):
		if not self.templates:
			return False, 0.0, None, None, None, None  # found, score, (x,y), (w,h), angle, name

		best = (False, 0.0, None, None, None, None)
		for tpl, ang, name in self.templates:
			th, tw = tpl.shape
			if img_bw.shape[0] < th or img_bw.shape[1] < tw:
				continue
			res = cv2.matchTemplate(img_bw, tpl, cv2.TM_CCOEFF_NORMED)
			_, maxVal, _, maxLoc = cv2.minMaxLoc(res)
			if maxVal > best[1]:
				best = (maxVal >= self.match_thresh, maxVal, maxLoc, (tw, th), ang, name)
		return best

	def start(self):
		if self.running:
			return
		self._prepare_templates()  # NUEVO: precalcula templates
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
	
	def test(self) -> bool:
		if not self.cam or not self.cam.isOpened():
			raise RuntimeError("La cámara no está inicializada. Usa start() antes de test().")

		ok, frame = self.cam.read()
		if not ok or frame is None:
			return False

		r0, r1 = self.roi_rows
		c0, c1 = self.roi_cols
		roi = frame[r0:r1, c0:c1]
		img_bw = self._hsv_color_filter(roi, self.blue_lo, self.blue_hi)

		found, score, loc, wh, ang, name = self._find_template(img_bw)
		if found:
			print(f"[MATCH] {name} score={score:.2f} angle={ang:.1f}")
		else:
			print(f"[NO MATCH] max_score={score:.2f}")

		return bool(found)

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
			if not ok:
				time.sleep(0.01)
				continue

			roi = frame[r0:r1, c0:c1]
			img_bw = self._hsv_color_filter(roi, self.blue_lo, self.blue_hi)

			found, score, loc, wh, ang, name = self._find_template(img_bw)
			if self.show:
				vis = cv2.cvtColor(img_bw, cv2.COLOR_GRAY2BGR)
				if found and loc and wh:
					x, y = loc
					w, h = wh
					cv2.rectangle(vis, (x, y), (x+w, y+h), (0,255,0), 2)
					cv2.putText(vis, f"{name} {score:.2f} @{ang:.0f}°",
								(x, max(0,y-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

				cv2.imshow('ROI bin', vis)
				cv2.imshow('Frame', frame)
				cv2.waitKey(1)

			# Guarda resultado simple al buffer si lo necesitas
			with self.lock:
				self.buf.append(score if found else 0.0)

			time.sleep(0.005)

if __name__ == "__main__":
	# Ejemplo:
	# - template_path: ruta al PNG binario de referencia
	# - rotate_step_deg: define rotaciones para tolerar orientaciones
	cvw = CVWorkerPositioning(
		show=False,
		template_paths=["positioning/referencia2.png", "positioning/referencia1.png"],
		match_thresh=0.60,
		rotate_step_deg=15
	)
	cvw.start()
	while True:
		time.sleep(1)
