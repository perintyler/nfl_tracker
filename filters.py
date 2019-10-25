def toBlackAndWhite(img):
    avg = np.mean(img, axis=2)
    bw = np.zeros(img.shape)
    bw[np.where(avg>150)] = [255,255,255]
    return bw


def getGreenChannel(img):
    green = img.copy()
    green[:,:,0] = 0
    green[:,:,2] = 0
    return green

