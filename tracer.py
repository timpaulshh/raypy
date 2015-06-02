#!/usr/bin/python

from abc import ABCMeta, abstractmethod
import math

import numpy as np

from geometry import Ray, normalize
from material import Color, WHITE


class DistanceObject:
	def __init__(self, distance, obj):
		self.distance = distance
		self.object = obj


class RayTracer:
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


class SimpleRayTracer(RayTracer):
	def shading(self, intersection, intersector, shadowRay, incoming):
		return intersector.getColor()

	def trace(self, ray, objects, lights=[]):
		nearest = self.distances(objects, ray)[0]
		if nearest.distance < np.inf:
			return self.shading(None, nearest.object, None, lights)
		else:
			return WHITE


class SimpleShadowRayTracer(RayTracer):
	def shading(self, intersection, intersector, shadowRay, incoming):
		ambient = intersector.getColor() * intersector.material.ambient
		diffuse = intersector.getColor() * intersector.material.diffuse
		specular = intersector.getColor() * intersector.material.specular

		return ambient + diffuse + specular

	def trace(self, ray, objects, lights):
		distances = self.distances(objects, ray)
		nearest = distances[0]

		# nothing is hit.
		if nearest.distance == np.inf:
			return WHITE.toHex()

		# ambient color of nearest
		C = nearest.object.getColor() * nearest.object.material.ambient

		intersection = ray.origin + nearest.distance * ray.direction

		for light in lights:
			# calculate ray from intersection towards the light
			shadowRay = Ray.fromPoints(p1=intersection, p2=light.center)

			shadowDistances = self.distances(objects, shadowRay)

			# if the distance is too low, it is most likely an intersection with the intersection
			# thanks to floating point inaccuracy.
			if shadowDistances[0].distance < 0.1:
				shadowNearest = shadowDistances[1]  # why the fuck does this not work?!
			else:
				shadowNearest = shadowDistances[0]

			lightDistance = self.distances([light], shadowRay)[0].distance

			# if the nearest intersection is in a higher or equal distance to the light, than
			# the distance from this point to the light, then there is nothing in between.
			if shadowNearest.distance >= lightDistance:
				C = C + self.shading(intersection, nearest.object, shadowRay, light.getColor())

		return C


# @todo: still is not stable for more than one light-source
class ShadingShadowRayTracer(RayTracer):
	def __init__(self, eye):
		self.eye = eye

	def trace(self, ray, objects, lights):
		distances = self.distances(objects, ray)
		nearest = distances[0]

		# nothing is hit.
		if nearest.distance == np.inf:
			return WHITE.toHex()

		# ambient color of nearest
		C = nearest.object.getColor() * nearest.object.material.ambient

		intersection = ray.origin + nearest.distance * ray.direction

		for light in lights:
			# calculate ray from intersection towards the light
			shadowRay = Ray.fromPoints(p1=intersection, p2=light.center)

			shadowDistances = self.distances(objects, shadowRay)

			# if the distance is too low, it is most likely an intersection with the intersection
			# thanks to floating point inaccuracy.
			if shadowDistances[0].distance < 0.1:
				shadowNearest = shadowDistances[2]  # this still is not correct. wtf does it not work with index 1?!
			else:
				shadowNearest = shadowDistances[0]

			lightDistance = self.distances([light], shadowRay)[0].distance

			# if the nearest intersection is in a higher or equal distance to the light, than
			# the distance from this point to the light, then there is nothing in between.
			if shadowNearest.distance > lightDistance:
				C = C + self.shading(intersection, nearest.object, shadowRay, light.getColor())

		r = min(C.r, nearest.object.getColor().r)
		g = min(C.g, nearest.object.getColor().g)
		b = min(C.b, nearest.object.getColor().b)

		return Color(r, g, b)

	def shading(self, intersection, intersector, shadowRay, incoming):
		# phong-blinn shading

		# ambient
		ambient = intersector.getColor() * intersector.material.ambient

		# diffuse
		L = shadowRay.direction
		cos_delta = np.dot(L, intersector.normalAt(intersection))
		if cos_delta < 0:
			cos_delta = 0
		diffuse = incoming * intersector.material.diffuse * cos_delta

		# specular (blinn)
		V = Ray.fromPoints(intersection, self.eye).direction
		H = normalize(V + L)
		cos_theta = np.dot(intersector.normalAt(intersection), H)
		if cos_theta < 0:
			cos_theta = 0
		specular = incoming * intersector.material.specular * math.pow(cos_theta, 10)

		return ambient + diffuse + specular


class RecursiveRayTracer(RayTracer):
	MAX_DEPTH = 5

	def trace(self, ray, objects, lights):
		return self.recursiveTrace(ray, objects, lights, 0)

	def recursiveTrace(self, ray, objects, lights, depth):
		if depth > self.MAX_DEPTH:
			return WHITE

		nearest = self.distances(objects, ray)[0]

		if nearest.distance == np.inf:
			return WHITE

		intersection = ray.origin + nearest.distance * ray.direction
		C = self.accLightSources(intersection, nearest.object, objects, lights)

		# recursive reflection computation.
		if nearest.object.material.specular > 0:
			N = nearest.object.normalAt(intersection)
			reflectionRayDirection = ray.direction - 2 * (np.dot(ray.direction, N)) * N
			reflection = Ray(intersection, reflectionRayDirection)

			recursiveValue = self.recursiveTrace(reflection, objects, lights, depth + 1)
			recursiveValue = recursiveValue * nearest.object.material.specular

			C = C + recursiveValue

		r = min(C.r, nearest.object.getColor().r)
		g = min(C.g, nearest.object.getColor().g)
		b = min(C.b, nearest.object.getColor().b)

		return Color(r, g, b)

	def accLightSources(self, intersection, intersector, objects, lights):
		C = intersector.getColor() * intersector.material.ambient

		for light in lights:
			shadowRay = Ray.fromPoints(p1=intersection, p2=light.center)
			shadowDistances = self.distances(objects, shadowRay)

			# if the distance is too low, it is most likely an intersection with the intersection
			# thanks to floating point inaccuracy.
			if shadowDistances[0].distance < 0.1:
				shadowNearest = shadowDistances[2]  # why the fuck does this not work with 1?!
			else:
				shadowNearest = shadowDistances[0]

			if shadowNearest > self.distances([light], shadowRay)[0].distance:
				C = C + light.getColor()

		r = min(C.r, intersector.getColor().r)
		g = min(C.g, intersector.getColor().g)
		b = min(C.b, intersector.getColor().b)

		return Color(r, g, b)
