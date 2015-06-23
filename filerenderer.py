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
		q2 = Queue() # in this case yolo.

		threads = [BlockProcess(y * self.height/4, (y+1) * self.height/4, self.width, self.tracer, self.scene, q, q2) for y in range(4)]
		count = len(threads)

		for t in threads:
			t.start()

		while not q.full():
			import time
			sys.stdout.write("Progress: %2.2f%%\r" % (q.qsize() / float(self.width*self.height) * 100))
			sys.stdout.flush()
			time.sleep(1)

		print "Exit While."

		draw = ImageDraw.Draw(img)

		while not q2.empty():
			info = q2.get()
			draw.point(info[0], fill=info[1])

		img.save(fileName + ".png", format="png")
		exit(0)

import multiprocessing

class BlockProcess(multiprocessing.Process):
	def __init__(self, y_s, y_e, width, tracer, scene, queue, f_queue):
		multiprocessing.Process.__init__(self)
		self.y_s = y_s
		self.y_e = y_e
		self.tracer = tracer
		self.scene = scene
		self.width = width
		self.queue = queue
		self.f_queue = f_queue

	def run(self):
		for y in range(self.y_s, self.y_e):
			for x in range(self.width):
				R = Ray.fromPoints(p1=self.scene.eye, p2=self.scene.screen.pixelToWorldCoord((x, y)))
				C = self.tracer.trace(R, self.scene.geometry, self.scene.lights).toHex()
				self.f_queue.put_nowait(((x,y), C))
				self.queue.put_nowait(1)
		print "Thread finished!"

