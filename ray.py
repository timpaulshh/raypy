#!/usr/bin/python

from Tkinter import *

import numpy as np

from geometry import Plane, Sphere
from scene import Screen, Scene
from tracer import SimpleShadowRayTracer
from window import Window

if __name__ == "__main__":
	master = Tk()

	WIDTH = 100
	HEIGHT = 100

	canvas = Canvas(master, width=WIDTH, height=HEIGHT)
	canvas.pack()

	img = PhotoImage(width=WIDTH, height=HEIGHT)

	canvas.create_image((WIDTH / 2, HEIGHT / 2), image=img, state="normal")

	eye = np.array([0, 0, -4])
	screen = Screen([0, 0, -1], [0, 0, -1], WIDTH, HEIGHT, 0.1)

	p1 = Plane([0, 5, 0], [0, -1, 0])
	p1.setColor((0, 0, 200))

	p2 = Plane([0, -5, 0], [0, 1, 0])
	p2.setColor((100, 100, 100))

	p3 = Plane([5, 0, 0], [-1, 0, 0])
	p3.setColor((100, 50, 50))

	p4 = Plane([-5, 0, 0], [1, 0, 0])
	p4.setColor((20, 20, 20))

	p5 = Plane([0, 0, 5], [0, 0, -1])
	p5.setColor((200, 200, 200))

	p6 = Plane([0, 0, -5], [0, 0, 1])
	p6.setColor((255, 255, 255))

	s1 = Sphere([0, 3, 2], 2)
	s1.setColor((255, 255, 0))

	l1 = Sphere([-2, -4.5, 4], 1)
	l1.setColor((255, 255, 255))

	scene = Scene(eye, screen, geometry=[s1, p1, p2, p3, p4, p5, p6], lights=[l1])

	window = Window(scene, image=img, master=master, tracer=SimpleShadowRayTracer())
	master.mainloop()
