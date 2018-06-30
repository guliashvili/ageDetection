CPU = 1


#import urllib.request
import requests
# import urllib
from multiprocessing import Pool
import multiprocessing
import time
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
from multiprocessing import Process, Lock

def gm(link):
    link = link.split('/images/M/')[1]
    link = link.split('@@._V1_')[0]
    link = link.split('@._V1_')[0]

    return link


lst = json.loads(open('data.txt', 'r').read())
lst = {list(elem.keys())[0]:list(elem.values())[0] for elem in lst}

num_of_pic = 0
for _, value in lst.items():
    num_of_pic += len(value[1])
print(num_of_pic)


def doit(img, output_filename, detector):

    # run detector
    results = detector.detect_face(img)


    if results is not None:

        points = results[1]
        if len(points) != 1:
            return False

        # extract aligned face chips
        chips = detector.extract_image_chips(img, points, 255, 0.37)
        for chip in chips:
            cv2.imwrite(output_filename, chip)


items = list(lst.items())[:10]
le = len(items)


def download(i):
    detector = MtcnnDetector(model_folder='model', ctx=mx.cpu(0), num_worker = 10 , accurate_landmark = False)

    for item in items[int(le * i / CPU): min(le, int(le * (i + 1) / CPU)) ]:
        id = item[0]
        value = item[1]

        sex = value[0]
        for link, age in value[1]:

            while True:
                try:
                    imgcA = requests.get(link)
                    if imgcA.status_code != requests.codes.ok:
                        print('oh1')
                        raise Exception('ax')
                    imgc = imgcA.content
                    break
                except:
                    print('oh2')
                    time.sleep(60)
                    continue

            x = np.fromstring(imgc, dtype='uint8')

            #decode the array into an image
            img = cv2.imdecode(x, cv2.IMREAD_UNCHANGED)
            doit(img, "imgs/{}_{}_{}{}.jpg".format(age, sex, id, gm(link)), detector)



procs = [Process(target=download, args = (i,)) for i in range(CPU)]
for p in procs:
    p.start()
for p in procs:
    p.join()
