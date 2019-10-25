import cv2 as cv 
import numpy as np 

from collections import deque as Queue

from video_manager import VideoManager


class HashMarkDetectionError(Exception):

    def __init__(self)
        Exception.__init__(self,'Unable to detect any hash marks')

class HashMarks:

    def __init__(self, locations):
        self.centers = locations

    def adjust(self, brightness):
         for point in self.centers:
            x, y = point
        return


    def findEdges(self, image):
        # get min/max x and y bright point and make a square from the 4 points
        return [0,0,0,0]


def findHashMarks(image, field_lines):
    hashmarks_found = False
    fl_to_search = field_lines.copy()
    search_zones = list(map(lambda fl: fl.getZone(), field_lines))
    for fl1 in field_lines:
        fl2 = field_lines.next_line
        center1, center2 = fl1.getMidwayPoint(), fl2


    raise HashMarkDetectionError()


def searchBetweenFieldLines(fl1, fl2):
    hm1, hm2 = [], []
    hm1_found, hm2_found = False, False


    center1, center2 = fl1.getMidwayPoint(), fl2.getMidwayPoint()




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


if __name__ == '__main__':
    scene_dir = 'scenes/overhead'
    videos = file_utils.getPaths(scene_dir)
    first_video = videos[0]
    manager = VideoManager(first_video)
    first_frame = manager.getFrame(0)
    field_lines = getFieldLines(first_frame)




