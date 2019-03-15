

def getEnumString(c, enum):
	"""extract enum string given the enum integer from an enum-only class"""
	for s in c.__dict__.keys():
		if c.__dict__[s] == enum:
			return s
	return "<UNKNOWN>"
