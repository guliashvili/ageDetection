import os, sys
import argparse
import mxnet as mx
import logging
head = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=head)

def main(args):
    def get_iterators(batch_size, data_shape=(3, 224, 224)):
        train = mx.io.ImageRecordIter(
            path_imgrec         = args.lst + 'train.rec',
            data_name           = 'data',
            label_name          = args.label,
            batch_size          = batch_size,
            data_shape          = data_shape,
            shuffle             = True,
            rand_crop           = False,
            rand_mirror         = True,
            prefetch_buffer = 10*args.num_gpus)
        val = mx.io.ImageRecordIter(
            path_imgrec         = args.lst + 'valid.rec',
            data_name           = 'data',
            label_name          = args.label,
            batch_size          = batch_size,
            data_shape          = data_shape,
            rand_crop           = False,
            rand_mirror         = False,
            prefetch_buffer = 10 * args.num_gpus)
        test = mx.io.ImageRecordIter(
            path_imgrec         = args.lst + 'test.rec',
            data_name           = 'data',
            label_name          = args.label,
            batch_size          = batch_size,
            data_shape          = data_shape,
            rand_crop           = False,
            rand_mirror         = False,
            prefetch_buffer = 10*args.num_gpus)
        return (train, val, test)


    sym, arg_params, aux_params = mx.model.load_checkpoint(args.prefix, args.epochsave)


    def fit(symbol, arg_params, aux_params, train, val, test, batch_size, num_gpus):
        devs = [mx.gpu(i) for i in range(num_gpus)]
        mod = mx.mod.Module(symbol=symbol, context=devs)
        # metrics = ["acc", "rmse", "mae"]
        metrics = "mae"

        mod.fit(train, val,
            num_epoch=args.epoch,
            arg_params=arg_params,
            aux_params=aux_params,
            allow_missing=True,
            batch_end_callback = mx.callback.Speedometer(batch_size, 100),
            epoch_end_callback = mx.callback.do_checkpoint(args.prefix, 1),
            kvstore='KVStore',
            optimizer='sgd',
            optimizer_params={'learning_rate':0.01},
            initializer=mx.init.Xavier(rnd_type='gaussian', factor_type="in", magnitude=2),
            eval_metric=metrics)

        return mod.score(test, metrics)

    batch_per_gpu = args.batch_per_gpu
    num_gpus = args.num_gpus

    batch_size = batch_per_gpu * num_gpus
    (train, val, test) = get_iterators(batch_size)
    mod_score = fit(sym, arg_params, aux_params, train, val, test, batch_size, num_gpus)
    print(mod_score)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('prefix', type=str, help='prefix')
    parser.add_argument('epochsave', type=int, help='epoch to start from')
    parser.add_argument('epoch', type=int, help='num of epochs')
    parser.add_argument('lst', type=str, help='Train lst')
    parser.add_argument('label', type=str, help='output label name')
    parser.add_argument('num_gpus', type=int,
                        help='num_gpus', default=-1)
    parser.add_argument('batch_per_gpu', type=int,
                        help='num_gpus', default=64)
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
