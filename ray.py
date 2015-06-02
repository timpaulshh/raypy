#!/usr/bin/python

from geometry import Plane, Sphere
from scene import Screen, Scene
from tracer import SimpleRayTracer
from material import Material, Color
from window import Window

if __name__ == "__main__":
	WIDTH = 200
	HEIGHT = 200

	screen = Screen([0, 0, -1], [0, 0, -1], WIDTH, HEIGHT, 0.05)

	p1 = Plane([0, 5, 0], [0, -1, 0], Material(Color(0, 0, 200), 0.5, 0.2, 0.2))
	p2 = Plane([0, -5, 0], [0, 1, 0], Material(Color(100, 100, 100), 0.5, 0.2, 0.2))
	p3 = Plane([5, 0, 0], [-1, 0, 0], Material(Color(100, 50, 50), 0.5, 0.2, 0.2))
	p4 = Plane([-5, 0, 0], [1, 0, 0], Material(Color(20, 20, 20), 0.5, 0.2, 0.2))
	p5 = Plane([0, 0, 5], [0, 0, -1], Material(Color(200, 200, 200), 0.5, 0.2, 0.2))
	p6 = Plane([0, 0, -5], [0, 0, 1], Material(Color(255, 255, 255), 0.5, 0.2, 0.2))

	s1 = Sphere([0, 3, 2], 2, Material(Color(255, 255, 0), 0.5, 0.2, 0.2))
	s2 = Sphere([4, 2, 1], 0.5, Material(Color(255, 255, 255), 0.5, 0.2, 0.2))

	l1 = Sphere([2, -4.5, 4], 1, Material(Color(255, 255, 255), 0.5, 0.2, 0.2))

	eye = [0, 0, -4.9]

	scene = Scene(eye=eye, screen=screen, geometry=[s1, p1, p2, p3, p4, p5, p6, s2], lights=[l1])

	window = Window(WIDTH, HEIGHT, scene, tracer=SimpleRayTracer())
