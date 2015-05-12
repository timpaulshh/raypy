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
	def update(self):
		if self.geometry.contains(self.d[0], self.d[1]):
			self.state[self.d[0]][self.d[1]] = "#000000"

	def draw(self):
		# calculate new state for self.d
		self.update()

		# next self.d
		# hier ist irgendwas falsch
		if self.d[0] < self.dimension[0]:
			self.d[0] = self.d[0] + 1
		else:
			if self.d[1] < self.dimension[1]:
				self.d[0] = 0
				self.d[1] = self.d[1] + 1
			else:
				self.master.after_cancel(self.after_id)
				return

		#draw state
		for x,row in enumerate(self.state):
			for y,value in enumerate(row):
				self.img.put(value, (x, y))

		# und zwar wenn man hier 10 statt 15 einsetzt?
		self.after_id = self.master.after(15, self.draw)

	def __init__(self, calculate, dimension, geometry, image, master):
		self.geometry = geometry
		self.d = calculate
		self.state = [["#ffffff" for x in range(dimension[0])] for x in range(dimension[1])]
		self.dimension = dimension
		self.img = image
		self.master = master
		self.after_id = 0

master = Tk()

WIDTH = 50
HEIGHT = 50

canvas = Canvas(master, width=WIDTH, height=HEIGHT)
canvas.pack()

img = PhotoImage(width=WIDTH, height=HEIGHT)

canvas.create_image((WIDTH / 2, HEIGHT / 2), image=img, state="normal")

c = Circle(x=WIDTH / 2, y=HEIGHT / 2, radius=WIDTH / 2)

window = Window(calculate = [0,0], dimension = (WIDTH, HEIGHT), geometry = c, image = img, master = master)

window.draw()

master.mainloop()


