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

    def __init__(self, data_directory='./dataprep/data'):
        data, data_binds = get_data(data_directory)
        width_dicom = data[0]['attributes']['width']
        height_dicom = data[0]['attributes']['height']
        self.data = data
        self.data_bins = data_binds
        self.width_dicom = width_dicom
        self.height_dicom = height_dicom

    def split_data_method(self, L, split_data):
        """ ((Actually, I ended up not using this method))
        Check that the split_data parameter is entered correctly and split the data accordingly
        :param L: len of data
        :param split_data: how ti split the database. List [float a, float b], where a is the number of samples for training, and b the number of samples for validation
        :return: number of samples for training, validation, and testing.
        """

        perc_train = int (split_data[0]*L)
        perc_valid = int(split_data[1]*L)
        perc_test = L - perc_train - perc_valid

        # Input sanity check
        if perc_train+perc_valid+perc_test != L:
            ValueError('Data split not correct: split_data[0] and split_data[1] must sum to 1 (currently split_data = {})'.format(split_data))
        if split_data[0]>1 or split_data[0]<0:
            ValueError('split_data[0] must be between 0 and 1 (currently split_data[0] = {})'.format(split_data[0]))
        if split_data[1]>1 or split_data[1]<0:
            ValueError('split_data[1] must be between 0 and 1 (currently split_data[0] = {})'.format(split_data[1]))

        return perc_train, perc_valid, perc_test


    def load_data_generator(self, batch_size=8, random_order=True, split_data=[.7, .1]):
        """
        Generator for data in batches
        :param batch_size:
        :param split_data: used for a method that I eneded up not needing
        :return:
        """

        data = self.data

        # The data split is not necessary at this point.
        # perc_train, perc_valid, perc_test = self.split_data_method(len(data), split_data)

        # Create indeces and shuffle if required order is random (as per description)
        indeces = np.arange(len(data))
        if random_order:
            np.random.shuffle(indeces)

        # implement data generator
        start = 0
        while True:
            stop = start + batch_size
            diff = stop - len(data)
            if diff < 0:
                batch = indeces[start:stop]
                start += batch_size
            elif diff==0:
                if random_order:
                    np.random.shuffle(indeces)
                batch = indeces[start:stop]
                start += batch_size
            else:
                batch = np.concatenate((indeces[start:], indeces[:diff]))
                start = diff
            batch = batch.astype(np.float32)

            # bind data
            input, output = [], []
            for ind in batch:
                input.append(data[ind]['mask'])
                output.append(data[ind]['dicom'])

            yield np.array(input), np.array(output)
            # yield [indeces[int(k)] for k in batch], batch (this is useful for debugging)

