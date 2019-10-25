import os

def iterateScenes(dir, func):
	for filename in os.listdir(dir):
		path = os.path.join(dir, filename)
		func(path)


def getPaths(dir):
	return list(map(lambda fn: os.path.join(dir, fn)))