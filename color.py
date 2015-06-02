class Color:
	def __init__(self,r ,g , b):
		self.r = r
		self.g = g
		self.b = b

	def __add__(self, other):
		return Color(self.r + other.r, self.g + other.g, self.b + other.b)

	def __sub__(self, other):
		return Color(self.r - other.r, self.g - other.g, self.b - other.b)


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
