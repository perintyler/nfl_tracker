import cv2 as cv 
import numpy as np 

from collections import deque as Queue

from video_manager import VideoManager
import visualize
from fieldlines import findFieldLines
import file_utils
import line

class HashMarkDetectionError(Exception):

    def __init__(self):
        Exception.__init__(self,'Unable to detect any hash marks')

class HashMarks:

    def __init__(self, coordinates):
        self.coordinates = coordinates


    def draw(self, image):
        point_radius = 2
        color = (255,0,0)
        line_type = -1
        for point in self.coordinates:
            cv.circle(image,point, point_radius, color, line_type)

    def makeAdjustments(self, brightness):
        return
        for point in self.centers:
            x, y = point
        return


    def findEdges(self, image):
        # get min/max x and y bright point and make a square from the 4 points
        return [0,0,0,0]


def findHotspots(fl1, fl2, bright_vals, image, search_jump=10, max_search_distance=500):
    NUM_HASH_MARKS = 4
    distance_searched = 0 
    p1, p2 = fl1.getBottomPoint(), fl2.getBottomPoint()

    fl1_slope, fl2_slope = fl1.getSlope(), fl2.getSlope()
    p1_dx, p1_dy = line.getdxdy(search_jump, fl1_slope)
    p2_dx, p2_dy = line.getdxdy(search_jump, fl2_slope)
    
    direction1 = 1 if p1_dy > 0 else - 1
    direction2 = 1 if p2_dy > 0 else - 1
    p1_dx, p1_dy = direction1*p1_dx, direction1*p1_dy
    p2_dx, p2_dy = direction2*p2_dx, direction2*p2_dy

    height, width = bright_vals.shape

    pointIsOnscreen = lambda p: (p[0] >= 0 and p[0] < width and
                                    p[1] >= 0 and p[1] < height)

    # cv.line(image, (int(p1[0]),int(p1[1])), (int(p2[0]),int(p2[1])), [0,0,255], 2)
    # visualize.show_image(image)

    while distance_searched < max_search_distance:
        print(f'search points: {p1}, {p2}')
        search_line = p1[0], p1[1], p2[0], p2[1]
        hotspots = line.getEquidistantPoints(search_line, NUM_HASH_MARKS)
        spots = list(map(lambda hs: (int(hs[0]),int(hs[1])),hotspots))

        hotspots_are_hashmarks = True
        num_bright = 0
        for point in hotspots: 
            # if not pointIsOnscreen(point): # TODO when i fix things this should be gone
            #     hotspots_are_hashmarks = False
            #     break

            x, y = point
            r, c = int(y), int(x)
            point_is_bright = True if bright_vals[r,c] == 1 else False
            if not point_is_bright:
                hotspots_are_hashmarks = False
                # break
            else:
                num_bright+=1

        print(f'num bright: {num_bright}')
        if num_bright > 2:
            hm = HashMarks(spots)
            hm.draw(image)
            visualize.show_image(image)

        if hotspots_are_hashmarks:
            print("WHATS IT REALLY GOOD SON")
            return True, hotspots
        else:
            distance_searched += search_jump
            p1x = p1[0] + p1_dx
            p1y = p1[1] + p1_dy
            p2x = p2[0] + p2_dx
            p2y = p2[1] + p2_dy
            p1, p2 = (p1x, p1y), (p2x, p2y)




    return False, [] 

def findHashMarks(image, field_lines):
    SEARCH_JUMP = 10
    MAX_SEARCH_DISTANCE = 100
    NUM_HASH_MARKS = 4

    no_green = image.copy()
    no_green[:,:,1] = 0
    brightness = np.mean(no_green, axis=2)

    bright_vals = np.where(brightness > 120, 1, 0)

    field_line = field_lines[1]
    while field_line.hasNextLine():
        hashmark_sets = []
        top_hm_found, top_hm = findHotspots(field_line, field_line.next_line, bright_vals, image)
        bottom_hm_found, bottom_hm = findHotspots(field_line, field_line.next_line, bright_vals, image)
        if top_hm_found and bottom_hm_found:
            hm_coordinates = hm1 + hm2
            hashmarks = HashMarks(hm_coordinates)
            hashmarks.makeAdjustments(brightness)
            return hashmarks
        field_line = field_line.next_line

    raise HashMarkDetectionError()




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


if __name__ == '__main__':
    scene_dir = 'scenes/overhead'
    videos = file_utils.getPaths(scene_dir)
    first_video = videos[0]
    manager = VideoManager(first_video)
    first_frame = manager.getFrame(0)
    field_lines = findFieldLines(first_frame)

    for fl in field_lines: fl.draw(first_frame)

    hashmarks = findHashMarks(first_frame, field_lines)
    hashmarks.draw(first_frame)
    visualize.show_image(first_frame)




