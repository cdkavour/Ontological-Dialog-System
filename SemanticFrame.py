from collections import defaultdict

class SemanticFrame:

	def __init__(self):
		self.Domain = None
		self.Intent = None
		self.Slots = defaultdict(lambda:None)