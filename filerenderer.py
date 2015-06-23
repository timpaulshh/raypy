from PIL import Image, ImageDraw
from geometry import Ray

class FileRenderer():
	def __init__(self, width, height, tracer, scene):
		self.width = width
		self.height = height
		self.tracer = tracer
		self.scene = scene

	def render(self, fileName):
		import sys, time
		img = Image.new("RGB", (self.width, self.height))

		processCount = 4

		from multiprocessing import Queue
		q1 = Queue()
		q2 = Queue() # in this case yolo.

		from processes import BlockProcess

		threads = BlockProcess.forCount(processCount, self.width, self.height, self.tracer, self.scene, q2, q1)

		startTime = time.time()

		print "Starting Processes..."
		for t in threads:
			t.start()
		print "Finished"

		count_finished = 0
		drawn = 0
		draw = ImageDraw.Draw(img)

		while count_finished < processCount:
			progress = q2.qsize() / float(self.width*self.height)

			timeString = ""
			if progress > 0:
				passedTime = time.time() - startTime
				estimatedTime = passedTime / progress - passedTime
				timeString = "\tRemaining time: %2.2fs" % (estimatedTime)

			sys.stdout.write("Progress: %2.2f%% %s        \r" % (progress * 100, timeString))
			sys.stdout.flush()

			import Queue
			try:
				info = q1.get(timeout=1)
				if info == "finished.":
					count_finished = count_finished+1
			except Queue.Empty:
				continue;

		while not q2.empty():
			info = q2.get()
			draw.point(info[0], fill=info[1])

		print "Joining Processes..."
		for t in threads:
			t.join()
		print "Finished"
			
		img.save(fileName + ".png", format="png")
