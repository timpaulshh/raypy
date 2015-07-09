# !/usr/bin/python

from abc import ABCMeta, abstractmethod

import numpy as np

from material import Material, Color


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

	def __str__(self):
		return "Origin: %s, Direction: %s" % (self.origin, self.direction)


class GeometryObject:
	__metaclass__ = ABCMeta

	def __init__(self, material):
		if material is None:
			material = Material(Color(0, 0, 0), 0, 0)
		self.material = material

	def setColor(self, color):
		self.material.color = color

	def getColor(self):
		return self.material.color

	def getColorHex(self):
		return self.material.color.toHex()

	@abstractmethod
	def intersect(self, ray):
		pass

	@abstractmethod
	def normalAt(self, point):
		pass


class Plane(GeometryObject):
	def __init__(self, origin, normal, material=None):
		GeometryObject.__init__(self, material)
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
	def __init__(self, center, radius, material=None):
		GeometryObject.__init__(self, material)
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
			return filter(lambda e: e > 0, [loc * -1])

		return filter(lambda e: e > 0, [loc * -1 - np.sqrt(term), loc * -1 + np.sqrt(term)]) 

	def normalAt(self, point):
		#    N = ((x - cx)/R, (y - cy)/R, (z - cz)/R)
		nx = (point[0] - self.center[0]) / self.radius
		ny = (point[1] - self.center[1]) / self.radius
		nz = (point[2] - self.center[2]) / self.radius

		return np.array([nx, ny, nz])

class Triangle(GeometryObject):
	def __init__(self, v0, v1, v2, material=None):
		GeometryObject.__init__(self, material)
		self.v0 = np.array(v0)
		self.v1 = np.array(v1)
		self.v2 = np.array(v2)

	def intersect(self, ray):
		# get triangles normal plane
		U = self.v1 - self.v0
		V = self.v2 - self.v0
		N = np.cross(U, V)

		P = Plane(self.v0, N)

		distance = P.intersect(ray)[0]

		if distance == np.inf:
			return [np.inf]

		intersection = ray.origin + ray.direction * distance

		if self.pointIn(intersection):
			return [distance]

		return [np.inf]

	def pointIn(self, point):
		U = self.v1 - self.v0
		V = self.v2 - self.v0

		# is intersection inside the triangle?
		uu = np.dot(U, U)
		uv = np.dot(U, V)
		vv = np.dot(V, V)
		w = point - self.v0
		wu = np.dot(w, U)
		wv = np.dot(w, V)
		D = uv*uv - uu*vv

		s = (uv*wv - vv*wu) / D
		if s < 0.0 or s > 1.0:
			return False

		t = (uv*wu - uu*wv) / D
		if t < 0.0 or (s+t) > 1.0:
			return False

		return True

	def normalAt(self, point):
		# get triangles normal plane
		U = self.v1 - self.v0
		V = self.v2 - self.v0
		N = np.cross(U, V)

		return N

class Cube(GeometryObject):
	def __init__(self, center, length, material=None):
		GeometryObject.__init__(self, material)
		self.center = np.array(center)
		self.radius = length / 2

		v1 = [center[0] - self.radius, center[1] + self.radius, center[2] - self.radius]
		v2 = [center[0] + self.radius, center[1] + self.radius, center[2] - self.radius]
		v3 = [center[0] + self.radius, center[1] + self.radius, center[2] + self.radius]
		v4 = [center[0] - self.radius, center[1] + self.radius, center[2] + self.radius]
		v5 = [center[0] - self.radius, center[1] - self.radius, center[2] - self.radius]
		v6 = [center[0] + self.radius, center[1] - self.radius, center[2] - self.radius]
		v7 = [center[0] + self.radius, center[1] - self.radius, center[2] + self.radius]
		v8 = [center[0] - self.radius, center[1] - self.radius, center[2] + self.radius]

		# unten
		t1 = Triangle(v1, v2, v3, self.material)
		t2 = Triangle(v1, v3, v4, self.material)

		# vorne 
		t3 = Triangle(v1, v2, v6, self.material)
		t4 = Triangle(v1, v6, v5, self.material)

		# links
		t5 = Triangle(v4, v1, v5, self.material)
		t6 = Triangle(v4, v5, v8, self.material)

		# rechts
		t7 = Triangle(v2, v3, v7, self.material)
		t8 = Triangle(v2, v7, v6, self.material)

		# hinten
		t9 = Triangle(v3, v4, v8, self.material)
		t10 = Triangle(v3, v8, v7, self.material)

		# oben
		t11 = Triangle(v5, v6, v7, self.material)
		t12 = Triangle(v5, v7, v8, self.material)

		self.triangles = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12]

	def intersect(self, ray):
		lol = map(lambda t: t.intersect(ray), self.triangles)
		distance = reduce(lambda x,y: min(x, y), lol)
		return distance

	def normalAt(self, point):
		for t in self.triangles:
			if t.pointIn(point):
				return t.normalAt(point)

		return None





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
