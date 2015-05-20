#!/usr/bin/python

from Tkinter import *
import math
import numpy as np
from geometry import Ray, Plane, Sphere
from scene import Screen

class SimpleRayTracer:
	def __init__(self):
		pass
		
	# returns a sorted list of tuples (distance, object)
	def __distances(self, objects, ray):
		return sorted(list(self.__distancesgen(objects, ray)), key=lambda x: x[0])
			
	def __distancesgen(self, objects, ray):
		for obj in objects:
			yield (obj.intersect(ray), obj)
	
	def trace(self, ray, objects):
		nearest = self.__distances(objects, ray)[0]
		if min(nearest[0]) < np.inf:
			return nearest[1].getColorHex()
		else:
			return "#ffffff"

class Window:
	def __init__(self, calculate, geometry, eye, screen, image, master, tracer = SimpleRayTracer()):
		self.geometry = geometry
		self.eye = eye
		self.screen = screen
		self.d = calculate
		self.img = image
		self.master = master
		self.after_id = 0
		self.tracer = tracer
	
	def update(self):
		ray = Ray(p1 = self.eye, p2 = self.screen.pixelToWorldCoord(self.d))
		self.img.put(self.tracer.trace(ray, self.geometry), (self.d[0], self.d[1]))

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

	WIDTH = 100
	HEIGHT = 100

	canvas = Canvas(master, width=WIDTH, height=HEIGHT)
	canvas.pack()

	img = PhotoImage(width=WIDTH, height=HEIGHT)

	canvas.create_image((WIDTH / 2, HEIGHT / 2), image=img, state="normal")

	eye = np.array([0, 0, 0])
	screen = Screen([0, 0, 3], [0, 0, -1], WIDTH, HEIGHT, 0.1)

	p = Plane([0, 5, 0], [0, -1, 0])
	p.setColor((0, 0, 200))
	s1 = Sphere([0, 0, 10], 5)
	s2 = Sphere([0, 3, 5], 2)
	s2.setColor((0, 200, 0))

	window = Window(calculate = [0,0], geometry = [s2, s1, p], eye = eye, screen = screen, image = img, master = master)
	window.draw()
	master.mainloop()
