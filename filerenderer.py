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

		processcount = 4

		from multiprocessing.queues import SimpleQueue
		q2 = SimpleQueue() # in this case yolo.

		from processes import BlockProcess

		threads = BlockProcess.forCount(4, self.width, self.height, self.tracer, self.scene, q2)
		count = len(threads)
		print count

		print "Starting Processes..."
		for t in threads:
			t.start()
		print "Finished"

		count_finished = 0
		drawn = 0
		draw = ImageDraw.Draw(img)

		while count_finished < count:
			info = q2.get()

			if info == "finished.":
				count_finished = count_finished+1
			else:
				draw.point(info[0], fill=info[1])
				drawn = drawn+1
			
			sys.stdout.write("Progress: %2.2f%%\r" % (drawn / float(self.width*self.height) * 100))
			sys.stdout.flush()

		print "Joining Processes..."
		for e,t in enumerate(threads):
			t.join()
		print "Finished"
			
		img.save(fileName + ".png", format="png")
