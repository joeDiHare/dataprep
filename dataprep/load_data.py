#! /usr/bin/env python

"""Loading data (PART 2)"""

import dicom
from dicom.errors import InvalidDicomError

import numpy as np
from PIL import Image, ImageDraw

from dataprep.dataprep.parse_input import *

import sys, os
import pandas as pd

class LoadData(object):


    def __init__(self, width_dicom=256, height_dicom=256):
        self.width_dicom = width_dicom
        self.height_dicom = height_dicom


    def split_data_method(self, L, split_data):
        """ Check that the split_data paramter is entered correctly and split the data accordingly
        :param L: len of data
        :param split_data: how ti split the database. List [float a, float b], where a is the number of samples for training, and b the number of samples for validation
        :return: number of samples for training, validation, and testing.
        """

        perc_train = int (split_data[0]*L)
        perc_valid = int(split_data[1]*L)
        perc_test = L - perc_train - perc_valid

        ####################
        # Input sanity check
        if perc_train+perc_valid+perc_test != L:
            ValueError('Data split not correct: split_data[0] and split_data[1] must sum to 1 (currently split_data = {})'.format(split_data))
        if split_data[0]>1 or split_data[0]<0:
            ValueError('split_data[0] must be between 0 and 1 (currently split_data[0] = {})'.format(split_data[0]))
        if split_data[1]>1 or split_data[1]<0:
            ValueError('split_data[1] must be between 0 and 1 (currently split_data[0] = {})'.format(split_data[1]))
        ####################

        return perc_train, perc_valid, perc_test


    def load_data_generator(self, data, batch_size=8, split_data=[.7,.1], random_order=True):
        """
        Generator for data in batches
        :param data:
        :param batch_size:
        :return:
        """
        L = len(data)

        perc_train, perc_valid, perc_test = self.split_data_method(L, split_data)

        if random_order:
            # permutate data tor randomize it
            data = data[np.random.permutation(np.arange(len(data)))]
            # np.random.shuffle(arrdataay)

        start = 0
        while True:
            stop = start + batch_size
            diff = stop - data.shape[0]
            if diff <= 0:
                batch = data[start:stop]
                start += batch_size
            else:
                batch = np.concatenate((data[start:], data[:diff]))
                start = diff
            batch = batch.astype(np.float32)
            yield batch

