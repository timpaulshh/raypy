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

		from multiprocessing.queues import SimpleQueue
		q2 = SimpleQueue() # in this case yolo.

		from processes import BlockProcess

		threads = BlockProcess.forCount(processCount, self.width, self.height, self.tracer, self.scene, q2)

		startTime = time.time()

		print "Starting Processes..."
		for t in threads:
			t.start()
		print "Finished"

		count_finished = 0
		drawn = 0
		draw = ImageDraw.Draw(img)

		while count_finished < processCount:
			info = q2.get()

			if info == "finished.":
				count_finished = count_finished+1
			else:
				draw.point(info[0], fill=info[1])
				drawn = drawn+1
			
			progress = drawn / float(self.width*self.height)

			timeString = ""
			if progress > 0:
				passedTime = time.time() - startTime
				estimatedTime = passedTime / progress - passedTime
				timeString = "\tRemaining time: %2.2fs" % (estimatedTime)

			sys.stdout.write("Progress: %2.2f%% %s        \r" % (progress * 100, timeString))
			sys.stdout.flush()

		print "Joining Processes..."
		for t in threads:
			t.join()
		print "Finished"
			
		img.save(fileName + ".png", format="png")
