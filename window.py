from Tkinter import Button

from geometry import Ray


class Window:
	def __init__(self, scene, image, master, tracer, calculate=None):
		if calculate is None:
			calculate = [0, 0]

		self.d = calculate
		self.scene = scene
		self.img = image
		self.master = master
		self.after_id = 0
		self.tracer = tracer

		Button(master, text="Start", command=self.draw).pack()

	def update(self):
		ray = Ray.fromPoints(p1=self.scene.eye, p2=self.scene.screen.pixelToWorldCoord(self.d))
		self.img.put(self.tracer.trace(ray, self.scene.geometry, self.scene.lights), (self.d[0], self.d[1]))

	def draw(self):
		# update image
		self.update()

		# next self.d
		if self.d[0] < self.scene.screen.resolutionX:
			self.d[0] = self.d[0] + 1
		else:
			if self.d[1] < self.scene.screen.resolutionY:
				self.d[0] = 0
				self.d[1] = self.d[1] + 1
			else:
				self.master.after_cancel(self.after_id)
				return

		self.after_id = self.master.after(1, self.draw)
