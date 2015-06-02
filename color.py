class Color:
	def __init__(self,r ,g , b):
		self.r = r
		self.g = g
		self.b = b

	def __add__(self, other):
		r = min(self.r + other.r, 255)
		g = min(self.g + other.g, 255)
		b = min(self.b + other.b, 255)

		return Color(r, g, b)

	def __sub__(self, other):
		r = max(self.r - other.r, 0)
		g = max(self.g - other.g, 0)
		b = max(self.b - other.b, 0)

		return Color(r, g, b)

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
