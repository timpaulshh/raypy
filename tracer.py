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

	def distanceBetween(self, p1, p2):
		from geometry import vector_length

		path = p2 - p1
		return vector_length(path)

	def lightAttenuation2(self, distance):
		if distance < 0.001:
			return 1

		# empirisch ermittelte konstanten!
		a = 0
		b = 0
		c = 0.5

		return 1.0 / (a + b*distance + c*distance*distance)

	def lightAttenuation(self, intersection, light):
		distance = self.distanceBetween(intersection, light.center)
		return self.lightAttenuation2(distance)

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
		attenuation = self.lightAttenuation(intersection, light)
		ambient = intersector.getColor() * intersector.material.ambient
		diffuse = intersector.getColor() * intersector.material.diffuse * attenuation
		specular = intersector.getColor() * intersector.material.specular * attenuation

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

		return C

	def shading(self, intersection, intersector, light):
		attenuation = self.lightAttenuation(intersection=intersection, light=light)
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
		diffuse = diffuse * attenuation

		# specular (blinn)
		V = Ray.fromPoints(intersection, self.eye).direction
		H = normalize(V + L)
		cos_theta = np.dot(intersector.normalAt(intersection), H)
		if cos_theta < 0:
			cos_theta = 0
		specular = light.getColor() * intersector.material.specular * math.pow(cos_theta, 10)
		specular = specular * attenuation

		return ambient + diffuse + specular


class RecursiveRayTracer(ShadingShadowRayTracer):
	MAX_DEPTH = 5

	def __init__(self, eye):
		self.eye = eye

	def trace(self, ray, objects, lights):
		return self.recursiveTrace(ray, objects, lights, 0, 0)

	def recursiveTrace(self, ray, objects, lights, depth, distance):
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
			C = C + (self.shading(intersection, nearest.object, light) * self.calcShadowFactor(intersection, objects, light))

		# recursive reflection computation.
		if nearest.object.material.specular > 0:
			N = nearest.object.normalAt(intersection)
			reflectionRayDirection = ray.direction - 2 * (np.dot(ray.direction, N)) * N
			reflection = Ray(intersection, reflectionRayDirection)

			recursiveValue = self.recursiveTrace(reflection, objects, lights, depth + 1, distance + nearest.distance)
			recursiveValue = recursiveValue * nearest.object.material.specular
			recursiveValue = recursiveValue * self.lightAttenuation2(distance=distance)

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
				value = self.recursiveTrace(refraction, objects, lights, depth + 1, distance + nearest.distance)

				C = C + value
		return C

class PathTracer(ShadingShadowRayTracer):
	MAX_DEPTH = 1
	RAY_PER_PIXEL = 8
	DIFFUSE_REFLECT = 10

	def trace(self, ray, objects, lights):
		C = Color(0, 0, 0)

		for i in range(self.RAY_PER_PIXEL):
			C =  C + (self.recursiveTrace(ray, objects, lights, 0, 0) / self.RAY_PER_PIXEL)

		return C

	def recursiveTrace(self, ray, objects, lights, depth, distance):
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

		A = nearest.object.getColor() * nearest.object.material.ambient
		C = nearest.object.getColor() * nearest.object.material.ambient

		# default lighting
		for light in lights:
			C = C + (self.shading(intersection, nearest.object, light) * self.calcShadowFactor(intersection, objects, light))

		# recursive reflection computation.
		if nearest.object.material.specular > 0:
			N = nearest.object.normalAt(intersection)
			reflectionRayDirection = ray.direction - 2 * (np.dot(ray.direction, N)) * N
			reflection = Ray(intersection, reflectionRayDirection)

			recursiveValue = self.recursiveTrace(reflection, objects, lights, depth + 1, distance + nearest.distance)
			recursiveValue = recursiveValue * (nearest.object.material.specular)
			recursiveValue = recursiveValue * self.lightAttenuation2(distance)

			C = C + recursiveValue

		if nearest.object.material.diffuse > 0:
			for c in range(self.DIFFUSE_REFLECT):
				N = nearest.object.normalAt(intersection)
				# calculate random new ray direction from hemisphere.
				# calculate random hemisphere shit in tangent space:
				# http://www.keithlantz.net/2013/03/a-basic-path-tracer-with-cuda/
				# http://www.rorydriscoll.com/2009/01/07/better-sampling/
				#D_tangent_space = self.random_normal_hemisphere()

				## get local coordinate system from at normal.
				#local_coord = self.local_coordinate_system_from(N)

				## transform tangent-space shit in this normal space.
				#new_D = np.dot(local_coord, D_tangent_space)

				from random import uniform
				new_D = np.array([uniform(-1, 1), uniform(-1, 1), uniform(-1, 1)])

				Diffuse = Ray(intersection, new_D)
				recursiveValue = self.recursiveTrace(Diffuse, objects, lights, depth+1, distance + nearest.distance)
				recursiveValue = recursiveValue / self.DIFFUSE_REFLECT
				recursiveValue = recursiveValue * self.lightAttenuation2(distance)

				C = C + recursiveValue

		return C


	def random_normal_hemisphere(self):
		from random import random

		# generate random numbers between 0.0 and 1.0.
		u1 = random()
		u2 = random()

		import math

		r = math.sqrt(1 - u1 * u1)
		phi = 2 * math.pi * u2

		x = r * math.cos(phi)
		z = r * math.sin(phi)

		return np.array([x, u1, z])

	def local_coordinate_system_from(self, N):
		x = N[0] +1
		y = N[1] +1
		z = N[2] -1

		ortho_N = np.cross(N, np.array([x, y, z]))

		from geometry import normalize
		axis_1 = normalize(ortho_N)
		axis_2 = normalize(np.cross(ortho_N, N))

		return np.array([axis_1, N, axis_2])
