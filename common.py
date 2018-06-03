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


def gen_bin(dir, clas, testc, trainc):
    dir = os.path.expanduser(dir)
    images = get_images(dir)
    with open(os.path.join(dir, 'lst_train.lst'), 'w') as train:
        with open(os.path.join(dir, 'lst_test.lst'), 'w') as test:
            with open(os.path.join(dir, 'lst_valid.lst'), 'w') as valid:
                for image in images:
                    name = os.path.basename(image)
                    print(name)
                    age, gender, num, _ = name.replace('.', '_').split('_')
                    if clas == 'age':
                        out = num + ' ' + age + ' ' + name
                    else:
                        out = num + ' ' + gender + ' ' + name

                    r = random.uniform(0, 1);
                    if r < testc:
                        f = test
                    elif r < testc + trainc:
                        f = train
                    else:
                        f = valid
                    f.write(out)
