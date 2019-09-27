from __future__ import print_function
import os

import subprocess # used to run ffmpeg command to split video file

from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector

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

            # video_name = os.path.splitext(file)[0] # strips the file extension
            # os.path.mkdir(f'{scene_dir}/{video_name}')
            #
            # for scene_number, timestamp in enumerate(timestamps):
            #     start_time = timestamp[0]
            #     end_time = timestamp[1]
            #     saveScene(video_file, )
            # scene_file = f'{scene_dir}/{video_name}/'


    # video_file = f'{VIDEO_DIR}/S2019w3_nyj-ne.mov'
    # print(video_file)
    # outfile_dir = SCENE_BASE_DIR
    # saveScenes(video_file, outfile_dir)

def getSceneTimestamps(video_file):

    # Setup PySceneDetect's VideoManager and SceneManager
    video_manager = VideoManager([video_file])
    scene_manager = SceneManager(StatsManager())
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    # get the video length from the video manager
    duration_info = video_manager.get_duration()
    video_length = duration_info[2] - duration_info[1] # end_time - start_time

    # Set the duration to be the whole video. The beginging of the video starts
    # at the video managers base_timecode. The end can be found with video length
    end_time = base_timecode + video_length
    video_manager.set_duration(start_time=base_timecode, end_time=end_time)

    # Set downscale factor to improve processing speed (no args means default).
    video_manager.set_downscale_factor()

    # try/finally so video manager always releases in the finally, even with errors
    try:
        video_manager.start()

        # use the scene manager to detect schene changess
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list(base_timecode)

        # scene_list is a list of tuples. Each tuple holds 2 FrameTimecodes object
        # for the scenes start/end frame. Map them to timestamps: (starttime, endtime)
        getDuration = lambda scene: (scene[0].get_timecode(), scene[1].get_timecode())
        timestamps = map(getDuration, scene_list)
    finally:
        video_manager.release() # no longer need the video manager. release it
        return list(timestamps) # convert map object to list and return


def saveScene(infile, outfile, timestamp):
    start, end = timestamp[0], timestamp[1]
    # run a ffmpegg command to create make a split copy of the video file
    # terminal command: ffmpeg -i "video.mp4" -ss "0" -c copy "scene.mp4"
    cmd = ['ffmpeg', '-i', infile, '-ss', start, '-to', end, '-c', 'copy', outfile]
    subprocess.run(cmd, stderr=subprocess.STDOUT)




if __name__ == '__main__':
    video_dir = 'videos'

    if not os.path.exists('scenes'): os.mkdir('scenes')

    for file in os.listdir(video_dir):
        # make sure the file is a video file
        if file.endswith('.mov') or file.endswith('.mp4'):
            # use the video's name to create a directory to store the video's scenes
            # video_name = os.path.splitext(file)[0] # strips the file extension
            file_path = os.path.join(video_dir, file)
            timestamps = getSceneTimestamps(file_path)

            vid_file_name = os.path.splitext(file)[0] # strips the file extension
            scene_dir = f'scenes/{vid_file_name}'
            os.mkdir(scene_dir)
            for scene_number, timestamp in enumerate(timestamps):
                scene_name = f'scene_{scene_number}.mov'
                scene_file = os.path.join(scene_dir, scene_name)
                saveScene(file_path, scene_file, timestamp)

            print(timestamps)
