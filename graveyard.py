            #print('og poly', polygon_area(hull_points))
                # if x_min is None or x_min[0] > x: x_min = (x,y)
                # if y_min is None or y_min[1] > y: y_min = (x,y)
                # if x_max is None or x_max[0] < x: x_max = (x,y)
                # if y_max is None or y_max[1] < y: y_max = (x,y)
            #field_line = (x_min, y_min, x_max, y_max)

            # frame = Image.new('L', (width, height), 0)
            # ImageDraw.Draw(frame).polygon(hull_points, outline=1, fill=1)
            # fl = np.array(frame)

            # poly_indecies = np.nonzero(fl)
            #
            # #img[poly_indecies] = [255,0,0]
            # r,g,b = np.mean(img[poly_indecies], axis=0)
            # print(r,g,b)

            # far_away = width*height
            # closest_points = { hp: [far_away,()] for hp in hull_points}
            # getDistance = lambda p1, p2: sqrt( (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 )
            # white_channel = 1.0 * (img > threshold)
            # white_channel = np.where(white_channel == [1,1,1], 1, 0)

            # rows, cols = height, width
            # for row in range(rows):
            #     for col in range(cols):
            #         if fl[row][col] != 1: continue
            #         r, g, b = img[row][col]
            #
            #         threshold = 120
            #         isWhiteEnough = lambda r,g,b: r > threshold and g > threshold and b > threshold
            #         if isWhiteEnough(r,g,b):
            #             white_point = (col, row)
            #             hp_distances = [getDistance(hp,white_point) for hp in hull_points]
            #             distance_ranks = [i[0] for i in sorted(enumerate(hp_distances), key=lambda k:k[1])]
            #             for rank, index in enumerate(distance_ranks):
            #                 hp_distance = hp_distances[index]
            #                 hp = hull_points[index]
            #                 min_distance = closest_points[hp][0]
            #                 if hp_distance < min_distance:
            #                     #print('yes', hp, hp_distance, min_distance, x, y)
            #                     closest_points[hp] = (hp_distance,white_point)
            #                     break

            # fl_poly = list(map(lambda val: val[1], closest_points.values()))

            # field_lines.append(fl_poly)


    #for field_line in field_lines:

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
    # im = Image.fromarray(img_arr)
    # im = im.filter(ImageFilter.MedianFilter())
    # enhancer = ImageEnhance.Contrast(im)
    # im = enhancer.enhance(2)
    # im = im.convert('1')
    # a = np.array([[[1,1,1],[2,2,2]],[[3,3,3],[4,4,4]]])
    # a = np.prod(a, axis=(1))
    # print(a)
    # p = np.dot(img_arr)
    # ave_rgb = np.mean(img_arr,axis=2)
    # whites = np.where(ave_rgb > 150, 1, 0)
    #
    # wi = np.zeros(img_arr.shape)
    # wi[np.nonzero(whites)] = [255,255,255]

    # whites[np.where(ave_rgb > 150)[0]] = [255,255,255]
    # whites[np.where(ave_rgb < 150)[0]] = [0,0,0]

    # visualize.show_image(whites)
    # b, g, r = img_arr[:, :, 0], img_arr[:, :, 1], img_arr[:, :, 2]
    # sums = np.add(r, g)
    # print(sums[0])
    # sums = np.add(sums,b)
    # print(sums[0])
    # for r in range(img_arr.shape[0]):
    #     for c in range(img_arr.shape[1]):
    #         print(img_arr[r][c], b[r][c], g[r][c], b[r][c], sums[r][c])

    # white = np.zeros(sums.shape)
    # white[sums > 300] = 1
    # white[sums < 300] = 0
    # img_arr[p.nonzero()] = [255,0,0]
    # print('showing')
    # visualize.show_image(img_arr)
    # print(p.shape,'1')
    #
    # pi = np.nonzero(p)
    # ni = np.where(p == 0)[0]
    # print(len(pi), len(ni))
    # img_arr[pi] = [255, 0, 0]
    # img_arr[ni] = [0,255,0]
    # visualize.show_image(img_arr)
    # #pi = np.nonzero(p)
            # for point in field_line:
            #     print(point)
            #     cv.circle(frame, point, 3, [0,0,255])
            #poly = np.array(field_line, 'int32')
            # x_min, y_min = float("inf"), float("inf")
            # x_max, y_max = 0, 0
            # for x,y in points:
            #     x_min, y_min = min(x_min, x), min(y_min, y)
            #     x_max, y_max = max(x_max, x), max(y_max, y)
            # slope = (y_max-y_min)/(x_max-x_min)
            # print(slope, x_min, x_max)
# def filterFieldLines(brightness, greens, lines):
#     filtered_lines = []
#     for fl in lines:
#         line_mask = np.zeros(brightness.shape, dtype=np.uint8)
#
#         x0,y0,x1,y1 = fl[0][0], fl[0][1], fl[1][0], fl[1][1]
#
#         rr, cc, val = line_aa(y0,x0,y1,x1)
#         line_mask[rr, cc] = 1
#         line_brightness = brightness[np.nonzero(line_mask)]
#         avg_brightness = np.mean(line_brightness)
#
#         avg_green = np.mean(greens[np.nonzero(line_mask)])
#         print(line_brightness.shape)
#         brightness_threshold = 100
#         green_threshold = 220
#         print(avg_brightness, avg_green)
#         if avg_brightness > brightness_threshold and avg_green < green_threshold:
#             filtered_lines.append(fl)
#     print('before filter', len(lines), 'after filter', len(filtered_lines))
#     return filtered_lines
