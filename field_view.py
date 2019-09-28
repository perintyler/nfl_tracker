# use black and white filter
# for field maybe only show white pixels
import cv2
import numpy as np
from video_utils import getArrayFromVideo
def toBlackAndWhite(img):
    gray_scale = np.dot(img[...,:3], [0.2989, 0.5870, 0.1140])
    bw = np.asarray(gray_scale).copy()
    bw[bw < 128] = 0    # Black
    bw[bw >= 128] = 255 # White
    return bw


def removeBlackFrames(video):
    return

if __name__ == '__main__':
    #video = 'scenes/2019w3_nyj-ne/scene_0.mov'
    video = 'scenes/carr/scene_0.mp4'
    arr = getArrayFromVideo(video)
    first_frame = arr[0]
    a = toBlackAndWhite(first_frame)
    print(a.shape)
