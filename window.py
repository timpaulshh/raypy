from Tkinter import Button, PhotoImage, Canvas, Frame

from geometry import Ray


class Window(Frame):
	def __init__(self, width, height, scene, tracer, calculate=None):
		Frame.__init__(self, master=None)

		if calculate is None:
			calculate = [0, 0]

		self.d = calculate
		self.scene = scene
		self.after_id = 0
		self.tracer = tracer

		self.__init_window(height, width)

		self.master.mainloop()

	def __init_window(self, height, width):
		self.master.title = "Ray Py"
		canvas = Canvas(self.master, width=width, height=height)
		canvas.pack()
		self.img = PhotoImage(width=width, height=height)
		canvas.create_image((width / 2, height / 2), image=self.img, state="normal")
		self.startButton = Button(self.master, text="Render", command=lambda: self.__onStartPressed(1))
		self.startButton.pack()

		self.instantly = Button(self.master, text="Render instantly", command=lambda: self.__onStartPressed(0))
		self.instantly.pack()

	def __onStartPressed(self, delay):
		self.startButton.config(state="disabled")
		self.instantly.config(state="disabled")
		self.__draw(delay)

	def __update(self):
		ray = Ray.fromPoints(p1=self.scene.eye, p2=self.scene.screen.pixelToWorldCoord(self.d))
		self.img.put(self.tracer.trace(ray, self.scene.geometry, self.scene.lights), (self.d[0], self.d[1]))

	def __draw(self, delay):
		# update image
		self.__update()

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

		self.after_id = self.master.after(delay, self.__draw, delay)
