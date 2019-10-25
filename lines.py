
def detect(image):
    gray = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray,50,150,apertureSize = 3)
    lines = cv.HoughLines(edges,1,np.pi/180,200)

    def getCartesianCoordinates(line):
        rho, theta = line[0], line[1]
        a, b = np.cos(theta), np.sin(theta)
        x0, y0 = a*rho, b*rho
        x1, y1 = int(x0 + 1000*(-b)), int(y0 + 1000*(a))
        x2, y2 = int(x0 - 1000*(-b)), int(y0 - 1000*(a))
        return x1, y1, x2, y2

    return [getCartesianCoordinates(line[0]) for line in lines]



def group(lines):

    width, height = img.shape[1], img.shape[0]

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


def findIntersection(l1, l2):
    x1, y1, x2, y2 = l1
    x3, y3, x4, y4 = l2
    try:
        px= ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
        py= ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
    except ZeroDivisionError:
        return False, ()
    else:
        return True, (px, py)


def fitToFrame(line, width, height):
    max_x, max_y = width-1, height-1
    top = (0, max_y, max_x, max_y)
    bottom = (0, 0, max_x, 0)
    left = (0, 0, 0, max_y)
    right = (max_x, 0, max_x, max_y)

    onscreen_points = []

    for edge in [top, bottom, left, right]:
        if len(onscreen_points) == 2: break
        intersection_exists, intersection = findIntersection(line, edge)
        if intersection_exists:
            x, y = int(intersection[0]), int(intersection[1])
            onscreen_points.append( (x,y) )
    p0, p1 = onscreen_points
    return p0[0], p0[1], p1[0], p1[1]