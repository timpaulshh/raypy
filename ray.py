#!/usr/bin/python

from Tkinter import *
import math

class Circle:
	def contains(self, x, y):
		return  math.pow(x-self.x,2) + math.pow(y-self.y,2) <= math.pow(self.r,2)

	def __init__(self, x, y, radius):
		self.x = x
		self.y = y
		self.r = radius


class Window:
	def update():
		if geometry.contains(self.d[0], self.d[1]):
			self.state[self.d[0]][self.d[1]] = "#000000"

	def draw(self):
		# calculate new state for self.d
		self.update()

		# next self.d
		if (self.d[0] < self.dimension[0]:
			self.d[0] = self.d[0] + 1
		else:
			self.d[0] = 0
			self.d[1] = self.d[0] + 1

		#draw state
		for x,row in enumerate(self.state):
			for y,value in enumerate(row):
				img.put(value, (x, y))

		self.after(1000, self.draw)

	def __init__(self, calculate, dimension, geometry):
		self.geometry = geometry
		self.d = calculate
		self.state = [["#ffffff" for x in range(dimension[0])] for x in range(dimension[1])]
		self.dimension = dimension

master = Tk()

canvas = Canvas(master, width=200, height=200)
canvas.pack()

img = PhotoImage(width=200, height=200)

canvas.create_image((100, 100), image=img, state="normal")

c = Circle(x=100, y=100, radius=50)

for x in range(200):
	for y in range(200):
		if c.contains(x, y):
			img.put("#000000", (x, y))


mainloop()


