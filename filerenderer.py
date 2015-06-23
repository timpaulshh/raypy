from PIL import Image, ImageDraw
from geometry import Ray

class FileRenderer():
	RENDER_PROCESSES = 4

	def __init__(self, width, height, tracer, scene):
		self.width = width
		self.height = height
		self.tracer = tracer
		self.scene = scene

	def render(self, fileName):
		import sys, time
		img = Image.new("RGB", (self.width, self.height))

		from multiprocessing import Queue
		finishedQueue = Queue()
		dataQueue = Queue() # in this case yolo.

		from processes import BlockProcess

		threads = BlockProcess.forCount(self.RENDER_PROCESSES, self.width, self.height, self.tracer, self.scene, dataQueue, finishedQueue)

		startTime = time.time()

		print "Starting Processes..."
		for t in threads:
			t.start()

		count_finished = 0
		drawn = 0
		draw = ImageDraw.Draw(img)

		while count_finished < self.RENDER_PROCESSES:
			progress = dataQueue.qsize() / float(self.width*self.height)

			timeString = ""
			if progress > 0:
				passedTime = time.time() - startTime
				estimatedTime = passedTime / progress - passedTime
				timeString = "\tRemaining time: %02dm %02ds" % (divmod(estimatedTime, 60))

			sys.stdout.write("Progress: %2.2f%% %s          \r" % (progress * 100, timeString))
			sys.stdout.flush()

			import Queue
			try:
				info = finishedQueue.get(timeout=1)
				if info == "finished.":
					count_finished = count_finished+1
			except Queue.Empty:
				continue;

		while not dataQueue.empty():
			info = dataQueue.get()
			draw.point(info[0], fill=info[1])

		print "Saving to file..."
		img.save(fileName + ".png", format="png")

		print "Joining Processes..."
		for t in threads:
			t.join()
		print "Finished in %02dm %02ds"%(divmod(time.time()-startTime, 60))