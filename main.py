#!/usr/bin/ipython
import os
import argparse
from data_loader import get_loader
import glob
import math
import ipdb
import imageio
import numpy as np
import config as cfg
import warnings
import ipdb
import sys
warnings.filterwarnings('ignore')

#./main.py -- --GPU 3 --GRAY --BLUR --L1_LOSS --lambda_l1 5

def str2bool(v):
  return v.lower() in ('true')

def main(config):
  from torch.backends import cudnn
  import torch  
  # For fast training
  cudnn.benchmark = True

  # Create directories if not exist
  if not os.path.exists(config.log_path): os.makedirs(config.log_path)
  if not os.path.exists(config.model_save_path): os.makedirs(config.model_save_path)
  if not os.path.exists(config.sample_path): os.makedirs(config.sample_path)

  data_loader = get_loader(config.metadata_path, config.image_size,
                   config.image_size, config.batch_size, config.dataset, config.mode, \
                   color_jitter='COLOR_JITTER' in config.GAN_options, \
                   mean=config.mean, std=config.std, num_workers=config.num_workers)   


  if config.mode_train=='CLS':
    from solver_cls import Solver
  else:
    from solver import Solver

  solver = Solver(data_loader, config)

  if config.DISPLAY_NET and config.mode_train=='GAN': 
    solver.display_net(name='discriminator')
    solver.display_net(name='generator')
    return
  elif config.DISPLAY_NET and config.mode_train=='CLS': 
    solver.display_net(name='classifier')
    return

  if config.mode == 'train':
    solver.train()
    solver.test()
    # solver.test_cls()
  elif config.mode == 'val':
    solver.val()
  elif config.mode == 'test':
    solver.test()
    # solver.val_cls(load=True)
    # solver.test_cls()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  # Model hyper-parameters
  parser.add_argument('--dataset_fake',     type=str, default='EmotionNet', choices=['BP4D', 'EmotionNet', 'CelebA'])
  parser.add_argument('--dataset_real',     type=str, default='', choices=['','BP4D', 'EmotionNet', 'CelebA'])  
  parser.add_argument('--fold',             type=str, default='0')
  parser.add_argument('--mode_data',        type=str, default='normal', choices=['normal', 'aligned'])   
  parser.add_argument('--mode_train',       type=str, default='GAN', choices=['GAN', 'CLS'])   
  parser.add_argument('--mode',             type=str, default='train', choices=['train', 'val', 'test']) 
  parser.add_argument('--c_dim',            type=int, default=12)
  parser.add_argument('--image_size',       type=int, default=128)
  parser.add_argument('--batch_size',       type=int, default=16)
  parser.add_argument('--num_workers',      type=int, default=4)
  parser.add_argument('--num_epochs',       type=int, default=199)
  parser.add_argument('--num_epochs_decay', type=int, default=200)
  parser.add_argument('--beta1',            type=float, default=0.5)
  parser.add_argument('--beta2',            type=float, default=0.999)
  parser.add_argument('--pretrained_model', type=str, default=None)  

  # Path
  parser.add_argument('--metadata_path',    type=str, default='./data')
  parser.add_argument('--log_path',         type=str, default='./snapshot/logs')
  parser.add_argument('--model_save_path',  type=str, default='./snapshot/models')
  parser.add_argument('--sample_path',      type=str, default='./snapshot/samples')
  # parser.add_argument('--result_path', type=str, default='./snapshot/results')  

  # Generative 
  parser.add_argument('--g_conv_dim',       type=int, default=64)
  parser.add_argument('--d_conv_dim',       type=int, default=64)
  parser.add_argument('--g_repeat_num',     type=int, default=6)
  parser.add_argument('--d_repeat_num',     type=int, default=6)
  parser.add_argument('--g_lr',             type=float, default=0.0001)
  parser.add_argument('--d_lr',             type=float, default=0.0001)
  parser.add_argument('--lambda_cls',       type=float, default=1)
  parser.add_argument('--lambda_l1',        type=float, default=10.0)
  parser.add_argument('--lambda_rec',       type=float, default=10.0)
  parser.add_argument('--lambda_gp',        type=float, default=10.0)
  parser.add_argument('--d_train_repeat',   type=int, default=5)

  # Generative settings
  parser.add_argument('--GAN_options',  type=str, default='')
  # parser.add_argument('--COLOR_JITTER', action='store_true', default=False)  
  # parser.add_argument('--BLUR',         action='store_true', default=False)   
  # parser.add_argument('--GRAY',         action='store_true', default=False)  
  # parser.add_argument('--GOOGLE',       action='store_true', default=False)   
  # parser.add_argument('--PPT',          action='store_true', default=False)  
  # parser.add_argument('--VAL_SHOW',     action='store_true', default=False)  
  # parser.add_argument('--LSGAN',        action='store_true', default=False) 
  # parser.add_argument('--L1_LOSS',      action='store_true', default=False) 
  # parser.add_argument('--L2_LOSS',      action='store_true', default=False) 
  # parser.add_argument('--NO_TANH',      action='store_true', default=False) 
  # parser.add_argument('--NEW_GEN',      action='store_true', default=False) ################
  # parser.add_argument('--HINGE',        action='store_true', default=False) 
  # parser.add_argument('--SpectralNorm', action='store_true', default=False) 
  # parser.add_argument('--SAGAN',        action='store_true', default=False) 
  # parser.add_argument('--TTUR',         action='store_true', default=False) 

  # Classifier Settings
  parser.add_argument('--CLS_options',  type=str, default='')
  parser.add_argument('--DENSENET',        action='store_true', default=False)  
  parser.add_argument('--Generator_path',  type=str, default='')

  # Misc
  parser.add_argument('--use_tensorboard', action='store_true', default=False)
  parser.add_argument('--TEST',            action='store_true', default=False)  
  parser.add_argument('--DISPLAY_NET',     action='store_true', default=False) 
  parser.add_argument('--DELETE',          action='store_true', default=False)
  parser.add_argument('--GPU',             type=str, default='0')

  # Step size
  parser.add_argument('--log_step',        type=int, default=1000)
  parser.add_argument('--sample_step',     type=int, default=100000)
  parser.add_argument('--model_save_step', type=int, default=200000)

  config = parser.parse_args()
  config.GAN_options = config.GAN_options.split(',')
  config.CLS_options = config.CLS_options.split(',')
  os.environ['CUDA_VISIBLE_DEVICES'] = str(int(float(config.GPU)))

  config = cfg.update_config(config)

  if config.mode_train=='CLS':
    config.dataset = [config.dataset_fake, config.dataset_real]
  else:
    config.dataset = [config.dataset_fake]

  if config.mode=='train':
    file_log = 'logs/gpu{}_{}.txt'.format(config.GPU, config.mode_train)
  else:
    file_log = 'logs/dummy.txt'

  if not 'GOOGLE' in config.GAN_options:
    with open(file_log, 'wb') as config.log:
      print >> config.log, ' '.join(sys.argv)
      config.log.flush()
      print(config)
      main(config)
    # last_sample = sorted(glob.glob(config.sample_path+'/*.jpg'))[-1]
    # os.system('echo {0} | mail -s "Training done - GPU {1} free" -A "{0}" rv.andres10@uniandes.edu.co'.format(msj, config.GPU))
  else:
    main(config)
