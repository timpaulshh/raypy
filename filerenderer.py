from PIL import Image, ImageDraw
from geometry import Ray

class FileRenderer():
	def __init__(self, width, height, tracer, scene):
		self.width = width
		self.height = height
		self.tracer = tracer
		self.scene = scene

	def render(self, fileName):
		import sys
		img = Image.new("RGB", (self.width, self.height))
		draw = ImageDraw.Draw(img)

		for x in range(self.width):
			for y in range(self.height):
				R = Ray.fromPoints(p1=self.scene.eye, p2=self.scene.screen.pixelToWorldCoord((x,y)))
				C = self.tracer.trace(R, self.scene.geometry, self.scene.lights).toHex()
				draw.point((x,y), fill=C)
				sys.stdout.write("Progress: %2.2f%%\r"%(x*float(self.width)+y) / (self.width * self.height))
				sys.stdout.flush()

		img.save(fileName + ".png", format="png")
