from __future__ import print_function, division

from torch import optim
from utils import resume
from utils.trainer import Trainer

import utils.classmetric as classmetric
import torch.nn as nn
import torch
from torch.utils import data
from utils.image import tiff_to_nd_array
import numpy as np
import torch
import torchvision.transforms as transforms
import os
import pwd
import csv
import pandas as pd
import torch.utils.model_zoo as model_zoo

import os.path as pt
from models.unet_models import UNet

from utils.dataloader import train_xbd_data_loader
from utils.dataloader import val_xbd_data_loader

from models.model_fns import * 

from utils import resume

from torch.autograd import Variable
import cv2


def init_network(experiment, n_classes, num_epochs, finetune):
    if experiment == 'pre_post':
        network = siam_unet_conc()
    elif experiment == 'pre' or experiment == 'post':
        network = unet_basic_vhr()
    else:
        raise ValueError("Please insert a valid experiment id. Valid experiments are 'pre', 'post', 'pre_post'")

    if torch.cuda.is_available():
        network = network.cuda()
 	network = nn.DataParallel(network).cuda()

    if finetune:
	finetune = finetune + "/epoch_{:02}_classes_{:02}.pth".format(num_epochs, n_classes)
        state = resume(finetune, network, None)
    else:
	finetune = RESULTS_PATH +  "/epoch_{:02}_classes_{:02}.pth".format(num_epochs, n_classes)     
        state = resume(finetune, network, None)

    print('Loaded: ', finetune)
    return network


RESULTS_PATH = os.environ["RESULTS_PATH"] 
TESTDATA_PATH = os.environ["TESTDATA_PATH"] 
def main(
        batch_size,
        nworkers,
        datadir,
        outdir,
	num_epochs,
        finetune,
        n_classes,
        experiment,
        write
):

    np.random.seed(0)
    network = init_network(experiment, n_classes, num_epochs, finetune)
	
    if not datadir:
        datadir = TESTDATA_PATH

    val = val_xbd_data_loader(datadir, batch_size=batch_size, num_workers=nworkers, mode='test', experiment=experiment)

    metric = classmetric.ClassMetric()
    loss_str_list = []
    metric_dicts = []
    network.eval()

    for iteration, data in enumerate(val):	
        tile, input, target_tensor = data
        target = tensor_to_variable(target_tensor[0])
        
        output_raw = network.forward(input) 
            
        # force the output label map to match the target dimensions
        _, h, w = target.shape
        output_raw = torch.nn.functional.upsample(output_raw, size=(h, w), mode='bilinear')
         
        # Normalize
        if n_classes == 1:
            output = output_raw
        else:
        #    soft = nn.Softmax2d()
	#    output = soft(output_raw)
            output = torch.exp(output_raw)
	#     output = output_raw
 
        train_metric = metric(target, output)
        
        if not write:
            metric_dicts.append(train_metric)
            continue

        loss_str_list.append("Input ID: {}; Metric: {} ".format(tile, str(train_metric)))

        # convert zo W x H x C
        if torch.cuda.is_available():
            prediction = output.cpu().data[0] 
            target = target.cpu().data[0]
        else:
            prediction = output.data[0] 
            target = target.data[0] 
        
        # Remove extra dim
        if n_classes == 1:
            prediction_img = prediction.numpy()
        else:
            prediction_img = np.argmax(prediction, prediction.shape.index(n_classes)).numpy()

        target_img = target.numpy()
 
        if not os.path.exists(finetune + "/img"):
            os.makedirs(finetune + "/img") 

        cv2.imwrite(finetune + "/img/{}_prediction_class_{:02}_{}.png".format(iteration, n_classes, tile[0].split('/')[-1].split('.')[0]), prediction_img*255)
        cv2.imwrite(finetune + "/img/{}_target_class_{:02}_{}.png".format(iteration, n_classes, tile[0].split('/')[-1].split('.')[0]), target_img*255)

        with open(finetune + "/MSEloss.csv", "w") as output:
            writer = csv.writer(output, delimiter=';', lineterminator='\n')
            for val in loss_str_list:
                writer.writerow([val])

    if not write:
        return (train_metric, network)
 

def tensor_to_variable(tensor):
    if torch.cuda.is_available():
        return Variable(tensor).cuda()
    else:
        return Variable(tensor)

if __name__ == '__main__':
    import argparse

    text_type=str

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-b', '--batch-size',
        default=8,
        type=int,
        help='number of images in batch',
    )
    parser.add_argument(
	'-e', '--num-epochs', 
	default=10, 
	type=int, 
	help='number of epochs', 
    )	
    parser.add_argument(
        '-w', '--workers',
        default=1,
        type=int,
        help='number of workers',
    )
    parser.add_argument(
        '-o', '--outdir',
        default='.',
        type=text_type,
        help='output directory',
    )
    parser.add_argument(
        '-m', '--num-mini-batches',
        default=1,
        type=int,
        help='number of mini batches per batch',
    )
    parser.add_argument(
        '-p', '--datadir',
        default='',
        type=text_type,
        help='ILSVRC12 dir',
    )
    parser.add_argument(
        '-r', '--resume',
        type=text_type,
	default='',
        help='snapshot path',
    )
    parser.add_argument(
        '-f', '--finetune',
        type=text_type,
	default='',
        help='finetune path',
    )
    parser.add_argument(
        '-c', '--n_classes',
        default = 2,
        type = int,
        help = 'prediction type: =1: regression />1: classification',
    )
    parser.add_argument(
        '-x', '--experiment',
        default="PspBuildingsRGB",
        type=text_type,
        help='experiment name',
    )
    parser.add_argument(
	'-wr', '--write',
        default=True,
        type=bool,
        help='must be set to True except when used in best_epochs.py' 
    )

    args, unknown = parser.parse_known_args()
    try:
        main(
            args.batch_size,
            args.workers,
            args.datadir,
            args.outdir,
	    args.num_epochs,
            args.finetune,
            args.n_classes,
            args.experiment,
            args.write,
        )
    except KeyboardInterrupt:
        pass
    finally:
        print()
