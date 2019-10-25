
import numpy as np

from fieldlines import findFieldLines
from hashmarks import findHashMarks
from boundaries import findBoundaries
from players import findPlayers
from field_model import 

'''
I'm thinking this class takes in the image, does all image processing shit, then all the 
field line and hash mark finding can somehow access those processed images. maybe by 
passing the field object into the search functions. Maybe create a class that stores 
all image filters and that can be passed through all of the search functions. TBD
'''



class Field:

    def __init__(self, image):
    	self.image = image
    	fieldlines, hashmarks, fieldNumbers = findFieldMarkings(image)
    	self.boundaries = findBoundaries(fieldlines, hashmarks, fieldNumbers)

    def performImageProcessing(self):
    	return


    def saveToFile(self, path=None):
    	return

    '''
    Uses the next frame in the video to return the new/updated field
    '''
    def update(self, image):
        return # returns a field


    def saveToFile(self):
    	return



