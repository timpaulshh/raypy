import numpy as np

class Color:
	def __init__(self, r, g, b):
		self.rgb = np.clip(np.array([r, g, b]), 0, 255)
		self.r = self.rgb[0]
		self.g = self.rgb[1]
		self.b = self.rgb[2]

	@classmethod
	def fromNp(cls, array):
		return cls(array[0], array[1], array[2])

	def __add__(self, other):
		return Color.fromNp(self.rgb + other.rgb)

	def __sub__(self, other):
		return Color.fromNp(self.rgb - other.rgb)

	def __mul__(self, scalar):
		return Color.fromNp(self.rgb * scalar)

	def __div__(self, scalar):
		return Color.fromNp(self.rgb / scalar)

	def toHex(self):
		return "#%02x%02x%02x" % (self.r, self.g, self.b)


if __name__ == "__main__":
	a = Color(100, 100, 100)
	b = Color(50, 50, 50)

	c = a + b
	assert(c.r == a.r + b.r)
	assert(c.g == a.g + b.g)
	assert(c.b == a.b + b.b)

	c = a - b
	assert(c.r == a.r - b.r)
	assert(c.g == a.g - b.g)
	assert(c.b == a.b - b.b)

	d = Color(200, 200, 200) + Color(200, 200, 200)
	assert(d.r == 255)
	assert(d.g == 255)
	assert(d.b == 255)

	e = Color(10, 10, 10) - Color(200, 200, 200)
	assert(e.r == 0)
	assert(e.g == 0)
	assert(e.b == 0)

	f = Color(10, 10, 10) * 5
	assert(f.r == 50)
	assert(f.g == 50)
	assert(f.b == 50)

	g = Color(50, 50, 50) / 5
	assert(g.r == 10)
	assert(g.g == 10)
	assert(g.b == 10)