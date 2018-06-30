# coding: utf-8
import mxnet as mx
from mtcnn_detector import MtcnnDetector
import cv2
import os
import time
import common

detector = MtcnnDetector(model_folder='model', ctx=mx.cpu(0), num_worker = 4 , accurate_landmark = False)


dataset = common.get_images('photoIN')
for imgp in dataset:
    img = cv2.imread(imgp)

    filename = os.path.splitext(os.path.split(img)[1])[0]
    output_filename = os.path.join('photoOUT', filename + '.png')

    # run detector
    results = detector.detect_face(img)

    if results is not None:

        total_boxes = results[0]
        points = results[1]
        if total_boxes != 1:
            continue

        # extract aligned face chips
        chips = detector.extract_image_chips(img, points, 144, 0.37)
        for chip in chips:
            cv2.imwrite(output_filename, chip)
