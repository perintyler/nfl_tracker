'''
This file can be used to detect scene changes in a video file. It also
can be used to create new video files for each scene. The scene videos are
trimmed copies of the original video, only containing frames for a single scene
'''

from __future__ import print_function
import os
import csv

import sys
import traceback

import subprocess # used to run ffmpeg command to split video file

from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector

import video_utils

video_dir = 'videos'
base_scene_dir = 'scenes'
timestamp_dir = 'timestamps'


'''
Uses pyscenedetect to detect scene changes in a video file. The returned
value is a list of timestamps for each scene. A timestamp is represented as
a tuple of size 2 with a start and end time e.g. (0, 20) -> first 20 ms of video.
If optional arg save_as_csv is set to true, the timestamps will be saved to
a csv file, which will be used if this func is called again on the same video.
'''
def getSceneTimestamps(video_file, save_as_csv=False):
    framerate = video_utils.getFrameRate(video_file)

    video_name = video_utils.getFileName(video_file)
    timestamp_file = f'{video_name}.csv'
    timestamp_path = os.path.join(timestamp_dir, timestamp_file)

    if os.path.exists(timestamp_path):
        csv_file = open(timestamp_path, 'r')
        reader = csv.reader(csv_file)
        timestamps = []
        for line in reader:
            start = FrameTimecode(timecode=line[0], fps=framerate)
            end = FrameTimecode(timecode=line[1], fps=framerate)
            timestamps.append( (start, end) )
        csv_file.close()
        return timestamps



    # Setup PySceneDetect's VideoManager and SceneManager
    video_manager = VideoManager([video_file], framerate=framerate)
    scene_manager = SceneManager(StatsManager())
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    # get the video length from the video manager
    duration_info = video_manager.get_duration()
    video_length = duration_info[2] - duration_info[1] # end_time - start_time

    # Set the duration to be the whole video. The beginging of the video starts
    # at the video managers base_timecode. The end can be found with video length
    start_time = base_timecode
    end_time = start_time + video_length
    video_manager.set_duration(start_time=start_time, end_time=end_time)

    # Set downscale factor to 1 which indicates no downscaling. Downscaling
    video_manager.set_downscale_factor(downscale_factor=1)

    # try/finally so video manager always releases in the finally, even with errors
    try:
        print(f'Detecting scenes from {video_file}')
        video_manager.start()

        # use the scene manager to detect schene changess
        scene_manager.detect_scenes(frame_source=video_manager)
        timestamps = scene_manager.get_scene_list(base_timecode)
        # scene_list is a list of tuples. Each tuple holds 2 FrameTimecodes object
        # for the scenes start/end frame. Map them to timestamps: (starttime, endtime)
        # getDuration = lambda scene: (scene[0].get_timecode(), scene[1].get_timecode())
        # timestamps = list(map(getDuration, scene_list))

        if save_as_csv and not os.path.exists(timestamp_path):
            if not os.path.exists(timestamp_dir): os.mkdir(timestamp_dir)
            with open(timestamp_path, 'w') as tsf:
                writer = csv.writer(tsf)
                for ts in timestamps:
                    start_time, end_time = ts[0].get_timecode(), ts[1].get_timecode()
                    writer.writerow([start_time, end_time])
            tsf.close()
    finally:
        video_manager.release() # no longer need the video manager. release it
        return timestamps # convert map object to list and return

'''
Uses ffmpeg to run a subprocess command to trim the infile video using the
given timestamp. The copied and trimmed video will be stored in the location
of the given outfile.
    infile: path of video file to be trimmed
    outfile: path used to store the copied/trimmed video
    timestamp: tuple with a start and end time (ms) of the trimmed video e.g. (0,20)
'''
def saveScene(infile, outfile, timestamp):
    # get the starting and ending frame time code
    start, end = timestamp[0], timestamp[1]
    start_time = start.get_timecode()
    duration = (end - start).get_timecode()

    # https://superuser.com/questions/138331/using-ffmpeg-to-cut-up-video
    # https://superuser.com/questions/1056599/ffmpeg-re-encode-a-video-keeping-settings-similar
    cmd = ['ffmpeg', '-i', infile, '-ss', start_time, '-t', duration, '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-c:a', 'copy', outfile]

    print(f'encoding video file {infile} with timestamp {timestamp}')
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # subprocess.run(cmd, stderr=subprocess.DEVNULL)



if __name__ == '__main__':

    try:
        # if not already created, create the base scene directory which will
        # store the scenes for every video in the video dir
        if not os.path.exists(base_scene_dir): os.mkdir(base_scene_dir)

        for video in os.listdir(video_dir):
            # split the file into a name and extension: name.mp4 -> name, .mp4
            video_name = os.path.splitext(video)[0]
            video_ext = os.path.splitext(video)[1]

            # use the video name to create a scenes dir inside the base scene dir,
            # which will store all scenes for this video: base_scene_dir/video_name/
            # If the directory already exists, skip this video file because scenes
            # have already been stored
            scene_dir = os.path.join(base_scene_dir, video_name)
            if os.path.exists(scene_dir): continue
            os.mkdir(scene_dir)

            # make sure the file is a video file
            if video_ext == '.mp4' or video_ext == '.mov':
                # construct the full path for the video file and get scene timestamps
                video_path = os.path.join(video_dir, video)
                timestamps = getSceneTimestamps(video_path, save_as_csv=True)
                # Iterate through the timestamps and create new video files for each scene
                for scene_number, timestamp in enumerate(timestamps):
                    start_time, end_time = timestamp[0], timestamp[1]
                    #print(timestamp[0], timestamp[1])
                    scene_length = (end_time - start_time).get_seconds()

                    if scene_length < 2: continue

                    scene_file = f'scene_{scene_number}{video_ext}'
                    scene_path = os.path.join(scene_dir, scene_file)

                    saveScene(video_path, scene_path, timestamp)

    except Exception as e:
        traceback.print_exc()
    finally:
        for scene_dir in os.listdir(base_scene_dir):
            path = f'{base_scene_dir}/{scene_dir}'
            if path == 'scenes/.DS_Store': continue
            if len(os.listdir(path)) == 0: os.rmdir(path)
