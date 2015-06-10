from Tkconstants import TOP, RIGHT, LEFT, END
from Tkinter import Button, PhotoImage, Canvas, Frame, Listbox

from geometry import Ray
from tracer import SimpleRayTracer, SimpleShadowRayTracer, ShadingShadowRayTracer, RecursiveRayTracer


class Window(Frame):
	def __init__(self, width, height, scene, tracer, calculate=None):
		Frame.__init__(self, master=None)

		if calculate is None:
			calculate = [0, 0]

		self.d = calculate
		self.scene = scene
		self.after_id = 0
		self.tracer = tracer

		self.threads = []

		self.__init_window(height, width)

		self.master.mainloop()

	def __init_window(self, height, width):
		self.master.title = "Ray Py"
		canvas = Canvas(self.master, width=width, height=height)
		canvas.pack(side=TOP)
		self.img = PhotoImage(width=width, height=height)
		canvas.create_image((width / 2, height / 2), image=self.img, state="normal")
		self.startButton = Button(self.master, text="Render", command=lambda: self.__onStartPressed())
		self.startButton.pack(side=RIGHT)
		self.resetButton = Button(self.master, text="Reset", command=lambda: self.__onResetPressed())
		self.resetButton.config(state="disabled")
		self.resetButton.pack(side=RIGHT)

		self.listbox = Listbox(self.master, height=4)
		self.listbox.bind('<<ListboxSelect>>', self.__selectTracer)
		self.listbox.insert(END, "Simple", "Shadow", "ShadingShadow", "Recursive")
		self.listbox.pack(side=LEFT)

		self.listbox.selection_set(0)
		self.listbox.activate(0)
		self.listbox.focus_set()

	def __selectTracer(self, evt):
		value = self.listbox.get(self.listbox.curselection())
		if value == "Simple":
			self.tracer = SimpleRayTracer()
		elif value == "Shadow":
			self.tracer = SimpleShadowRayTracer()
		elif value == "ShadingShadow":
			self.tracer = ShadingShadowRayTracer(self.scene.eye)
		elif value == "Recursive":
			self.tracer = RecursiveRayTracer(self.scene.eye)

	def __onStartPressed(self):
		self.startButton.config(state="disabled")
		self.listbox.config(state="disabled")
		self.__draw()

	# def __update(self):
	# 	ray = Ray.fromPoints(p1=self.scene.eye, p2=self.scene.screen.pixelToWorldCoord(self.d))
	# 	self.img.put(self.tracer.trace(ray, self.scene.geometry, self.scene.lights).toHex(), (self.d[0], self.d[1]))
	# 	self.master.update()

	def __draw(self):
		count = 0
		stepSize = 4
		while count <= self.scene.screen.resolutionY:
			self.threads = [LineThread(self.tracer, self.img, y, self.scene.screen.resolutionX, self.master, self.scene)
							for y in range(count, count + stepSize)]
			for t in self.threads:
				t.start()
			for t in self.threads:
				t.join()

			count += stepSize

		self.resetButton.config(state="active")

	def __onResetPressed(self):
		self.img.blank()

		self.resetButton.config(state="disabled")
		self.startButton.config(state="active")
		self.listbox.config(state="normal")

		self.threads = []


import threading


class LineThread(threading.Thread):
	def __init__(self, tracer, img, line, width, master, scene):
		threading.Thread.__init__(self)
		self.tracer = tracer
		self.img = img
		self.line = line
		self.width = width
		self.master = master
		self.scene = scene

	def run(self):
		for x in range(self.width):
			ray = Ray.fromPoints(p1=self.scene.eye, p2=self.scene.screen.pixelToWorldCoord((x, self.line)))
			self.img.put(self.tracer.trace(ray, self.scene.geometry, self.scene.lights).toHex(), (x, self.line))
			self.master.update()
