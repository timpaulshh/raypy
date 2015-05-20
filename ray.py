#!/usr/bin/python

from Tkinter import *
import math
import numpy as np

class Circle:
	def contains(self, x, y):
		return  math.pow(x-self.x,2) + math.pow(y-self.y,2) <= math.pow(self.r,2)

	def __init__(self, x, y, radius):
		self.x = x
		self.y = y
		self.r = radius


class Window:
	def update(self):
		if self.geometry.contains(self.d[0], self.d[1]):
			self.img.put("#000000", (self.d[0], self.d[1])) 
		else:
			self.img.put("#ffffff", (self.d[0], self.d[1])) 

	def draw(self):
		#update image
		self.update()
		
		# next self.d
		if self.d[0] < self.dimension[0]:
			self.d[0] = self.d[0] + 1
		else:
			if self.d[1] < self.dimension[1]:
				self.d[0] = 0
				self.d[1] = self.d[1] + 1
			else:
				self.master.after_cancel(self.after_id)
				return

		self.after_id = self.master.after(1, self.draw)

	def __init__(self, calculate, dimension, geometry, image, master):
		self.geometry = geometry
		self.d = calculate
		self.dimension = dimension
		self.img = image
		self.master = master
		self.after_id = 0

class Ray:
	def __init__(self, origin, direction):
		self.origin = np.array(origin)
		self.direction = np.array(direction) / np.linalg.norm(np.array(direction))

class Plane:
	def __init__(self, origin, normal):
		self.origin = np.array(origin)
		self.normal = np.array(normal) / np.linalg.norm(np.array(normal))

	def intersect(self, ray):
		denom = np.dot(ray.direction, self.normal)
		if np.abs(denom) < 1e-6:
			return np.inf
		d = np.dot(self.origin - ray.origin, self.normal) / denom
		if d < 0:
			return np.inf
		return d
		
class Sphere:
	def __init__(self, center, radius):
		self.center = np.array(center)
		self.radius = radius
	
	def intersect(self, ray):
		# line-sphere intersection term from en.wiki.org
		loc = np.dot(ray.direction, (ray.origin - self.center))
		oc_length = np.linalg.norm(ray.origin - self.center)
		# term in sqrt
		term = loc * loc - oc_length * oc_length + self.radius * self.radius
		
		# no solution, because sqrt of less than zero is not defined.
		if term < 0:
			return np.inf
		
		# sqrt of zero is zero, we dont have to compute it.	
		if np.abs(term) < 1e-6:
			return loc * -1
			
		return loc * -1 - np.sqrt(term)


r = Ray([0, 0, 0], [0, 0, 1])
p = Plane([0, 0, 5], [0, 0, -1])
s = Sphere([0, 0, 2], 1)
print p.intersect(r)
print s.intersect(r)


master = Tk()

WIDTH = 100
HEIGHT = 100

canvas = Canvas(master, width=WIDTH, height=HEIGHT)
canvas.pack()

img = PhotoImage(width=WIDTH, height=HEIGHT)

canvas.create_image((WIDTH / 2, HEIGHT / 2), image=img, state="normal")

c = Circle(x=WIDTH / 2, y=HEIGHT / 2, radius=WIDTH / 2)

window = Window(calculate = [0,0], dimension = (WIDTH, HEIGHT), geometry = c, image = img, master = master)

window.draw()

master.mainloop()


