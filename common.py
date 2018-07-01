import os
import re
import random


def get_images(dir):
    dir = os.path.expanduser(dir)
    files = (os.path.join(dir, file) for file in os.listdir(dir))
    files = [file for file in files if os.path.isfile(file)
            and not file.endswith('.txt')
            and '.' in file
            and not file.endswith('.DS_Store')
            and not file.endswith('.csv')
            and not file.endswith('.lst')
            and not file.endswith('.bin')
            and not file.endswith('.idx')
            and not file.endswith('.rec')]

    return files
