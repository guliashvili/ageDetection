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


def pad(img, margin):
    margin = int(margin / 2) + 1
    return np.pad(img, ((margin, margin), (margin, margin), (0, 0)), 'constant'), margin


def align(img):
    imgSize = (112, 96)

    x_ = [30.2946, 65.5318, 48.0252, 33.5493, 62.7299]
    y_ = [51.6963, 51.5014, 71.7366, 92.3655, 92.2041]

    src = np.array(zip(x_, y_)).astype(np.float32).reshape(1, 5, 2)

    alignedFaces = []

    # there might be more than one faces, hence
    # multiple sets of points
    for pset in points:
        img2 = img.copy()

        pset_x = pset[0:5]
        pset_y = pset[5:10]

        dst = np.array(zip(pset_x, pset_y)).astype(np.float32).reshape(1, 5, 2)

        transmat = cv2.estimateRigidTransform(dst, src, False)

        out = cv2.warpAffine(img2, transmat, (imgSize[1], imgSize[0]))

        alignedFaces.append(out)


def to_rgb(img):
    w, h = img.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 0] = ret[:, :, 1] = ret[:, :, 2] = img
    return ret


def main(args):
    sleep(random.random())
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

    minsize = 20  # minimum size of face
    threshold = [0.6, 0.7, 0.7]  # three steps's threshold
    factor = 0.709  # scale factor

    nrof_images_total = 0
    nrof_successfully_aligned = 0
    for image_path in dataset:
        nrof_images_total += 1
        filename = os.path.splitext(os.path.split(image_path)[1])[0]
        output_filename = os.path.join(output_dir, filename + '.png')
        if math.floor(100.0 * nrof_images_total / len(dataset)) != math.floor(
                100.0 * (nrof_images_total - 1) / len(dataset)):
            print(math.floor(100.0 * nrof_images_total / len(dataset)), '%')

        if not os.path.exists(output_filename):
            try:
                img = misc.imread(image_path)
            except (IOError, ValueError, IndexError) as e:
                errorMessage = '{}: {}'.format(image_path, e)
                print(errorMessage)
            else:
                if img.ndim < 2:
                    print('Unable to align "%s"' % image_path)
                    # text_file.write('%s\n' % (output_filename))
                    continue
                if img.ndim == 2:
                    img = to_rgb(img)
                img = img[:, :, 0:3]
                print('shape', img.shape)
                print('img', img)

                bounding_boxes, points = detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold,
                                                                 factor)
                print(image_path, '\n', bounding_boxes, '\n', points)
                nrof_faces = bounding_boxes.shape[0]
                if nrof_faces == 1:
                    img, padd = pad(img, args.margin)

                    points = points[0]
                    det = bounding_boxes[:, 0:4]

                    points += padd
                    det += padd


                    img_size = np.asarray(img.shape)[0:2]
                    det = np.squeeze(det)
                    bb = np.zeros(4, dtype=np.int32)
                    bb[0] = det[0] - args.margin / 2
                    bb[1] = det[1] - args.margin / 2
                    bb[2] = det[2] + args.margin / 2
                    bb[3] = det[3] + args.margin / 2
                    cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
                    scaled = misc.imresize(cropped, (args.image_size, args.image_size), interp='bilinear')
                    nrof_successfully_aligned += 1
                    misc.imsave(output_filename, scaled)


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
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
