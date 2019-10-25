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
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract as tes
from skimage.draw import line_aa

FIELD_LINE_WIDTH = 10.16 # cm

def getTopBottom(p0,p1):
    p0_y, p1_y = p0[1], p1[1]
    top = p0 if p0_y > p1_y else p1
    bottom = p0 if p0_y < p1_y else p1
    return top, bottom

def getLineSlope(p0, p1):
    top, bottom = getTopBottom(p0,p1)
    return (top[1]-bottom[1])/(top[0]-bottom[0])

def getSlopeOutlier(field_lines):
    getSlope = lambda p0, p1: (p1[1]-p0[1])/(p1[0]-p0[0])
    slopes = []
    for fl in field_lines:
        p0, p1 = fl
        top, bottom = getTopBottom(p0,p1)
        slope = getSlope(top, bottom)
        slopes.append(slope)

    std = np.std(slopes)
    std_cutoff = 10
    if std > std_cutoff:
        outlier_cutoff = 2 * std
        isOutlier = lambda slope: abs(slope - std) > outlier_cutoff
        field_lines = [field_lines[i] for i, slope in enumerate(slopes) if not isOutlier(slope)]
    return field_lines




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
    return x >= 0 and y >= 0 and x < width and y < height

def getEdgePoints(line, width, height):
    max_x, max_y = width-1, height-1
    top = (0, max_y, max_x, max_y)
    bottom = (0, 0, max_x, 0)
    left = (0, 0, 0, max_y)
    right = (max_x, 0, max_x, max_y)

    onscreen_points = []
    for edge in [top, bottom, left, right]:
        intersection_exists, intersection = findIntersection(line, edge)
        if not intersection_exists: continue
        x, y = int(intersection[0]), int(intersection[1])
        if isPointOnscreen(x,y,width,height):
            point = (x,y)
            onscreen_points.append(point)
    return onscreen_points

def getMinMaxPoints(points):
    x_min, y_min = float("inf"), float("inf")
    x_max, y_max = 0, 0
    for x,y in points:
        x_min, y_min = min(x_min, x), min(y_min, y)
        x_max, y_max = max(x_max, x), max(y_max, y)
    return x_min, y_min, x_max, y_max

def getdxdy(distance, slope):
    dx = sqrt( distance**2 / (1 + slope**2))
    dy = slope*dx
    return dx, dy

def getDistance(pnt0,pnt1):
    x_distance, y_distance = pnt1[0] - pnt0[0], pnt1[1] - pnt0[1]
    return sqrt(x_distance**2 + y_distance**2)

def findHashes(img,line1,line2):
    greens = img[:,:,1]
    high_greens = np.zeros(greens.shape)
    high_greens[np.where(greens > 200)] = 1
    green_channel[np.nonzero(high_greens)] = [255,255,255]
    green_channel[np.where(high_greens==0)] = [0,0,0]
    visualize.show_image(green_channel)
    # get search zone array
    # get 4 lines parallel with field lines equidastly spaced
    # get values with green is over threshold (or similar values as lines?)
    # get intercection of lines and high greens
    # if a perfect 8 hashes are found, were done. otherwise, need to try next lines
    # find edges of the hashes
    # all information needed for a field model has been found
    return



def searchForHashMarks(green_channel, field_lines, img):
    print('searching for hash marks')
    height, width = green_channel.shape[0], green_channel.shape[1]
    search_indecies = np.zeros((height, width))

    markers = []
    # def get_point(): return
    for fl in field_lines:
        p0, p1 = fl
        line_length = getDistance(p0, p1)
        ld = 0.3*line_length
        slope = getLineSlope(p0,p1)
        dx, dy = getdxdy(ld, slope)
        top, bottom = getTopBottom(p0,p1)
        TEMP_VANTAGE = 0.5 # get actual constant after i make field modeling stuff. Oh shit it actually might be .5 if height is field_heght
        sign_top = -1 if slope > 0 else 1
        sign_bottom = -1 if slope < 0 else 1
        search_tx, search_ty = int(top[0] + sign_top*dx), int(top[1] + sign_top*dy)
        search_bx, search_by = int(bottom[0] + sign_bottom*TEMP_VANTAGE*dx), int(bottom[1] + sign_bottom*TEMP_VANTAGE*dy)
        search_range_top = (search_tx, search_ty)
        search_range_bottom = (search_bx, search_by)

        marker = [search_range_top, search_range_bottom]
        markers.append(marker)
    print('have search zones')
    search_boxes = []
    for i in range(len(markers)-1):
        m0, m1 = markers[i], markers[i+1]
        frame = Image.new('L', (width, height), 0)
        box_points = [m0[0],m1[0],m1[1],m0[1]]
        ImageDraw.Draw(frame).polygon(box_points, outline=1, fill=1)
        box = np.array(frame)
        search_boxes.append(box)
    # print('getting gradient')
    # gradient = np.gradient(greens)
    # x_gradient, y_gradient = gradient[0], gradient[1]
    # inflection_points = np.where(abs(x_gradient) > .2, 1, 0)
    # for i in range(potential_inflections[0].shape[0]):
    #     print(potential_inflections[1][i], potential_inflections[0][i])
    # img_to_show = np.zeros(green_channel.shape)
    # green_channel[np.nonzero(inflection_points)] = [0,0,0]
    # visualize.show_image(green_channel)

    # print(x_gradient)
    # print(x_gradient.shape, y_gradient.shape, 1, 1)
    # print('gradient found')
    # green_channel = np.zeros(green_channel.shape)
    # for box in search_boxes:
    #     for r in range(height):
    #         for c in range(width):
    #             gx,gy = y_gradient[r,c], x_gradient[r,c]
    #             avg_green_change = (gx+gy)/2
    #             green_channel[r,c,0] = gx
    #             # green_channel[r,c,2] = gy
    greens = green_channel[:,:,1]
    high_greens = np.zeros(greens.shape)
    high_greens[np.where(greens > 200)] = 1
    green_channel[np.nonzero(high_greens)] = [255,255,255]
    green_channel[np.where(high_greens==0)] = [0,0,0]
    visualize.show_image(green_channel)


    # green_channel[np.where(gradient==0)] = [255, 0, 0]



def adjustFieldLines(brightness, lines):
    adjustment_range = 20
    height, width = brightness.shape[0], brightness.shape[1]
    adjusted_field_lines = []
    for l in lines:
        adjusted_line = []
        slope = getLineSlope(l[0],l[1])
        for p in l:
            xl,yl = p
            line_distance = 15
            dx, dy = getdxdy(line_distance, slope)
            lpx, lpy = xl, yl
            if yl < height/2 and slope > 0 or yl > height/2 and slope < 0:
                lpx += dx
                lpy += dy
            else:
                lpx -= dx
                lpy -= dy
            if isPointOnscreen(lpx,lpy, width, height):
                xl,yl = lpx,lpy

            xl, yl = int(xl), int(yl)
            # if yl == height: # THIS IS SO DUMB CHANGE ISONSCREEN
            #     yl-=1
            # if xl == width:
            #     xl-=1
            start, end = xl - adjustment_range/2, xl + adjustment_range/2
            mbx, b = xl, brightness[yl][xl]

            for xt in range(int(start), int(end)):
                if xt >= width: break
                xtb = brightness[yl][xt]
                if xtb > b:
                    b = xtb
                    mbx = xt
            adjusted_line.append((mbx, yl))
        adjusted_field_lines.append(adjusted_line)

    return adjusted_field_lines




def groupLines(img, lines):

    width, height = img.shape[1], img.shape[0]
    no_green = img.copy()
    greens = img[:,:,1]
    no_green[:,:,1] = 0
    brightness = np.mean(no_green, axis=2)

    point_to_point = {}
    point_to_line = {}
    points = []
    for line in lines:
        x1, y1, x2, y2 = line[0], line[1], line[2], line[3]
        p1, p2 = (x1,y1), (x2,y2)
        point_to_point[p1], point_to_point[p2] = p2, p1
        point_to_line[p1], point_to_line[p2] = line, line
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
            if len(hull_points) < 4: continue

            # Note: This will only work for the overhead angle. Otherwise
            # you would need to do left points and right points
            top_points = [hp for hp in hull_points if hp[1] > height/2]
            bottom_points = [hp for hp in hull_points if hp[1] < height/2]
            if len(top_points) != 2 and len(bottom_points) != 2: continue
            top_ave_x = (top_points[0][0] + top_points[1][0]) / 2
            bottom_ave_x = (bottom_points[0][0] + bottom_points[1][0]) / 2
            top_ave_y = (top_points[0][1] + top_points[1][1]) / 2
            bottom_ave_y = (bottom_points[0][1] + bottom_points[1][1]) / 2

            fl_p0 = (int(top_ave_x), int(top_ave_y))
            fl_p1 = (int(bottom_ave_x), int(bottom_ave_y))
            field_line = (fl_p0, fl_p1)
            field_lines.append(field_line)

    field_lines = adjustFieldLines(brightness, field_lines)
    field_lines = sorted(field_lines, key=lambda p: p[0][0])

    return field_lines

def getDistanceRatio(field_lines):#y, width, height):
    fl_distance = 10 # 10 yards
    top_distance, bottom_distance = 0, 0
    last_points = []
    num_lines = len(field_lines)
    for i in range(num_lines):
        p0,p1 = field_lines[i]
        top, bottom = getTopBottom(p0,p1)
        if i == 0:
            last_points = [top, bottom]
        else:
            top_distance += abs(top[0] - last_points[0][0])
            bottom_distance += abs(bottom[0] - last_points[1][0])
    dfl = 10 # 10 yards
    top_distance /= (num_lines-1)
    bottom_distance /= (num_lines-1)

    top_ratio = top_distance / dfl
    bottom_ratio = bottom_distance / dfl

    return (top_ratio + bottom_ratio) / 2
    #
    # y_ratio = y/height
    # return bottom_ratio + y_ratio(top_ratio - bottom_ratio)

def removeFieldLines(img, field_lines):
    #fl_width = 0.111111
    fl_width = 0.2
    pixelDistanceRatio = getDistanceRatio(field_lines)
    fl_pixel_width = int(pixelDistanceRatio * fl_width)
    print('fl width', fl_pixel_width)
    for fl in field_lines:
        cv.line(img, fl[0], fl[1], [0,0,0], fl_pixel_width)
    return img

def doSomething(img, field_lines):
    width, height = img.shape[1], img.shape[0]
    no_greens = img.copy()
    no_greens[:,:,1] = 0
    avg_rb = np.mean(no_greens,axis=2)
    # darks = np.where(avg_rb < 100, 1, 0)
    darks = np.where(avg_rb > 100, 1, 0)
    # wi = np.zeros(img_arr.shape)
    # wi[np.nonzero(whites)] = [255,255,255]
    # whites = np.zeros(img.shape)#np.zeros(img.shape)
    # whites.fill(255)
    whites = img.copy()
    whites[np.nonzero(darks)] = [255,0,0]
    removeFieldLines(whites, field_lines)
    whites = np.array(whites,np.int32)

    res = tes.image_to_string(Image.fromarray((whites * 255).astype(np.uint8)),config='digits')
    print(res)
    visualize.show_image(whites)

    # print(int(0.9*height))
    # whites[int(0.9*height):height,:] = [255,0,0]


if __name__ == '__main__':
    # edges = cv2.Canny(frame,100,200)

    #video = 'scenes/2019w3_nyj-ne/scene_0.mov'
    scene_dir = 'scenes/overhead'
    for scene_file in os.listdir(scene_dir):
        scene_path = os.path.join(scene_dir, scene_file)

        #scene_path = 'scenes/overhead/scene_22.mp4'
        #scene_path = scenes/overhead/scene_19.mp4
        print(scene_path)

        scene = getArrayFromVideo(scene_path)
        frame = scene[0]
        height, width = frame.shape[0], frame.shape[1]

        lines = line.detect()
        lines = [line.fitToFrame(line, height, width) for line in lines]
        lines = groupLines(lines)
        for line in lines:
            framed_line = line.fitToFrame(line, width, height)
            if len(framed_line) == 2:
                p0, p1 = points[0], points[1]
                x1, y1, x2, y2 = p0[0], p0[1], p1[0], p1[1]
                # cv.line(frame,(x1,y1),(x2,y2),(255,0,0),2)
                fixed.append((x1,y1,x2,y2))
        groups = groupLines(frame, fixed)
        # doSomething(frame, groups)
        # field_lines = [getFieldLine(g) for g in groups if len(g)>2]
        # visualize.show_image(toBlackAndWhite(frame))
        searchForHashMarks(getGreenChannel(frame), groups, frame)
        for field_line in groups:

            cv.line(frame, field_line[0], field_line[1], [0,0,255], 2)


        # visualize.show_image(frame)
