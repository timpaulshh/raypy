#!/usr/bin/python

from abc import ABCMeta, abstractmethod
import numpy as np

class RayTracer:
	__metaclass__ = ABCMeta

	@abstractmethod
	def trace(self, ray, objects):
		pass

class SimpleRayTracer(RayTracer):
	def __init__(self):
		pass
		
	# returns a sorted list of tuples (distance, object)
	def __distances(self, objects, ray):
		return sorted(list(self.__distancesgen(objects, ray)), key=lambda x: x[0])
			
	def __distancesgen(self, objects, ray):
		for obj in objects:
			yield (obj.intersect(ray), obj)
	
	def trace(self, ray, objects):
		nearest = self.__distances(objects, ray)[0]
		if min(nearest[0]) < np.inf:
			return nearest[1].getColorHex()
		else:
			return "#ffffff"