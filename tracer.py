#!/usr/bin/python

from abc import ABCMeta, abstractmethod
import numpy as np

class RayTracer:
	__metaclass__ = ABCMeta

	# returns a sorted list of tuples (distance, object)
	def distances(self, objects, ray):
		return sorted(list(self.__distancesgen(objects, ray)), key=lambda x: x[0])
			
	def __distancesgen(self, objects, ray):
		for obj in objects:
			yield (obj.intersect(ray), obj)

	@abstractmethod
	def trace(self, ray, objects):
		pass

class SimpleRayTracer(RayTracer):
	def trace(self, ray, objects):
		nearest = self.distances(objects, ray)[0]
		if min(nearest[0]) < np.inf:
			return nearest[1].getColorHex()
		else:
			return "#ffffff"