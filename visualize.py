from matplotlib import pyplot as plt

# interactive mode
plt.ion()


def show_image(arr):
    plt.imshow(arr)#, interpolation='nearest')
    plt.show()
    input()
    plt.close()



def preview(video, display_frame_rate=50):
    for frame_num in range(0,len(video),display_frame_rate):
        frame = video[frame_num]
        show_image(frame)
