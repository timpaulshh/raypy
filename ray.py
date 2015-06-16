#!/usr/bin/python

from geometry import Plane, Sphere
from scene import Screen, Scene
from tracer import SimpleRayTracer, SimpleShadowRayTracer, ShadingShadowRayTracer, RecursiveRayTracer
from material import Material, Color
from window import Window

if __name__ == "__main__":

	WIDTH = 200
	HEIGHT = 200

	screen = Screen([0, 0, -1], [0, 0, -1], WIDTH, HEIGHT, 0.05)

	p1 = Plane([0, 5, 0], [0, -1, 0], Material(Color(0, 0, 200), 0.5, 0, 0.2))
	p2 = Plane([0, -5, 0], [0, 1, 0], Material(Color(100, 100, 100), 0.5, 0, 0.2))
	p3 = Plane([5, 0, 0], [-1, 0, 0], Material(Color(100, 50, 50), 0.5, 0, 0.2))
	p4 = Plane([-5, 0, 0], [1, 0, 0], Material(Color(20, 20, 20), 0.5, 0, 0.2))
	p5 = Plane([0, 0, 5], [0, 0, -1], Material(Color(0, 200, 0), 0.5, 0, 0.2))
	p6 = Plane([0, 0, -5], [0, 0, 1], Material(Color(200, 0, 0), 0.5, 0, 0.2))

	s1 = Sphere([0, 3, 2], 2, Material(Color(200, 200, 0), 0.5, 0.8, 0.2, refractive=False, n=1.52))
	s2 = Sphere([4, 2, 1], 0.5, Material(Color(0, 250, 0), 0.5, 0.8, 0.2, refractive=False, n=1.52))
	s3 = Sphere([-3, 2, 1], 1, Material(Color(0, 0, 250), 0.5, 0.8, 0.2, refractive=False, n=1.52))
	s4 = Sphere([2, -2, 1], 0.8, Material(Color(0, 250, 250), 0.5, 0.8, 0.2, refractive=False, n=1.52))

	l1 = Sphere([0, -4, 0], 1, Material(Color(255, 255, 255), 0.5, 0.2, 0.2))

	eye = [0, 0, -4.9]

	scene = Scene(eye=eye, screen=screen, geometry=[s1, p1, p2, p3, p4, p5, p6, s2, s3, s4], lights=[l1])

	import argparse
	parser = argparse.ArgumentParser(description="Ray Tracing in Python.")
	parser.add_argument("-r", "--render", help="activate non-interactive rendering into a file.", nargs=2,
						metavar=("FILENAME", "ALGORITHM"))

	args = parser.parse_args()

	if not args.render is None:
		print "rendering mode into: %s with %s" % (args.render[0], args.render[1])
		from filerenderer import FileRenderer

		value = args.render[1]

		if value == "Simple":
			tracer = SimpleRayTracer()
		elif value == "Shadow":
			tracer = SimpleShadowRayTracer()
		elif value == "ShadingShadow":
			tracer = ShadingShadowRayTracer(scene.eye)
		elif value == "Recursive":
			tracer = RecursiveRayTracer(scene.eye)
		else:
			print "Unknown Ray-Tracer Algorithm. Exiting ..."
			exit(1)

		renderer = FileRenderer(WIDTH, HEIGHT, tracer, scene)
		renderer.render(args.render[0])
	else:
		window = Window(WIDTH, HEIGHT, scene, tracer=SimpleRayTracer())
