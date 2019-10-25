# Using video footage, find the sidelines and yard ticks to create a model of
# the field, where player locations can be mapped to


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



def createSpatialModel(fieldmarks, hashmarks, boundaries):
    fieldlines = findFieldLines(image)
    hashmarks = findHashMarks(image, fieldlines)
    boundaries = findBoundaries(image, fieldlines, hashmarks, boundaries)



