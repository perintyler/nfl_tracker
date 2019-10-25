from video_utils import getArrayFromVideo

import numpy as np
import cv2 as cv

import line

import visualize
from file_utils import iterateScenes

'''
TODO 
    - Convert all lines to FieldLine objects
    - clean up nonsensical poorly named variable code

https://www.pyimagesearch.com/2016/04/04/measuring-distance-between-objects-in-an-image-with-opencv/
edged = cv2.Canny(gray, 50, 100)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)
'''

class FieldLineDetectionError(Exception):

    def __init__(self):
        Exception.__init__(self, 'Could not find field lines')

class FieldLine:

    def __init__(self, coordinates):
        p0, p1 = coordinates
        x0, y0 = p0 
        x1, y1 = p1
        self.next_line = None
        self.setCoordinates(x0, y0, x1, y1)


    def getCoordinates(self):
        return self.x0,self.y0,self.x1,self.y1

    # def getMidwayPoint(self):
    #     x = (self.x0 + self.x1) / 2
    #     y = (self.y0 + self.y1) / 2
    #     return (x,y)

    def setCoordinates(self, x0, y0, x1, y1):
        p0, p1 = (x0,y0), (x1,y1)
        bottom_point = p0 if y0 < y1 else p1 
        top_point = p0 if bottom_point == p1 else p1
        self.x0, self.y0 = bottom_point
        self.x1, self.y1 = top_point


    def getSlope(self):
        return (self.y1-self.y0)/(self.x1-self.x0)
    

    def makeAdjustments(self, brightness):
        # adjust coordinates by finding brightest point in its area
        ax0, ay0 = self._adjustPoint(self.x0, self.y0, brightness)
        ax1, ay1 = self._adjustPoint(self.x1, self.y1, brightness)
        # use the found adjusted coordinates to reset coordinates
        self.setCoordinates(ax0, ay0, ax1, ay1)

    def _adjustPoint(self, x, y, brightness):
        height, width = brightness.shape
        adjustment_range = 20

        line_distance = 15
        slope = self.getSlope()
        dx, dy = line.getdxdy(line_distance, slope)
        adjusted_x, adjusted_y = x, y
        if y < height/2 and slope > 0 or y > height/2 and slope < 0:
            adjusted_x += dx
            adjusted_y += dy
        else:
            adjusted_x -= dx
            adjusted_y -= dy

        adjusted_x, adjusted_y = int(adjusted_x), int(adjusted_y)

        adjustment_is_onscreen = x >= 0 and y >= 0 and x < width and y < height
        if adjustment_is_onscreen:
            x,y = adjusted_x, adjusted_y 

        start, end = int(x - adjustment_range/2), int(x + adjustment_range/2)
        brightest_x, brightest_val = x, brightness[y][x]

        for x_search in range(start, end):
            if x_search >= width: break
            search_brightness = brightness[y][x_search]
            if search_brightness > brightest_val:
                brightest_val = search_brightness
                brightest_x = x_search
        adjusted_point = (brightest_x, y)
        return adjusted_point

    def getBottomPoint(self):
        return (self.x0, self.y0)

    def getTopPoint(self):
        return (self.x1, self.y1)

    def draw(self, image, color=[0,0,255], thickness=1):
        p0, p1 = (self.x0, self.y0), (self.x1, self.y1)
        cv.line(image, p0, p1, color, thickness)

    def hasNextLine(self):
        return self.next_line != None

    def getNextLine(self):
        return self.next_line

    @staticmethod
    def sort(field_lines): 
        sorted_lines = sorted(field_lines, key=lambda fl: fl.x0)
        for i in range(0, len(sorted_lines)-1):
            fl1, fl2 = sorted_lines[i], sorted_lines[i+1]
            fl1.next_line = fl2
        return sorted_lines


def filterLines(lines):
    filtered = []
    for l in lines:
        x0, y0, x1, y1 = l 
        if x1 - x0 != 0 and y1 - y0 != 0:
            filtered.append(l)
    return filtered

'''This should always be called to create field lines because it sets up the linked_list 
among field lines allowing access to the field lines in order.'''
def createFieldLines(coordinates, image):
    # create brightness array which is used to make small adjustments to field line coordinates
    no_green = image.copy()
    no_green[:,:,1] = 0
    brightness = np.mean(no_green, axis=2)

    field_lines = []
    for line in coordinates:
        # create the field line using the coordinates and adjust the coordinate using brightness
        fl = FieldLine(line)
        fl.makeAdjustments(brightness)
        field_lines.append(fl)

    field_lines = FieldLine.sort(field_lines)
    # for i in range(1,len(field_lines)):
    #     fl1, fl2 = field_lines[i-1], field_lines[i]
    #     fl1.next_line = fl2
    #     fl2.last_line = fl1

    return field_lines


def findFieldLines(image):

    height, width = image.shape[0], image.shape[1]

    detected_lines = line.detect(image)
    filtered_lines = filterLines(detected_lines)
    framed_lines = [line.fitToFrame(l, width, height) for l in filtered_lines]
    lines_to_group = [l for l in framed_lines if len(framed_lines) != 0]
    grouped_lines = line.group(lines_to_group, width, height)
    field_lines = createFieldLines(grouped_lines, image)
    return field_lines


if __name__ == '__main__':
    scenes_dir = 'scenes/overhead'
    def drawFieldLines(video_path):
        print(f'showing {video_path}')
        video = getArrayFromVideo(video_path)
        frame = video[0]
        field_lines = findFieldLines(frame)
        for fl in field_lines:
            print(fl.getCoordinates(), f'slope: {fl.getSlope()}')
            fl.draw(frame)
        visualize.show_image(frame)
    iterateScenes(scenes_dir, drawFieldLines)

