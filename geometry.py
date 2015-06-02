# !/usr/bin/python

from abc import ABCMeta, abstractmethod
from color import Color

import numpy as np

def vector_length(v):
	return np.linalg.norm(v)


def normalize(v):
	return v / vector_length(v)


class Ray:
	def __init__(self, origin, direction):
		self.origin = np.array(origin)
		self.direction = normalize(np.array(direction))

	# returns a ray, defined by 2 points.
	@classmethod
	def fromPoints(cls, p1, p2):
		return cls(np.array(p1), np.array(p2) - np.array(p1))


class GeometryObject:
	__metaclass__ = ABCMeta

	def __init__(self, color):
		self.rgb = color

	def setColor(self, rgb):
		self.rgb = rgb

	def getColor(self):
		return self.rgb

	def getColorHex(self):
		return self.rgb.toHex()

	@abstractmethod
	def intersect(self, ray):
		pass

	@abstractmethod
	def normalAt(self, point):
		pass


class Plane(GeometryObject):
	def __init__(self, origin, normal, color=(0, 0, 0)):
		GeometryObject.__init__(self, color)
		self.origin = np.array(origin)
		self.normal = normalize(np.array(normal))

	def intersect(self, ray):
		denom = np.dot(ray.direction, self.normal)
		if np.abs(denom) < 1e-6:
			return [np.inf]
		d = np.dot(self.origin - ray.origin, self.normal) / denom
		if d < 0:
			return [np.inf]
		return [d]

	def normalAt(self, point):
		return self.normal


class Sphere(GeometryObject):
	def __init__(self, center, radius, color=(0, 0, 0)):
		GeometryObject.__init__(self, color)
		self.center = np.array(center)
		self.radius = radius

	def intersect(self, ray):
		# line-sphere intersection term from en.wiki.org
		loc = np.dot(ray.direction, (ray.origin - self.center))
		oc_length = vector_length(ray.origin - self.center)
		# term in sqrt
		term = loc * loc - oc_length * oc_length + self.radius * self.radius

		# no solution, because sqrt of less than zero is not defined.
		if term < 0:
			return [np.inf]

		# sqrt of zero is zero, we dont have to compute it.
		if np.abs(term) < 1e-6:
			return [loc * -1]

		return [loc * -1 - np.sqrt(term), loc * -1 + np.sqrt(term)]

	def normalAt(self, point):
		#    N = ((x - cx)/R, (y - cy)/R, (z - cz)/R)
		nx = (point[0] - self.center[0]) / self.radius
		ny = (point[1] - self.center[1]) / self.radius
		nz = (point[2] - self.center[2]) / self.radius

		return np.array([nx, ny, nz])


if __name__ == "__main__":
	r = Ray([0, 0, 0], [0, 0, 1])
	r2 = Ray.fromPoints(p1=[0, 0, 10], p2=[0, 0, 0])
	p = Plane([0, 0, 5], [0, 0, -1])
	s = Sphere([0, 0, 2], 1)
	s.setColor(Color(255, 0, 0))
	print p.intersect(r)
	print s.intersect(r)
	print p.intersect(r2)
	print s.getColorHex()
