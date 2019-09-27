from __future__ import print_function
import os
import sys

import scenedetect
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector

from settings import VIDEO_DIR, SCENE_BASE_DIR

def getSceneTimestamps(video_file):

    # Set up a PySceneDetect's Manager objects which finds scene transitions
    video_manager = VideoManager([video_file])
    scene_manager = SceneManager(StatsManager())
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    # get the video length 
    duration_info = video_manager.get_duration()
    vid_length = duration_info[2] - duration_info[1] # end_time - start_time


    start_time = base_timecode
    end_time = start_time + vid_length

    # Set video_manager duration to be the videos duration
    video_manager.set_duration(start_time=start_time, end_time=end_time)
    # Set downscale factor to improve processing speed (no args means default).
    video_manager.set_downscale_factor()

    # using a try  here to ensure that the video manager is released in
    # the finally statement, even if there are errors
    try:
        video_manager.start()

        # Use the scene manager to perform scene detection, then get a list of scenes
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list(base_timecode)

        getDuration = lambda frame: (scene[0].get_timecode(), scene[1].get_timecode())
        timestamps = list(map(getDuration, scene_list))
    finally:
        # release the video manager
        video_manager.release()
        return timestamps


def saveSceneFile(infile, outfile, start_time, end_time):
    ['ffmpeg', 'i', file]
    return


# def saveScenes(video_file, scene_dir):
    # strip the directory and extension of the video file to get the file name
    # used to organize the video's scene data ('dir/filename.ext' -> filename)
    # video_name = os.path.splitext(os.path.basename(video_file))[0]

    # # if it hasn't already been created, create a directory to store
    # # all scene files for the given video
    # scenes_dir = f'{outfile_dir}/{video_name}'
    # if not os.path.exists(scenes_dir):
    #     os.mkdir(scenes_dir)

    # Store scene timestamps in a csv file if the scene data hasn't already been stored
    # timestamp_file = f'{scenes_dir}/timestamps.csv'
    # if not os.path.exists(timestamp_file):
    #     findSceneData(video_file, timestamp_file)

    # scene data has been found. Save each scene as individual video files
    # using the timestamps stored in the scene data csv file




if __name__ == '__main__':
    video_dir = 'video'
    if not os.path.exists(video_dir): os.mkdir(video_dir)

    for file in os.listdir(video_dir):
        # make sure the file is a video file
        if file.endswith('.mov') or file.endswith('.mp4'):
            # use the video's name to create a directory to store the video's scenes
            # video_name = os.path.splitext(file)[0] # strips the file extension
            file_path = os.path.join(video_dir, file)
            timestamps = getSceneTimestamps(file_path)


    # video_file = f'{VIDEO_DIR}/S2019w3_nyj-ne.mov'
    # print(video_file)
    # outfile_dir = SCENE_BASE_DIR
#    saveScenes(video_file, outfile_dir)
