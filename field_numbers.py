def detect_text(img_arr):
    sums = np.mean(img_arr, axis=2)
    white = np.where(sums > 190, 1, 0)
    #points = [(wi[1][i],wi[0][i]) for i in range(len(wi[0]))]
    indecies = np.nonzero(white)
    # white = np.zeros(img_arr.shape)
    # white[sums < 200] = [255,255,255]
    points = [(indecies[0][i],indecies[1][i]) for i in range(len(indecies[0]))]
    cluster_labels = hcluster.fclusterdata(points, 25, criterion="distance")
    clusters = {label:[] for label in cluster_labels}
    for i, label in enumerate(cluster_labels):
        clusters[label].append(points[i])
    for g in clusters.values():
        color = np.random.choice(range(256), size=3)
        for p in g:
            img_arr[p[0]][p[1]] = color
    visualize.show_image(img_arr)
    output = tes.Output.DICT
    #conf = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
    # results = tes.image_to_boxes(im, output_type=output, config=conf)
    return results
