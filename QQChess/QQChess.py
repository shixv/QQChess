from PIL import ImageGrab, Image

if __name__ == '__main__':
    img = ImageGrab.grab()
    img.save("test.jpg")
    