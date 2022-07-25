#!/usr/bin/env python3
# coding: utf8

"""
python3 Rfactor_pdb.py -i refine_param_lys_r0096_basic_cal_masked_016.pdb -o r0096_basic_cal_masked_016_Rfactors.png

python3 Rfactor_pdb.py -i refine_param_lys_p8snr5_sph_016.pdb refine_param_lys_p8snr6_check_peaks_sph_016.pdb refine_param_lys_p8snr6_sph_016.pdb refine_param_lys_p8snr8_sph_016.pdb refine_param_lys_p9_sph_016.pdb refine_param_lys_grep_Alireza_w_sph_016.pdb -o cheetah_Rfacrors.png


python3 Rfactor_pdb.py -i refine_param_lys_r0096_basic_cal_wo_own_mask_016.pdb refine_param_lys_r0096_basic_cal_masked_016.pdb refine_param_lys_r0096_pc_ff_blc-set-min_wo_own_mask_016.pdb refine_param_lys_r0096_pc_ff_blc-set-min_masked_016.pdb refine_param_lys_r0096_pc_ff_wo_own_mask_016.pdb refine_param_lys_r0096_pc_ff_masked_016.pdb -o proc_Rfactors.png

"""


import os
import sys

import shutil

import matplotlib.pyplot as plt
import argparse

from itertools import groupby, cycle 
from cycler import cycler


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i', nargs='+', type=str, help="Input stream file")
    parser.add_argument('-o', type=str, help='Output png file')
    return parser.parse_args()


def parsing_pdb(input_pdb):
    bins = []
    rwork = []
    rfree = []
    res_mean = []

    with open(input_pdb, 'r') as pdb:
        reading_rfactors = False
        for line in pdb:
            if line.startswith('REMARK   3   BIN  RESOLUTION RANGE  COMPL.    NWORK NFREE   RWORK  RFREE  CCWORK CCFREE'):
                reading_rfactors = True
            elif reading_rfactors:
                # REMARK   3   BIN  RESOLUTION RANGE  COMPL.    NWORK NFREE   RWORK  RFREE  CCWORK CCFREE
                # REMARK   3     1 19.7514 -  3.5490    1.00     1461   160  0.2385 0.2454   0.855  0.845
                #   BIN  low res    high res  COMPL.    NWORK NFREE   RWORK  RFREE  CCWORK CCFREE
                # 3  1     19.7514    3.5490    1.00     1461   160  0.2385 0.2454   0.855  0.845
                tmp = line.replace('REMARK','').replace('-', '')
                tmp = tmp.split()
                if len(tmp) == 1:
                    reading_rfactors = False
                    break
                else:
                    bins.append(int(tmp[1]))
                    res_mean.append(round((float(tmp[2]) + float(tmp[3]))/2, 4))
                    rfree.append(float(tmp[-3]))
                    rwork.append(float(tmp[-4]))
    return bins, res_mean, rwork, rfree



if __name__ == "__main__":
    args = parse_cmdline_args()
    input_files = args.i
    output_fig_name = args.o
    
    set_of_colours = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    colours_for_png = set_of_colours[:len(input_files)]
    
    current_path = os.getcwd()
    path_to_plots = os.path.join(current_path, 'plots_Rfactor')

    if not os.path.exists(path_to_plots):
        os.mkdir(path_to_plots)
    
    f1, ax = plt.subplots(nrows=2, ncols=2, figsize=(20,20), constrained_layout=True)
    cy = cycler('color', colours_for_png)
    ax[0][0].set_prop_cycle(cy)
    ax[0][1].set_prop_cycle(cy)
    ax[1][0].set_prop_cycle(cy)
    ax[1][1].set_prop_cycle(cy)


    for input_pdb in input_files:
        bins, res_mean, rwork, rfree = parsing_pdb(input_pdb)
        print(res_mean[1:])

        ax[0][0].plot(bins, rwork, marker='.', label="RWORK(BIN) of {}".format(input_pdb.split('.')[0]))
        ax[0][1].plot(bins, rfree, marker='.', label="RFREE(BIN) of {}".format(input_pdb.split('.')[0]))
        ax[1][0].plot(res_mean[1:], rwork[1:], marker='.', label="RWORK(RESOLUTION) of {}".format(input_pdb.split('.')[0]))
        ax[1][1].plot(res_mean[1:], rfree[1:], marker='.', label="RFREE(RESOLUTION) of {}".format(input_pdb.split('.')[0]))

   

    ax[0][0].legend(loc='best')
    ax[0][1].legend(loc='best')
    ax[1][0].legend(loc='best')
    ax[1][1].legend(loc='best')
    

    ax[0][0].set_xlabel('BINS')
    ax[0][1].set_xlabel('BINS')
    ax[1][0].set_xlabel('RESOLUTION')
    ax[1][1].set_xlabel('RESOLUTION')

    ax[0][0].set_ylabel('RWORK')
    ax[0][1].set_ylabel('RFREE')
    ax[1][0].set_ylabel('RWORK')
    ax[1][1].set_ylabel('RFREE')


    f1.savefig(output_fig_name)
    shutil.move(output_fig_name, path_to_plots)