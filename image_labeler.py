import os
from matplotlib import pyplot as plt
import json
from video_utils import getArrayFromVideo

labels = []
images = []
paths = []
dir = 'scenes'

# interactive mode
max_label = 5

def startLabeling():
    plt.ion()
    num_images = len(images)
    while index < num_images:
        img = images[index]
        plt.imshow(img)
        plt.show()
        user_input = input('Enter Label')
        plt.close()
        if user_input == 'back':
            labels.pop()
            index-=1
        elif user_input == 'stop':
            label_info = {paths[i]:label[i] for i in range(len(labels))}
            storeLabels(label_info)
        elif user_input == 'skip':
            index+=1
        else:
            try:
                label = int(label)
                if label < 0 or label > max_label:
                    print('invalid label')
                else:
                    labels.append(label)
                    index+=1
            except:
                print('invalid label')



def storeLabels(label_info):
    label_file = 'labels.json'
    with open(label_file, 'w') as f:
        json.dump(label_info, f)


def get_images():
    for scene_dir in os.listdir('scenes'):
        for scene in os.listdir(f'scenes/{scene_dir}):
            path = f'scenes/{scene_dir}/{scene}'
            video = getArrayFromVideo()
            frame_num = 20
            frame = video[frame_num]
            images.append(frame)
            paths.append(path)

if __name__ == '__main__':
    print('getting images')
    getImages()
    print('Finished Getting Images')
    startLabeling()
