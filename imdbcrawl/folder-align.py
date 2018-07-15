#import urllib.request
import requests
# import urllib
import traceback
import time
import random
import json
import sys
import mxnet as mx
from mtcnn_detector import MtcnnDetector
import cv2
import os
import time
import os
import re
import random
import numpy as np
from multiprocessing import Process
import argparse
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
CPU = 1


def get_imgs(dir):
    return list(set(get_images(dir)))


def align(i, dir, outdir):
    detector = MtcnnDetector(model_folder='model', num_worker = 1 , accurate_landmark = False)

    imgs = get_imgs(dir)
    s = len(imgs)*i/CPU
    e = min(len(imgs), len(imgs)*(i+1)/CPU)
    imgs = imgs[s: e]

    for imgc in imgs:
        imgPath = imgc
        name = os.path.basename(imgc)
        imgc = cv2.imread(imgc)
        if len(imgc.shape) == 2:
            imgc = cv2.cvtColor(imgc,cv2.COLOR_GRAY2RGB)

        height, width, _ = imgc.shape
        if height + width > 1700:
            mult = min(0.5, 1000.0/max(height,width))
            imgc = cv2.resize(imgc, (0,0), fx=mult, fy=mult)

        results = detector.detect_face(imgc)
        if results is None:
            imgc = [imgc]
            print('Could not find the face ' + imgPath)
        else:
            points = results[1]
            if len(points) != 1:
                print('could find more then one face ' + imgPath)

            # extract aligned face chips
            imgc = detector.extract_image_chips(imgc, points, 255, 0.37)

        for chip in imgc:
            cv2.imwrite(outdir + name, chip)


def align_faces(dir, outdir):
    dir = os.path.expanduser(dir)
    outdir = os.path.expanduser(outdir + '/')

    procs = [Process(target=align, args =(i, dir, outdir)) for i in range(CPU)]

    for p in procs:
        p.start()
    for p in procs:
        p.join()



def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('dir', type=str, help='dir')
    parser.add_argument('outdir', type=str, help='dir')
    return parser.parse_args(argv)


if __name__ == '__main__':
    argv = parse_arguments(sys.argv[1:])
    align_faces(argv.dir, argv.outdir)
