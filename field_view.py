# use black and white filter
# for field maybe only show white pixels
import cv2 as cv
import numpy as np
from video_utils import getArrayFromVideo
from sklearn.cluster import KMeans
import sys
import scipy.cluster.hierarchy as hcluster
from scipy.spatial import ConvexHull
from PIL import Image, ImageDraw
import visualize
import os
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from math import sqrt

FIELD_LINE_WIDTH = 10.16 # cm

def polygon_area(coords):
    return Polygon(coords).area


def toBlackAndWhite(img):
    gray_scale = np.dot(img[...,:3], [0.2989, 0.5870, 0.1140])
    bw = np.asarray(gray_scale).copy()
    bw[bw < 128] = 0    # Black
    bw[bw >= 128] = 255 # White
    return bw

def getCoordinates(line):
    rho, theta = line[0], line[1]
    a, b = np.cos(theta), np.sin(theta)
    x0, y0 = a*rho, b*rho
    x1, y1 = int(x0 + 1000*(-b)), int(y0 + 1000*(a))
    x2, y2 = int(x0 - 1000*(-b)), int(y0 - 1000*(a))
    return x1, y1, x2, y2

def findIntersection(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    try:
        px= ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
        py= ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
    except ZeroDivisionError:
        return False, ()
    else:
        return True, (px, py)

def isPointOnscreen(x, y, width, height):
    return x >= 0 and y >= 0 and x <= width and y <= height

def getEdgePoints(line, width, height):
    top = (0, height, width, height)
    bottom = (0, 0, width, 0)
    left = (0, 0, 0, height)
    right = (width, 0, width, height)

    onscreen_points = []
    for edge in [top, bottom, left, right]:
        intersection_exists, intersection = findIntersection(line, edge)
        if not intersection_exists: continue
        x, y = int(intersection[0]), int(intersection[1])
        if isPointOnscreen(x,y,width,height):
            point = (int(x), int(y))
            onscreen_points.append(point)
    return onscreen_points

def isPointInPoly(point, vertices):
    point = Point(point[0], point[1])
    polygon = Polygon(vertices)
    return polygon.contains(point)

def getMinMaxPoints(points):
    x_min, y_min = float("inf"), float("inf")
    x_max, y_max = 0, 0
    for x,y in points:
        x_min, y_min = min(x_min, x), min(y_min, y)
        x_max, y_max = max(x_max, x), max(y_max, y)
    return x_min, y_min, x_max, y_max

def groupLines(img, lines):

    width, height = img.shape[1], img.shape[0]


    point_to_point = {}
    point_to_line = {}
    points = []
    for line in lines:
        x1, y1, x2, y2 = line[0], line[1], line[2], line[3]
        p1, p2 = (x1,y1), (x2,y2)
        point_to_point[p1] = p2
        point_to_point[p2] = p1
        point_to_line[p1] = line
        point_to_line[p2] = line
        points.extend([p1, p2])


    clusters = hcluster.fclusterdata(points, 50, criterion="distance")
    point_groups = {} # line groups
    point_to_label = {}
    for i, label in enumerate(clusters):
        label = clusters[i]
        if label not in point_groups:
            point_groups[label] = []
        point = points[i]
        point_to_label[point] = label
        point_groups[label].append(point)

        # line = points_to_line[point]
        # groups[label].add(line)
    # print(groups)

    associations = set()
    print('1')
    unconnected_point_groups = point_groups.copy()
    while len(unconnected_point_groups) > 0:
        label, pg = unconnected_point_groups.popitem()
        connections = set()
        for point in pg:
            connected_point = point_to_point[point]
            connected_point_label = point_to_label[connected_point]
            connections.add(connected_point_label)
        if len(connections) == 1:
            try:
                associated_label = next(iter(connections))
                association = (label, associated_label)
                associations.add(association)
                unconnected_point_groups.pop(associated_label)
            except:
                to_remove = []
                for a in associations:
                    label1, label2 = a
                    if label1 == label or label2 == label:
                        to_remove.append(a)
                for a in to_remove: associations.remove(a)
                #unconnected_point_groups.pop()
        # else:
        #     for label in connections:
        #         unconnected_point_groups.pop(label)
    print('2')
    field_lines = []
    for association in associations:
        label1, label2 = association[0], association[1]
        pg1, pg2 = point_groups[label1], point_groups[label2]
        line_group = pg1 + pg2
        if len(line_group) > 2:
            hull = ConvexHull(line_group)

            #print(label1,label2, hull.simplices)
            hull_points = []


            hull_points = [line_group[v] for v in hull.vertices]
            #print('og poly', polygon_area(hull_points))
                # if x_min is None or x_min[0] > x: x_min = (x,y)
                # if y_min is None or y_min[1] > y: y_min = (x,y)
                # if x_max is None or x_max[0] < x: x_max = (x,y)
                # if y_max is None or y_max[1] < y: y_max = (x,y)
            #field_line = (x_min, y_min, x_max, y_max)

            frame = Image.new('L', (width, height), 0)
            ImageDraw.Draw(frame).polygon(hull_points, outline=1, fill=1)
            fl = np.array(frame)


            far_away = width*height
            closest_points = { hp: [far_away,()] for hp in hull_points}
            getDistance = lambda p1, p2: sqrt( (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 )
            # white_channel = 1.0 * (img > threshold)
            # white_channel = np.where(white_channel == [1,1,1], 1, 0)

            rows, cols = height, width
            for row in range(rows):
                for col in range(cols):
                    if fl[row][col] != 1: continue
                    r, g, b = img[row][col]

                    threshold = 120
                    isWhiteEnough = lambda r,g,b: r > threshold and g > threshold and b > threshold
                    if isWhiteEnough(r,g,b):
                        white_point = (col, row)
                        hp_distances = [getDistance(hp,white_point) for hp in hull_points]
                        distance_ranks = [i[0] for i in sorted(enumerate(hp_distances), key=lambda k:k[1])]
                        for rank, index in enumerate(distance_ranks):
                            hp_distance = hp_distances[index]
                            hp = hull_points[index]
                            min_distance = closest_points[hp][0]
                            if hp_distance < min_distance:
                                #print('yes', hp, hp_distance, min_distance, x, y)
                                closest_points[hp] = (hp_distance,white_point)
                                break

            fl_poly = list(map(lambda val: val[1], closest_points.values()))

            field_lines.append(fl_poly)


    # slopes = []
    # for points in field_lines:
    #     x_min, y_min, x_max, y_max = getMinMaxPoints(points)
    #     slope = (y_max-y_min)/(x_max-x_min)
    #     slopes.append(slope)

    # color_threshold = 200
    # line_groups = []
    # for fl in field_lines:
    #     lines = set()
    #     for point in fl:
    #         line = point_to_line[point]
    #         lines.add(line)
    #     line_groups.append(lines)


    return field_lines
    # line_groups = []
    # ungrouped_lines = set(lines)
    # while len(point_groups) > 0 and len(ungrouped_lines) != 0:
    #     label, point_group = point_groups.popitem()
    #     line_group = set()
    #     for point in point_group:
    #         line = point_to_line[point]
    #         if line in ungrouped_lines:
    #             line_group.add(line)
    #             ungrouped_lines.remove(line)
    #     line_groups.append(line_group)



if __name__ == '__main__':
    # edges = cv2.Canny(frame,100,200)

    #video = 'scenes/2019w3_nyj-ne/scene_0.mov'
    scene_dir = 'scenes/wentz'
    for scene_file in os.listdir(scene_dir):
        scene_path = os.path.join(scene_dir, scene_file)

        print(scene_path)
        scene = getArrayFromVideo(scene_path)
        frame = scene[0]
        height, width = frame.shape[0], frame.shape[1]

        gray = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
        edges = cv.Canny(gray,50,150,apertureSize = 3)
        lines = cv.HoughLines(edges,1,np.pi/180,200)
        line_coords = [getCoordinates(line[0]) for line in lines]
        fixed = []
        for line in line_coords:
            points = getEdgePoints(line, width, height)
            if len(points) == 2:
                p0, p1 = points[0], points[1]
                x1, y1, x2, y2 = p0[0], p0[1], p1[0], p1[1]
                # cv.line(frame,(x1,y1),(x2,y2),(255,0,0),2)
                fixed.append((x1,y1,x2,y2))
        groups = groupLines(frame, fixed)
        # field_lines = [getFieldLine(g) for g in groups if len(g)>2]

        for field_line in groups:
            # for point in field_line:
            #     print(point)
            #     cv.circle(frame, point, 3, [0,0,255])
            poly = np.array(field_line, 'int32')
            # x_min, y_min = float("inf"), float("inf")
            # x_max, y_max = 0, 0
            # for x,y in points:
            #     x_min, y_min = min(x_min, x), min(y_min, y)
            #     x_max, y_max = max(x_max, x), max(y_max, y)
            # slope = (y_max-y_min)/(x_max-x_min)
            # print(slope, x_min, x_max)

            cv.fillConvexPoly(frame, poly, [0,0,255])

        visualize.show_image(frame)
