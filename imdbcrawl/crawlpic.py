CPU = int(72/8 - 1)


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

def gm(link):
    link = link.split('/images/M/')[1]
    link = link.split('@@._V1_')[0]
    link = link.split('@._V1_')[0]

    return link

def get_items():
    items = json.loads(open('data.txt', 'r').read())
    items = {list(elem.keys())[0]:list(elem.values())[0] for elem in items}
    items = list(items.items())

    links = {}

    for item in items:
        id = item[0]
        value = item[1]

        for link, _ in value[1]:
            if link not in links:
                links[link] = 0
            links[link] += 1

    items2 = []
    for item in items:
        id = item[0]
        value = item[1]
        sex = value[0]

        for link, age in value[1]:
            if age < 5 or age > 100:
                continue
            if links[link] == 1:
                items2.append((id, link, age, sex))

    items = items2
    items2 = None
    links = None

    return items
def download(i):
    time.sleep(random.random()*20)
    detector = MtcnnDetector(model_folder='model', num_worker = 1 , accurate_landmark = False)
    items = get_items()
    print(len(items))

    le = len(items)
    items = items[int(le * i / CPU): min(le, int(le * (i + 1) / CPU))]

    processed = 0
    printed = 0

    for id, link, age, sex in items:
        try:
            #print(link,age)
            processed += 1
            if processed % 100 == 0:
                print("Thread {}: printed {} / {}".format(i, printed, processed))

            for _ in range(3):
                try:
                    imgc = requests.get(link)
                    if imgc.status_code != requests.codes.ok:
                        print('Thread {} oh1 {} link {}'.format(i, imgc.status_code, link))
                        raise Exception('ax')
                    imgc = imgc.content
                    break
                except:
                    print('Thread {} oh2 {} link {}'.format(i, imgc.status_code, link))
                    time.sleep(60)
                    continue

            imgc = np.fromstring(imgc, dtype='uint8')

            #decode the array into an image
            imgc = cv2.imdecode(imgc, cv2.IMREAD_UNCHANGED)
            if len(imgc.shape) == 2:
                imgc = cv2.cvtColor(imgc,cv2.COLOR_GRAY2RGB)
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
                    #cv2.imwrite("imgsl/{}_{}_{}_{}{}.jpg".format(len(points),age, sex, id, gm(link)), imgc)
                continue

                # extract aligned face chips
            imgc = detector.extract_image_chips(imgc, points, 255, 0.37)
            for chip in imgc:
                printed += 1
                cv2.imwrite("imgs/{}_{}_{}{}.jpg".format(age, sex, id, gm(link)), chip)

        except:
            print("Thread {} Unexpected error: {} {}".format(i, sys.exc_info()[0], traceback.format_exc()))


# download(0)

procs = [Process(target=download, args = (i,)) for i in range(int(CPU))]
for p in procs:
    p.start()
for p in procs:
    p.join()
