import os, sys
import argparse
import mxnet as mx

def main(args):
    if sys.version_info[0] >= 3:
        from urllib.request import urlretrieve
    else:
        from urllib import urlretrieve

    def download(url):
        filename = url.split("/")[-1]
        print(filename)
        if not os.path.exists(filename):
            urlretrieve(url, filename)




    def get_iterators(batch_size, data_shape=(3, 224, 224)):
        train = mx.io.ImageRecordIter(
            path_imgrec         = args.lst + 'train.rec',
            data_name           = 'data',
            label_name          = 'softmax_label',
            batch_size          = batch_size,
            data_shape          = data_shape,
            shuffle             = True,
            rand_crop           = False,
            rand_mirror         = True)
        val = mx.io.ImageRecordIter(
            path_imgrec         = args.lst + 'valid.rec',
            data_name           = 'data',
            label_name          = 'softmax_label',
            batch_size          = batch_size,
            data_shape          = data_shape,
            rand_crop           = False,
            rand_mirror         = False)
        test = mx.io.ImageRecordIter(
            path_imgrec         = args.lst + 'test.rec',
            data_name           = 'data',
            label_name          = 'softmax_label',
            batch_size          = batch_size,
            data_shape          = data_shape,
            rand_crop           = False,
            rand_mirror         = False)
        return (train, val, test)


    def get_model(prefix, epoch):
        download(prefix+'-symbol.json')
        download(prefix+'-%04d.params' % (epoch,))

    get_model('http://data.mxnet.io/models/imagenet/resnet/50-layers/resnet-50', 0)
    sym, arg_params, aux_params = mx.model.load_checkpoint('resnet-50', 0)

    def get_fine_tune_model(symbol, arg_params, num_classes, layer_name='flatten0'):
        """
        symbol: the pretrained network symbol
        arg_params: the argument parameters of the pretrained model
        num_classes: the number of classes for the fine-tune datasets
        layer_name: the layer name before the last fully-connected layer
        """
        all_layers = symbol.get_internals()
        net = all_layers[layer_name+'_output']
        net = mx.symbol.FullyConnected(data=net, num_hidden=num_classes, name='fc1')
        net = mx.symbol.SoftmaxOutput(data=net, name='softmax')
        new_args = dict({k:arg_params[k] for k in arg_params if 'fc1' not in k})
        return (net, new_args)


    import logging
    head = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=head)

    def fit(symbol, arg_params, aux_params, train, val, test, batch_size, num_gpus):
        devs = [mx.gpu(i) for i in range(num_gpus)]
        mod = mx.mod.Module(symbol=symbol, context=devs)
        mod.fit(train, val,
            num_epoch=8,
            arg_params=arg_params,
            aux_params=aux_params,
            allow_missing=True,
            batch_end_callback = mx.callback.Speedometer(batch_size, 10),
            kvstore='device',
            optimizer='sgd',
            optimizer_params={'learning_rate':0.01},
            initializer=mx.init.Xavier(rnd_type='gaussian', factor_type="in", magnitude=2),
            eval_metric='acc')
        metric = mx.metric.Accuracy()
        return mod.score(test, metric)

    num_classes = 100
    batch_per_gpu = 128
    num_gpus = args.num_gpus

    (new_sym, new_args) = get_fine_tune_model(sym, arg_params, num_classes)

    batch_size = batch_per_gpu * num_gpus
    (train, val, test) = get_iterators(batch_size)
    mod_score = fit(new_sym, new_args, aux_params, train, val, test, batch_size, num_gpus)
    print(mod_score)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('lst', type=str, help='Train lst')
    parser.add_argument('num_gpus', type=int,
                        help='num_gpus', default=-1)
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
