#!/usr/bin/python

from abc import ABCMeta, abstractmethod
import math

import numpy as np

from geometry import rgb_to_hex, Ray, normalize
from color import Color


class DistanceObject:
	def __init__(self, distances, obj):
		self.distances = distances
		self.object = obj


class RayTracer:
	__metaclass__ = ABCMeta

	# returns a sorted list of tuples (distance, object)
	def distances(self, objects, ray):
		return sorted(list(self.__distancesgen(objects, ray)), key=lambda x: min(x.distances))

	def __distancesgen(self, objects, ray):
		for obj in objects:
			yield DistanceObject(obj.intersect(ray), obj)

	@abstractmethod
	def trace(self, ray, objects, lights):
		pass


class SimpleRayTracer(RayTracer):
	def trace(self, ray, objects, lights=[]):
		nearest = self.distances(objects, ray)[0]
		if min(nearest.distances) < np.inf:
			return nearest.object.getColorHex()
		else:
			return "#ffffff"


class SimpleShadowRayTracer(RayTracer):
	def trace(self, ray, objects, lights):
		nearest = self.distances(objects, ray)[0]

		if (min(nearest.distances) == np.inf):
			return "#ffffff"

		intersection = ray.origin + min(nearest.distances) * ray.direction

		S = Color(50, 50, 50)

		for light in lights:
			shadowRay = Ray.fromPoints(p1=intersection, p2=light.center)
			s_distances = self.distances(objects, shadowRay)

			if np.abs(min(s_distances[0].distances)) < 0.5:
				if len(s_distances[0].distances) == 1:
					shadownearest = min(s_distances[1].distances)
				else:
					shadownearest = s_distances[0].distances[1]
			else:
				shadownearest = min(s_distances[0].distances)

			if shadownearest > min(self.distances([light], shadowRay)[0].distances):
				S = S + light.getColor()


		r = min(S.r, nearest.object.getColor().r)
		g = min(S.g, nearest.object.getColor().g)
		b = min(S.b, nearest.object.getColor().b)

		return rgb_to_hex((r, g, b))


class ShadingShadowRayTracer(RayTracer):
	def __init__(self, eye):
		self.eye = eye

	def trace(self, ray, objects, lights):
		nearest = self.distances(objects, ray)[0]

		if (min(nearest.distances) == np.inf):
			return "#ffffff"

		intersection = ray.origin + min(nearest.distances) * ray.direction

		S = Color(20, 20, 20)

		for light in lights:
			shadowRay = Ray.fromPoints(p1=intersection, p2=light.center)
			s_distances = self.distances(objects, shadowRay)

			if min(s_distances[0].distances) < 0.1:
				shadownearest = min(s_distances[1].distances)
			else:
				shadownearest = min(s_distances[0].distances)

			if shadownearest > min(self.distances([light], shadowRay)[0].distances):
				lightPower = np.array([light.getColor().r, light.getColor().g, light.getColor().b])
				temp = self.shading(intersection, nearest.object, shadowRay, lightPower)
				S = Color(temp[0], temp[1], temp[2])

		r = min(abs(S.r), nearest.object.getColor().r)
		g = min(abs(S.g), nearest.object.getColor().g)
		b = min(abs(S.b), nearest.object.getColor().b)

		return rgb_to_hex((r, g, b))

	def shading(self, intersection, intersector, shadowRay, incoming):
		# phong-blinn shading

		# ambient
		ambient = np.array([10, 10, 10])

		# diffuse
		L = shadowRay.direction
		cos_delta = np.dot(L, intersector.normalAt(intersection))
		if (cos_delta) < 0:
			cos_delta = 0
		diffuse = incoming * 0.5 * cos_delta

		# specular (blinn)
		V = Ray.fromPoints(intersection, self.eye).direction
		H = normalize(V + L)
		cos_theta = np.dot(intersector.normalAt(intersection), H)
		if cos_theta < 0:
			cos_theta = 0
		specular = incoming * 0.5 * math.pow(cos_theta, 10)

		return ambient + diffuse + specular
