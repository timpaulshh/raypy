import multiprocessing

class BlockProcess(multiprocessing.Process):
	def __init__(self, y_s, y_e, width, tracer, scene, f_queue):
		multiprocessing.Process.__init__(self)
		self.y_s = y_s
		self.y_e = y_e
		self.tracer = tracer
		self.scene = scene
		self.width = width
		self.f_queue = f_queue

	def run(self):
		from geometry import Ray
		for y in range(self.y_s, self.y_e):
			for x in range(self.width):
				R = Ray.fromPoints(p1=self.scene.eye, p2=self.scene.screen.pixelToWorldCoord((x, y)))
				C = self.tracer.trace(R, self.scene.geometry, self.scene.lights).toHex()
				self.f_queue.put(((x,y), C))
		self.f_queue.put("finished.")

	@classmethod
	def forCount(cls, processCount, width, height, tracer, scene, queue):
		return [cls(y * height/processCount, (y+1) * height/processCount, width, tracer, scene, queue) for y in range(processCount)]