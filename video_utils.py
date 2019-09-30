import skvideo.io
from PIL import Image

import visualize
import cv2

import os

def getFileName(path):
    file = os.path.basename(path)
    return os.path.splitext(file)[0]

def getFileExt(path):
    file = os.path.basename(path)
    return os.path.splitext(file)[1]

def getFrameRate(video):
    vid_cap = cv2.VideoCapture(video)
    return vid_cap.get(cv2.CAP_PROP_FPS)

def removeBlackFrames(video):
    frame0 = video[0]
    return

def getArrayFromVideo(file):
    return skvideo.io.vread(file)

# def dir_map(dir, func):
#     for scene in os.path.listdir(scene_dir):
#         scene_path = os.path.join(scene_dir, scene)
if __name__ == '__main__':
    video = 'scenes/2019w3_nyj-ne/scene_0.mov'
    arr = getArrayFromVideo(video)
    for i in range(0,len(arr),20):
        visualize.show_image(arr[i])
        input()
