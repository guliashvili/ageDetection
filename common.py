import os

def get_images(dir):
    dir = os.path.expanduser(dir)
    files = (os.path.join(dir, file) for file in os.path.listdir(dir))
    files = (file for file in files if os.path.isfile(file) and not file.endswith('.txt') and '.' in file)

    return files