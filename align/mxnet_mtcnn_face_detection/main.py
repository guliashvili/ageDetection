# coding: utf-8
import mxnet as mx
from mtcnn_detector import MtcnnDetector
import cv2
import os
import time
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
            and not file.endswith('.bin')]

    return files

detector = MtcnnDetector(model_folder='model', ctx=mx.cpu(0), num_worker = 4 , accurate_landmark = False)


dataset = get_images('photoIN')
for imgp in dataset:
    img = cv2.imread(imgp)

    filename = os.path.splitext(os.path.split(imgp)[1])[0]
    output_filename = os.path.join('photoOUT', filename + '.png')

    # run detector
    results = detector.detect_face(img)

    if results is not None:

        total_boxes = results[0]
        points = results[1]
        if len(points) != 1:
            continue

        # extract aligned face chips
        chips = detector.extract_image_chips(img, points, 144, 0.37)
        for chip in chips:
            cv2.imwrite(output_filename, chip)
