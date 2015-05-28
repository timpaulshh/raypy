#!/usr/bin/python

from geometry import Plane


class Screen(Plane):
	def __init__(self, origin, normal, resolutionX, resolutionY, pixelSizeInWorldCoords):
		Plane.__init__(self, origin, normal)
		self.resolutionX = resolutionX
		self.resolutionY = resolutionY
		self.pixelSizeInWorldCoords = pixelSizeInWorldCoords
		self.width = resolutionX * pixelSizeInWorldCoords
		self.height = resolutionY * pixelSizeInWorldCoords

	def pixelToWorldCoord(self, pixel):
		x = self.origin[0] - self.width / 2.0 + pixel[0] * self.pixelSizeInWorldCoords
		y = self.origin[1] - self.height / 2.0 + pixel[1] * self.pixelSizeInWorldCoords
		z = self.origin[2]
		return [x, y, z]
