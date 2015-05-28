#!/usr/bin/python

from abc import ABCMeta, abstractmethod
import numpy as np
from geometry import rgb_to_hex, Ray

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
	def trace(self, ray, objects, lights = []):
		nearest = self.distances(objects, ray)[0]
		if min(nearest.distance) < np.inf:
			return nearest.object.getColorHex()
		else:
			return "#ffffff"

class SimpleShadowRayTracer(RayTracer):
	def trace(self, ray, objects, lights):
		nearest = self.distances(objects, ray)[0]

		if (min(nearest.distances) == np.inf):
			return "#ffffff"

		intersection = ray.origin + min(nearest.distances) * ray.direction

		sr = 0
		sg = 0
		sb = 0

		for light in lights:
			shadowRay = Ray(p1 = intersection, p2 = light.center)
			s_distances = self.distances(objects, shadowRay)

			if min(s_distances[0].distances) < 0.01:
				shadownearest = s_distances[1]			
			else:
				shadownearest = s_distances[0]

			if min(shadownearest.distances) > min(self.distances([light], shadowRay)[0].distances):
				sr = min(sr + light.getColor()[0], 255)
				sg = min(sg + light.getColor()[1], 255)
				sb = min(sb + light.getColor()[2], 255)

		r = min(sr, nearest.object.getColor()[0])
		g = min(sg, nearest.object.getColor()[1])
		b = min(sb, nearest.object.getColor()[2])

		return rgb_to_hex((r, g, b))
