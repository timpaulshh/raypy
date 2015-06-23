#!/usr/bin/python

from abc import ABCMeta, abstractmethod
import math

import numpy as np

from geometry import Ray, normalize
from material import Color, WHITE

EPSILON = 0.0001
LIGHT_DAMPING = 0.5

class DistanceObject:
	def __init__(self, distance, obj):
		self.distance = distance
		self.object = obj

class Tracer:
	__metaclass__ = ABCMeta

	# returns a sorted list of tuples (distance, object)
	def distances(self, objects, ray):
		return sorted(list(self.__distancesgen(objects, ray)), key=lambda x: x.distance)

	def __distancesgen(self, objects, ray):
		for obj in objects:
			intersections = obj.intersect(ray)
			for intersection in intersections:
				yield DistanceObject(intersection, obj)

	@abstractmethod
	def trace(self, ray, objects, lights):
		pass

class RayTracer(Tracer):
	__metaclass__ = ABCMeta

	def lightAttenuation(self, intersection, light):
		from geometry import vector_length

		path = light.center - intersection
		distance = vector_length(path)

		return 1.0 / (distance**2)

	@abstractmethod
	def shading(self, intersection, intersector, light):
		pass

	@abstractmethod
	def calcShadowFactor(self, intersection, objects, light):
		pass


class SimpleRayTracer(RayTracer):
	def shading(self, intersection, intersector, light):
		return intersector.getColor()

	def calcShadowFactor(self, intersection, objects, light):
		return 1

	def trace(self, ray, objects, lights=[]):
		nearest = self.distances(objects, ray)[0]
		if nearest.distance < np.inf:
			return self.shading(None, nearest.object, None)
		else:
			return WHITE


class SimpleShadowRayTracer(RayTracer):
	def shading(self, intersection, intersector, light):
		ambient = intersector.getColor() * intersector.material.ambient
		diffuse = intersector.getColor() * intersector.material.diffuse
		specular = intersector.getColor() * intersector.material.specular

		return ambient + diffuse + specular

	def calcShadowFactor(self, intersection, objects, light):
		shadowRay = Ray.fromPoints(p1=intersection, p2=light.center)
		shadowDistances = self.distances(objects, shadowRay)

		# if the distance is too low, it is most likely an intersection with the intersection
		# thanks to floating point inaccuracy.
		if abs(shadowDistances[0].distance) < EPSILON:
			shadowNearest = shadowDistances[1]
		else:
			shadowNearest = shadowDistances[0]

		lightDistance = self.distances([light], shadowRay)[0].distance

		# if the nearest intersection is in a higher or equal distance to the light, than
		# the distance from this point to the light, then there is nothing in between.
		if shadowNearest.distance >= lightDistance:
			return 1
		else:
			return 0

	def trace(self, ray, objects, lights):
		distances = self.distances(objects, ray)
		nearest = distances[0]

		# nothing is hit.
		if nearest.distance == np.inf:
			return WHITE

		# ambient color of nearest
		C = nearest.object.getColor() * nearest.object.material.ambient

		intersection = ray.origin + nearest.distance * ray.direction

		for light in lights:
			C = C + (self.shading(intersection, nearest.object, light) * self.calcShadowFactor(intersection, objects, light))

		return C


# @todo: still is not stable for more than one light-source
class ShadingShadowRayTracer(SimpleShadowRayTracer):
	def __init__(self, eye):
		self.eye = eye

	def trace(self, ray, objects, lights):
		distances = self.distances(objects, ray)
		nearest = distances[0]

		# nothing is hit.
		if nearest.distance == np.inf:
			return WHITE

		# ambient color of nearest
		C = nearest.object.getColor() * nearest.object.material.ambient

		intersection = ray.origin + nearest.distance * ray.direction

		for light in lights:
			C = C + (self.shading(intersection, nearest.object, light) * self.calcShadowFactor(intersection, objects, light))

		r = min(C.r, nearest.object.getColor().r)
		g = min(C.g, nearest.object.getColor().g)
		b = min(C.b, nearest.object.getColor().b)

		return Color(r, g, b)

	def shading(self, intersection, intersector, light):
		shadowRay = Ray.fromPoints(p1=intersection, p2=light.center)
		# phong-blinn shading

		# ambient
		ambient = intersector.getColor() * intersector.material.ambient

		# diffuse
		L = shadowRay.direction
		cos_delta = np.dot(L, intersector.normalAt(intersection))
		if cos_delta < 0:
			cos_delta = 0
		diffuse = light.getColor() * intersector.material.diffuse * cos_delta

		# specular (blinn)
		V = Ray.fromPoints(intersection, self.eye).direction
		H = normalize(V + L)
		cos_theta = np.dot(intersector.normalAt(intersection), H)
		if cos_theta < 0:
			cos_theta = 0
		specular = light.getColor() * intersector.material.specular * math.pow(cos_theta, 10)

		return ambient + diffuse + specular


class RecursiveRayTracer(ShadingShadowRayTracer):
	MAX_DEPTH = 5

	def __init__(self, eye):
		self.eye = eye

	def trace(self, ray, objects, lights):
		return self.recursiveTrace(ray, objects, lights, 0)

	def recursiveTrace(self, ray, objects, lights, depth):
		if depth > self.MAX_DEPTH:
			return WHITE

		distances = self.distances(objects, ray)
		if abs(distances[0].distance) < EPSILON:
			nearest = distances[1]
		else:
			nearest = distances[0]

		if nearest.distance == np.inf:
			return WHITE

		intersection = ray.origin + nearest.distance * ray.direction

		# default lighting
		C = nearest.object.getColor() * nearest.object.material.ambient
		for light in lights:
			C = C + (self.shading(intersection, nearest.object, light) * self.calcShadowFactor(intersection, objects, light) * LIGHT_DAMPING**depth)

		r = min(C.r, nearest.object.getColor().r)
		g = min(C.g, nearest.object.getColor().g)
		b = min(C.b, nearest.object.getColor().b)

		C = Color(r, g, b)

		# recursive reflection computation.
		if nearest.object.material.specular > 0:
			N = nearest.object.normalAt(intersection)
			reflectionRayDirection = ray.direction - 2 * (np.dot(ray.direction, N)) * N
			reflection = Ray(intersection, reflectionRayDirection)

			recursiveValue = self.recursiveTrace(reflection, objects, lights, depth + 1)
			recursiveValue = recursiveValue * nearest.object.material.specular * LIGHT_DAMPING**depth

			C = C + recursiveValue

		# http://www.flipcode.com/archives/reflection_transmission.pdf
		# http://courses.cs.washington.edu/courses/cse457/08au/lectures/markup/ray-tracing-markup.pdf
		# maybe better: http://www.keithlantz.net/2013/03/a-basic-path-tracer-with-cuda/
		if nearest.object.material.refractive:
			normal = nearest.object.normalAt(intersection)
			minusD = ray.direction * -1

			# ray is entering object
			if np.dot(minusD, normal) > 0:
				n1 = 1.000292  # brechungsindex luft
				n2 = nearest.object.material.n
			else:  # ray is escaping object.
				n1 = nearest.object.material.n
				n2 = 1.000292

			n = n1 / n2
			cosI = np.dot(ray.direction, normal)
			sinT2 = n * n * (1.0 - cosI * cosI)

			# catch total internal reflection
			if not (sinT2 > 1.0):
				refraction = Ray(intersection, n * ray.direction - (n + np.sqrt(1.0 - sinT2)) * normal)
				value = self.recursiveTrace(refraction, objects, lights, depth + 1)

				C = C + value
		return C

class PathTracer(ShadingShadowRayTracer):
	MAX_DEPTH = 1
	RAY_PER_PIXEL = 2
	DIFFUSE_REFLECT = 5

	def trace(self, ray, objects, lights):
		C = Color(0, 0, 0)

		for i in range(self.RAY_PER_PIXEL):
			C =  C + (self.recursiveTrace(ray, objects, lights, 0) / self.RAY_PER_PIXEL)

		return C

	def recursiveTrace(self, ray, objects, lights, depth):
		if depth > self.MAX_DEPTH:
			return Color(0, 0, 0)

		distances = self.distances(objects, ray)
		if abs(distances[0].distance) < EPSILON:
			nearest = distances[1]
		else:
			nearest = distances[0]

		if nearest.distance == np.inf:
			return WHITE

		intersection = ray.origin + nearest.distance * ray.direction

		C = Color(0, 0, 0)

		# default lighting
		for light in lights:
			C = C + (self.shading(intersection, nearest.object, light) * self.calcShadowFactor(intersection, objects, light) * LIGHT_DAMPING**depth)

		r = min(C.r, nearest.object.getColor().r)
		g = min(C.g, nearest.object.getColor().g)
		b = min(C.b, nearest.object.getColor().b)

		C = Color(r, g, b)

		# recursive reflection computation.
		if nearest.object.material.specular > 0:
			N = nearest.object.normalAt(intersection)
			reflectionRayDirection = ray.direction - 2 * (np.dot(ray.direction, N)) * N
			reflection = Ray(intersection, reflectionRayDirection)

			recursiveValue = self.recursiveTrace(reflection, objects, lights, depth + 1)
			recursiveValue = recursiveValue * (nearest.object.material.specular * LIGHT_DAMPING**depth)

			C = C + recursiveValue

		if nearest.object.material.diffuse > 0:
			for c in range(self.DIFFUSE_REFLECT):
				N = nearest.object.normalAt(intersection)
				# calculate random new ray direction from hemisphere.
				# calculate random hemisphere shit in tangent space:
				# http://www.keithlantz.net/2013/03/a-basic-path-tracer-with-cuda/
				# http://www.rorydriscoll.com/2009/01/07/better-sampling/
				D_tangent_space = self.random_normal_hemisphere()

				# get local coordinate system from at normal.
				local_coord = self.local_coordinate_system_from(N, intersection)

				# transform tangent-space shit in this normal space.
				new_D = np.dot(local_coord, D_tangent_space)

				Diffuse = Ray(intersection, new_D)
				recursiveValue = self.recursiveTrace(Diffuse, objects, lights, depth+1)

				C = C + ((recursiveValue / self.DIFFUSE_REFLECT) * LIGHT_DAMPING**depth)

		return C


	def random_normal_hemisphere(self):
		from random import random

		# generate random numbers between 0.0 and 1.0.
		u1 = random()
		u2 = random()

		import math

		r = math.sqrt(u1)
		theta = 2 * math.pi * u2

		x = r * math.cos(theta)
		y = r * math.sin(theta)

		return np.array([x,y, math.sqrt(max(0.0, 1.0-u1))])

	def local_coordinate_system_from(self,N, P):
		x = N[0] +1
		y = N[1] +1
		z = N[2] -1

		ortho_N = np.cross(N, np.array([x, y, z]))

		from geometry import normalize
		axis_1 = normalize(ortho_N)
		axis_2 = normalize(np.cross(ortho_N, N))

		return np.array([axis_1, N, axis_2])

