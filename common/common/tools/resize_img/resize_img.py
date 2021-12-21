import cv2

def resize_img(fpath):
    """
    进行图片压缩
    IMWRITE_JPEG_QUALITY：表示图片的质量，值越大，大小越大
    """
    img = cv2.imread(fpath)
    cv2.imwrite(fpath,img,[cv2.IMWRITE_JPEG_QUALITY,90])

if __name__ == '__main__':

    imgfpath = "test.jpg"
    resize_img(imgfpath)