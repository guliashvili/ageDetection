import os, sys
import argparse
import mxnet as mx

def main(args):
    sym, arg_params, aux_params = mx.model.load_checkpoint(args.prefixin, 0)

    def get_fine_tune_model(symbol, arg_params, num_classes, layer_name='flatten0'):
        """
        symbol: the pretrained network symbol
        arg_params: the argument parameters of the pretrained model
        num_classes: the number of classes for the fine-tune datasets
        layer_name: the layer name before the last fully-connected layer
        """
        all_layers = symbol.get_internals()
        net = all_layers[layer_name+'_output']
        net = mx.symbol.FullyConnected(data=net, num_hidden=num_classes, name=args.problayer)
        net = mx.symbol.SoftmaxOutput(data=net, name=args.outlayer)

        new_args = dict({k:arg_params[k] for k in arg_params if args.problayer not in k})
        return (net, new_args)


    (new_sym, new_args) = get_fine_tune_model(sym, arg_params, args.num,  args.lastgoodlayer)
    mx.model.save_checkpoint(args.prefixout, 0, new_sym, new_args, aux_params)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('prefixin', type=str, help='prefix of base')
    parser.add_argument('prefixout', type=str, help='prefix of base')

    parser.add_argument('num', type=int, help='num classes')
    parser.add_argument('lastgoodlayer', type=str, help='last good lyer')
    parser.add_argument('problayer', type=str, help='huge prob weight layer name')
    parser.add_argument('outlayer', type=str, help='out lyer name')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
