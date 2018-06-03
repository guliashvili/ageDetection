import os
from os.path import join, dirname
import random


mypath = '/Users/gguli/Desktop/bachelor/MORPH_nonCommercial/'

csv = [x.split(',') for x in list(filter(None,open('/Users/gguli/Desktop/bachelor/MORPH_nonCommercial/morph_2008_nonCommercial.csv', 'r').read().split('\n')))[1:]]

csv = [(x[5],x[7], x[10]) for x in csv]

for gender, age, loc in csv:
    if not loc.endswith(".JPG"):
        raise Exception()

    cur_path = join(mypath, loc)

    filename = str(age) + '_' + str(gender) + '_' + str(random.randint(10**14, 10**15-1)) + '.JPG'
    next_path = join(dirname(cur_path), filename)

    print(cur_path, next_path)

    os.rename(cur_path, next_path)
