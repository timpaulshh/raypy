#!/usr/bin/python

from Tkinter import *
import math
import numpy as np
from geometry import Ray, Plane, Sphere
from scene import Screen
from tracer import SimpleRayTracer, SimpleShadowRayTracer

class Window:
	def __init__(self, calculate, geometry, lights, eye, screen, image, master, tracer = SimpleRayTracer()):
		self.geometry = geometry
		self.lights = lights
		self.eye = eye
		self.screen = screen
		self.d = calculate
		self.img = image
		self.master = master
		self.after_id = 0
		self.tracer = tracer
	
	def update(self):
		ray = Ray(p1 = self.eye, p2 = self.screen.pixelToWorldCoord(self.d))
		self.img.put(self.tracer.trace(ray, self.geometry, self.lights), (self.d[0], self.d[1]))

	def draw(self):
		#update image
		self.update()
		
		# next self.d
		if self.d[0] < self.screen.resolutionX:
			self.d[0] = self.d[0] + 1
		else:
			if self.d[1] < self.screen.resolutionY:
				self.d[0] = 0
				self.d[1] = self.d[1] + 1
			else:
				self.master.after_cancel(self.after_id)
				return

		self.after_id = self.master.after(1, self.draw)

if __name__ == "__main__":
	master = Tk()

	WIDTH = 300
	HEIGHT = 300

	canvas = Canvas(master, width=WIDTH, height=HEIGHT)
	canvas.pack()

	img = PhotoImage(width=WIDTH, height=HEIGHT)

	canvas.create_image((WIDTH / 2, HEIGHT / 2), image=img, state="normal")

	eye = np.array([0, 0, -4])
	screen = Screen([0, 0, 0], [0, 0, -1], WIDTH, HEIGHT, 0.1)

	p1 = Plane([0, 5, 0], [0, -1, 0])
	p1.setColor((0, 0, 200))
	
	p2 = Plane([0, -5, 0], [0, 1, 0])
	p2.setColor((100, 100, 100))
	
	p3 = Plane([5, 0, 0], [-1, 0, 0])
	p3.setColor((100, 50, 50))
	
	p4 = Plane([-5, 0, 0],[1, 0, 0])
	p4.setColor((20, 20, 20))
	
	p5 = Plane([0, 0, 5],[0, 0, -1])
	p5.setColor((200, 200, 200)) 
	
	p6 = Plane([0, 0, -5], [0, 0, 1])
	p6.setColor((255, 255, 255))
	
	
	s1 = Sphere([2, 2, 2], 3)
	s1.setColor((255, 255, 0))

	l1 = Sphere([0, -4.5, -2], 1)
	l1.setColor((255, 255, 255))

	window = Window(calculate = [0,0], geometry = [s1, p1, p2, p3, p4, p5, p6], lights = [l1], eye = eye, screen = screen, image = img, master = master, tracer = SimpleShadowRayTracer())
	window.draw()
	master.mainloop()
