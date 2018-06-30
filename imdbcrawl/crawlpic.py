CPU = 2


#import urllib.request
import requests
# import urllib
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
from multiprocessing import Process

def gm(link):
    link = link.split('/images/M/')[1]
    link = link.split('@@._V1_')[0]
    link = link.split('@._V1_')[0]

    return link


def download(i):
    detector = MtcnnDetector(model_folder='model', num_worker = CPU , accurate_landmark = False)
    lst = json.loads(open('data.txt', 'r').read())
    lst = {list(elem.keys())[0]:list(elem.values())[0] for elem in lst}
    items = list(lst.items())
    le = len(items)
    items = items[int(le * i / CPU): min(le, int(le * (i + 1) / CPU))]

    processed = 0
    printed = 0

    for item in items:
        id = item[0]
        value = item[1]

        sex = value[0]
        for link, age in value[1]:
            if age < 5 or age > 100:
                continue
            print(link,age)
            processed += 1
            if processed % 1000 == 0:
                print("Thread {}: printed {} / {}".format(i, printed, processed))

            while True:
                try:
                    imgc = requests.get(link)
                    if imgc.status_code != requests.codes.ok:
                        print('oh1')
                        raise Exception('ax')
                    imgc = imgc.content
                    break
                except:
                    print('oh2')
                    time.sleep(60)
                    continue

            imgc = np.fromstring(imgc, dtype='uint8')

            #decode the array into an image
            imgc = cv2.imdecode(imgc, cv2.IMREAD_UNCHANGED)
            height, width, _ = imgc.shape
            if height + width > 1700:
                mult = min(0.5, 1000.0/max(height,width))
                imgc = cv2.resize(imgc, (0,0), fx=mult, fy=mult)

            # run detector
            results = detector.detect_face(imgc)
            if results is None:
                continue

            points = results[1]
            if len(points) != 1:
                cv2.imwrite("imgsl/{}_{}_{}_{}{}.jpg".format(len(points),age, sex, id, gm(link)), imgc)
                continue

            # extract aligned face chips
            imgc = detector.extract_image_chips(imgc, points, 255, 0.37)
            for chip in imgc:
                printed += 1
                cv2.imwrite("imgs/{}_{}_{}{}.jpg".format(age, sex, id, gm(link)), chip)


# download(0)

procs = [Process(target=download, args = (i,)) for i in range(CPU)]
for p in procs:
    p.start()
for p in procs:
    p.join()
