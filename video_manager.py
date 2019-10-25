import skvideo.io

class VideoManager:


	def __init__(self, path):
		self.path = path
		self.frames = skvideo.io.vread(path)

	def getFrame(self, frame_number):
		return self.frames[frame_number]