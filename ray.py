#!/usr/bin/python

from Tkinter import *
import math
import numpy as np
from geometry import Ray, Plane, Sphere
from scene import Screen

class Circle:
	def contains(self, x, y):
		return  math.pow(x-self.x,2) + math.pow(y-self.y,2) <= math.pow(self.r,2)

	def __init__(self, x, y, radius):
		self.x = x
		self.y = y
		self.r = radius

class Window:
	def update(self):
		ray = Ray(p1 = self.eye, p2 = self.screen.pixelToWorldCoord(self.d))
		if self.geometry.intersect(ray) < np.inf:
			self.img.put(self.geometry.getColorHex(), (self.d[0], self.d[1]))
		else:
			self.img.put("#ffffff", (self.d[0], self.d[1]))

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

	def __init__(self, calculate, geometry, eye, screen, image, master):
		self.geometry = geometry
		self.eye = eye
		self.screen = screen
		self.d = calculate
		self.img = image
		self.master = master
		self.after_id = 0


if __name__ == "__main__":
	master = Tk()

	WIDTH = 100
	HEIGHT = 100

	canvas = Canvas(master, width=WIDTH, height=HEIGHT)
	canvas.pack()

	img = PhotoImage(width=WIDTH, height=HEIGHT)

	canvas.create_image((WIDTH / 2, HEIGHT / 2), image=img, state="normal")

	eye = np.array([0, 0, 0])
	screen = Screen([0, 0, 5], [0, 0, -1], WIDTH, HEIGHT, 0.1)

#	p = Plane([0, 0, 5], [0, 0, -1])
	s = Sphere([0, 0, 10], 5)
	s.setColor((200, 0, 0))

	window = Window(calculate = [0,0], geometry = s, eye = eye, screen = screen, image = img, master = master)
	window.draw()
	master.mainloop()


