from Tkconstants import TOP, RIGHT, LEFT, END
from Tkinter import Button, PhotoImage, Canvas, Frame, Listbox

from geometry import Ray
from tracer import SimpleRayTracer, SimpleShadowRayTracer, ShadingShadowRayTracer, RecursiveRayTracer, PathTracer


class Window(Frame):
	RENDER_PROCESSES = 4

	def __init__(self, width, height, scene, tracer, calculate=None):
		Frame.__init__(self, master=None)

		if calculate is None:
			calculate = [0, 0]

		self.d = calculate
		self.scene = scene
		self.after_id = 0
		self.tracer = tracer
		self.width = width
		self.height = height

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

		self.listbox = Listbox(self.master, height=5)
		self.listbox.bind('<<ListboxSelect>>', self.__selectTracer)
		self.listbox.insert(END, "Simple", "Shadow", "ShadingShadow", "Recursive", "PathTracer")
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
		elif value == "PathTracer":
			self.tracer = PathTracer()

	def __onStartPressed(self):
		self.startButton.config(state="disabled")
		self.listbox.config(state="disabled")
		self.__draw()

	def __update(self):
		if self.finishedQueue.qsize() >= self.RENDER_PROCESSES:
			self.finishedThreads = self.RENDER_PROCESSES
			while not self.finishedQueue.empty():
				self.finishedQueue.get()

		if not self.dataQueue.empty():
			item = self.dataQueue.get()
			self.img.put(item[1], item[0])
			self.master.update()
		elif self.finishedThreads == self.RENDER_PROCESSES:
			for t in self.threads:
				t.join()

			self.master.after_cancel(self.after_id)
			self.resetButton.config(state="active")
			return

		self.after_id = self.master.after(0, self.__update)

	def __draw(self):
		from processes import BlockProcess
		from multiprocessing import Queue
		self.finishedQueue = Queue()
		self.dataQueue = Queue()
		self.finishedThreads = 0

		self.threads = BlockProcess.forCount(self.RENDER_PROCESSES, self.width, self.height, self.tracer, self.scene, self.dataQueue, self.finishedQueue)

		for t in self.threads:
			t.start()

		self.__update()

		self.after_id = self.master.after(0, self.__update)

	def __onResetPressed(self):
		self.img.blank()
		self.d = [0, 0]
		self.resetButton.config(state="disabled")
		self.startButton.config(state="active")
		self.listbox.config(state="normal")
