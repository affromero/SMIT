#!/usr/bin/ipython
from __future__ import print_function
import os
import argparse
from data_loader import get_loader
import glob
import math
import os, glob, ipdb, imageio, numpy as np, config as cfg, warnings, sys
from misc.utils import PRINT, config_yaml
warnings.filterwarnings('ignore')

__DATASETS__ = [
    os.path.basename(line).split('.py')[0]
    for line in glob.glob('datasets/*.py')
]


def _PRINT(config):
    string = '------------ Options -------------'
    PRINT(config.log, string)
    for k, v in sorted(vars(config).items()):
        string = '%s: %s' % (str(k), str(v))
        PRINT(config.log, string)
    string = '-------------- End ----------------'
    PRINT(config.log, string)


def main(config):
    from torch.backends import cudnn
    import torch
    from solver import Solver
    # For fast training
    cudnn.benchmark = True

    data_loader = get_loader(
        config.mode_data,
        config.image_size,
        config.batch_size,
        config.dataset_fake,
        config.mode,
        num_workers=config.num_workers,
        all_attr=config.ALL_ATTR,
        c_dim=config.c_dim)

    if config.mode == 'train':
        from train import Train
        Train(config, data_loader)
        from test import Test
        test = Test(config, data_loader)
        test(dataset=config.dataset_real)

    elif config.mode == 'test':
        from test import Test
        test = Test(config, data_loader)
        if config.DEMO_PATH:
            test.DEMO(config.DEMO_PATH)
        else:
            test(dataset=config.dataset_real)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Model hyper-parameters
    parser.add_argument(
        '--dataset_fake', type=str, default='CelebA', choices=__DATASETS__)
    parser.add_argument(
        '--dataset_real', type=str, default='', choices=[''] + __DATASETS__)
    parser.add_argument(
        '--mode', type=str, default='train', choices=['train', 'val', 'test'])
    parser.add_argument('--color_dim', type=int, default=3)
    parser.add_argument('--image_size', type=int, default=256)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--num_workers', type=int, default=4)
    parser.add_argument('--num_epochs', type=int, default=100)
    parser.add_argument('--num_epochs_decay', type=int, default=80)
    parser.add_argument(
        '--save_epoch', type=int, default=1)  #Save samples how many epochs
    parser.add_argument(
        '--model_epoch', type=int,
        default=2)  #Save models and weights every how many epochs
    parser.add_argument('--beta1', type=float, default=0.5)
    parser.add_argument('--beta2', type=float, default=0.999)
    parser.add_argument('--pretrained_model', type=str, default=None)

    # Path
    parser.add_argument('--log_path', type=str, default='./snapshot/logs')
    parser.add_argument(
        '--model_save_path', type=str, default='./snapshot/models')
    parser.add_argument(
        '--sample_path', type=str, default='./snapshot/samples')
    parser.add_argument('--DEMO_PATH', type=str, default='')
    parser.add_argument('--DEMO_LABEL', type=str, default='')

    # Generative
    parser.add_argument('--MultiDis', type=int, default=3, choices=[1, 2, 3])
    parser.add_argument('--g_conv_dim', type=int, default=64)
    parser.add_argument('--d_conv_dim', type=int, default=64)
    parser.add_argument('--g_repeat_num', type=int, default=6)
    parser.add_argument('--d_repeat_num', type=int, default=6)
    parser.add_argument('--g_lr', type=float, default=0.0001)
    parser.add_argument('--d_lr', type=float, default=0.0001)
    parser.add_argument('--lambda_cls', type=float, default=1.0)
    parser.add_argument('--lambda_rec', type=float, default=10.0)
    parser.add_argument('--lambda_idt', type=float, default=10.0)
    parser.add_argument('--lambda_mask', type=float, default=0.1)
    parser.add_argument('--lambda_mask_smooth', type=float, default=0.00001)

    parser.add_argument('--style_dim', type=int, default=20, choices=[20])
    parser.add_argument('--dc_dim', type=int, default=256, choices=[256])

    parser.add_argument('--d_train_repeat', type=int, default=1)

    # Misc
    parser.add_argument(
        '--use_tensorboard', action='store_true', default=False)
    parser.add_argument('--DELETE', action='store_true', default=False)
    parser.add_argument('--ALL_ATTR', type=int, default=0)
    parser.add_argument('--GPU', type=str, default='-1')

    # Step size
    parser.add_argument('--log_step', type=int, default=10)
    parser.add_argument('--sample_step', type=int, default=500)
    parser.add_argument('--model_save_step', type=int, default=10000)

    # Debug options
    parser.add_argument('--iter_test', type=int, default=1)
    parser.add_argument('--iter_style', type=int, default=40)
    parser.add_argument('--style_debug', type=int, default=4)
    parser.add_argument('--style_train_debug', type=int, default=9)
    parser.add_argument(
        '--style_label_debug',
        type=int,
        default=3,
        choices=[0, 1, 2, 3, 4, 5, 6, 7])

    config = parser.parse_args()

    if config.GPU == '-1':
        config.GPU = 'no_cuda'
        print("NO CUDA!")
    else:
        os.environ['CUDA_VISIBLE_DEVICES'] = config.GPU
        config.GPU = [int(i) for i in config.GPU.split(',')]

    config_yaml(config, 'datasets/{}.yaml'.format(config.dataset_fake))
    config = cfg.update_config(config)

    if config.mode == 'train':
        # Create directories if not exist
        if not os.path.exists(config.log_path): os.makedirs(config.log_path)
        if not os.path.exists(config.model_save_path):
            os.makedirs(config.model_save_path)
        if not os.path.exists(config.sample_path):
            os.makedirs(config.sample_path)
        org_log = os.path.abspath(os.path.join(config.sample_path, 'log.txt'))
        config.loss_plot = os.path.abspath(
            os.path.join(config.sample_path, 'loss.txt'))
        os.system('touch ' + org_log)

        of = 'a' if os.path.isfile(org_log) else 'wb'
        with open(org_log, of) as config.log:
            PRINT(config.log, ' '.join(sys.argv))
            _PRINT(config)
            main(config)
    else:
        main(config)
