import os
import re
import random
import common
import argparse
import sys

def gen_lst(dir, clas, testc, trainc):
    dir = os.path.expanduser(dir)
    images = common.get_images(dir)
    with open(os.path.join(dir, 'lst_train.lst'), 'w') as train:
        with open(os.path.join(dir, 'lst_test.lst'), 'w') as test:
            with open(os.path.join(dir, 'lst_valid.lst'), 'w') as valid:
                for image in images:
                    name = os.path.basename(image)
                    print(name)
                    age, gender, num, _ = name.replace('.', '_').split('_')
                    if clas == 'age':
                        out = num + '\t' + age + '\t' + name
                    else:
                        out = num + '\t' + gender + '\t' + name

                    r = random.uniform(0, 1);
                    if r < testc:
                        f = test
                    elif r < testc + trainc:
                        f = train
                    else:
                        f = valid
                    f.write(out + '\n')


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('dir', type=str, help='dir')
    parser.add_argument('clas', type=str, help='age or sex')
    parser.add_argument('testc', type=float, help='test fraction')
    parser.add_argument('trainc', type=float, help='trainc fraction')
    return parser.parse_args(argv)


if __name__ == '__main__':
    argv = parse_arguments(sys.argv[1:])
    gen_lst(argv.dir, argv.clas, argv.testc, argv.trainc)