import urllib.request
# import urllib
from multiprocessing import Pool
import multiprocessing
import time
import json
import sys

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

def download(item):
    id = item[0]
    value = item[1]

    sex = value[0]
    for link, age in value[1]:
        urllib.request. vurlretrieve(link, "imgs/{}_{}_{}{}.jpg".format(age, sex, id, gm(link)))

p = Pool(50)
p.map(download, lst.items())