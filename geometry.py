#!/usr/bin/python

from abc import ABCMeta, abstractmethod
import numpy as np

# returns rgb-color value as hex-value (web format)
# rgb has to be a triple (r, g, b)
def rgb_to_hex(rgb):
	return "#%02x%02x%02x" % rgb

def vector_length(v):
	return np.linalg.norm(v)
		
def normalize(v):
	return v / vector_length(v)

class Ray:
	def __init__(self, origin, direction):
		self.origin = np.array(origin)
		self.direction = normalize(np.array(direction))

	def __init__(self, p1, p2):
		# constructs normalized ray from two points
		self.origin = np.array(p1)
		self.direction = normalize(np.array(p2)-np.array(p1))

class GeometryObject:
	__metaclass__ = ABCMeta

	def __init__(self, color = (0, 0, 0)):
		self.rgb = color

	def setColor(self, rgb):
		self.rgb = rgb

	def getColorHex(self):
		return rgb_to_hex(self.rgb)

	@abstractmethod
	def intersect(self, ray):
		pass

class Plane(GeometryObject):
	def __init__(self, origin, normal):
		GeometryObject.__init__(self)
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

class Sphere(GeometryObject):
	def __init__(self, center, radius):
		GeometryObject.__init__(self)
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

if __name__ == "__main__":
	r = Ray([0, 0, 0], [0, 0, 1])
	r2 = Ray(p1 = [0, 0, 10], p2 = [0, 0, 0])
	p = Plane([0, 0, 5], [0, 0, -1])
	s = Sphere([0, 0, 2], 1)
	s.setColor((255, 0, 0))
	print p.intersect(r)
	print s.intersect(r)
	print p.intersect(r2)
	print s.getColorHex()
