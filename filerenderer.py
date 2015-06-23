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

		from multiprocessing import Queue
		q = Queue(maxsize=self.width * self.height)

		threads = [BlockProcess(y * self.height/4, (y+1) * self.height/4, self.width, self.tracer, self.scene, ImageDraw.Draw(img), q) for y in range(4)]

		for t in threads:
			t.start()

		while not q.full():
			import time
			sys.stdout.write("Progress: %2.2f%%\r" % (q.qsize() / float(self.width*self.height) * 100))
			sys.stdout.flush()
			time.sleep(1)

		for t in threads:
			t.join()

		img.save(fileName + ".png", format="png")


import multiprocessing

class BlockProcess(multiprocessing.Process):
	def __init__(self, y_s, y_e, width, tracer, scene, draw, queue):
		multiprocessing.Process.__init__(self)
		self.y_s = y_s
		self.y_e = y_e
		self.tracer = tracer
		self.scene = scene
		self.draw = draw
		self.width = width
		self.queue = queue

	def run(self):
		for y in range(self.y_s, self.y_e):
			for x in range(self.width):
				R = Ray.fromPoints(p1=self.scene.eye, p2=self.scene.screen.pixelToWorldCoord((x, y)))
				C = self.tracer.trace(R, self.scene.geometry, self.scene.lights).toHex()
				self.draw.point((x, y), fill=C)
				self.queue.put_nowait(1)

