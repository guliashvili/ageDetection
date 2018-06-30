"""Performs face alignment and stores face thumbnails in the output directory."""
# MIT License
#
# Copyright (c) 2016 David Sandberg
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os, sys, inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
from scipy import misc
import argparse
import tensorflow as tf
import numpy as np
import detect_face
import random
from time import sleep
import common
import math
import cv2


def pad(img, margin):
    margin = int(margin / 2) + 2
    return np.pad(img, ((margin, margin), (margin, margin), (0, 0)), 'constant'), margin


def align(img, pset):
    imgSize = (img.shape[0], img.shape[1])

    x_ = np.array([30.2946, 65.5318, 48.0252, 33.5493, 62.7299])
    y_ = np.array([51.6963, 51.5014, 71.7366, 92.3655, 92.2041])

    x_ = x_.dot(img.shape[1] / 86.0)
    y_ = y_.dot(img.shape[0] / 112.0)

    src = np.array(zip(x_, y_)).astype(np.float32).reshape(1, 5, 2)

    pset_x = pset[0:5]
    pset_y = pset[5:10]

    dst = np.array(zip(pset_x, pset_y)).astype(np.float32).reshape(1, 5, 2)

    transmat = cv2.estimateRigidTransform(dst, src, False)
    if transmat is None:
        transmat = cv2.estimateRigidTransform(dst, src, True)
    out = cv2.warpAffine(img, transmat, (imgSize[1], imgSize[0]))

    return out


def to_rgb(img):
    w, h = img.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 0] = ret[:, :, 1] = ret[:, :, 2] = img
    return ret

minsize = 20  # minimum size of face
threshold = [0.6, 0.7, 0.7]  # three steps's threshold
factor = 0.709  # scale factor


def get_face(margin, image_size, output_dir, i, al, image_path, pnet, rnet, onet):
    if hash(image_path) % al != i:
        return False
    filename = os.path.splitext(os.path.split(image_path)[1])[0]
    output_filename = os.path.join(output_dir, filename + '.png')

    if os.path.exists(output_filename):
        return False

    img = None
    try:
        img = misc.imread(image_path)
    except (IOError, ValueError, IndexError) as e:
        errorMessage = '{}: {}'.format(image_path, e)
        print(errorMessage)
        return False

    if img.ndim < 2:
        print('Unable to align "%s"' % image_path)
        # text_file.write('%s\n' % (output_filename))
        return False
    if img.ndim == 2:
        img = to_rgb(img)
    img = img[:, :, 0:3]

    bounding_boxes, points = detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold,factor)
    if bounding_boxes.shape[0] != 1:
        return False

    # img = align(img, points)
    # misc.imsave(output_filename, img)
    # return True

    img, padd = pad(img, args.margin)
    det = bounding_boxes[:, 0:4]
    det += padd

    img_size = np.asarray(img.shape)[0:2]
    det = np.squeeze(det)
    bb = np.zeros(4, dtype=np.int32)
    bb[0] = np.maximum(det[0] - margin / 2, 0)
    bb[1] = np.maximum(det[1] - margin / 2, 0)
    bb[2] = np.minimum(det[2] + margin / 2, img_size[1])
    bb[3] = np.minimum(det[3] + margin / 2, img_size[0])
    cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
    scaled = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
    misc.imsave(output_filename, scaled)
    return True


def main(args, i, al):
    sleep(random.random())
    print('thread ' + str(i) + ' runing out of ' + str(al))
    output_dir = os.path.expanduser(args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Store some git revision info in a text file in the log directory
    src_path, _ = os.path.split(os.path.realpath(__file__))
    dataset = common.get_images(args.input_dir)

    print('Creating networks and loading parameters')

    with tf.Graph().as_default():
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=args.gpu_memory_fraction)
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess.as_default():
            pnet, rnet, onet = detect_face.create_mtcnn(sess, None)

    nrof_images_total = 0
    nrof_successfully_aligned = 0
    for image_path in dataset:
        nrof_images_total += 1

        if math.floor(100.0 * nrof_images_total / len(dataset)) != math.floor(
                100.0 * (nrof_images_total - 1) / len(dataset)):
            print(math.floor(100.0 * nrof_images_total / len(dataset)), '%')
        if get_face(args.margin, args.img_size, args.output_dir, i, al, image_path, pnet, rnet, onet):
            nrof_successfully_aligned += 1

    print('Aligned %d/%d' % (nrof_successfully_aligned, nrof_images_total))


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('input_dir', type=str, help='Directory with unaligned images.')
    parser.add_argument('output_dir', type=str, help='Directory with aligned face thumbnails.')
    parser.add_argument('--image_size', type=int,
                        help='Image size (height, width) in pixels.', default=182)
    parser.add_argument('--margin', type=int,
                        help='Margin for the crop around the bounding box (height, width) in pixels.', default=44)
    parser.add_argument('--gpu_memory_fraction', type=float,
                        help='Upper bound on the amount of GPU memory that will be used by the process.', default=1.0)
    parser.add_argument('--thread', type=int,
                        help='Upper bound on the amount of GPU memory that will be used by the process.', default=10)
    return parser.parse_args(argv)

import threading

if __name__ == '__main__':
    argv = parse_arguments(sys.argv[1:])
    threads = [threading.Thread(target = main, args=(argv,i,argv.thread)) for i in range(argv.thread)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
