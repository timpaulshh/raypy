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


