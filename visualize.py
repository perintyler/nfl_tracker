from matplotlib import pyplot as plt

# interactive mode
plt.ion()


def show_image(arr):
    plt.imshow(arr, interpolation='nearest')
    plt.show()
    input()
    plt.close()
