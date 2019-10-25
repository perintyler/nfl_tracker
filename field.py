
import numpy as np

from fieldlines import findFieldLines
from hashmarks import findHashMarks
from boundaries import findBoundaries
from players import findPlayers
from field_model import 




class Field:

    def __init__(self, image):
    	self.image = image
    	fieldlines, hashmarks, fieldNumbers = findFieldMarkings(image)
    	self.boundaries = findBoundaries(fieldlines, hashmarks, fieldNumbers)

    def getPlayerLocation(self,x,y): 
    	return


    def findPlayers(self):
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



