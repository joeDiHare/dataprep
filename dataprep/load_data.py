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

    def load_data_generator(self, array, batch_size):
        """
        Generator for data in batches
        :param array:
        :param batch_size:
        :return:
        """
        start = 0
        while True:
            stop = start + batch_size
            diff = stop - array.shape[0]
            if diff <= 0:
                batch = array[start:stop]
                start += batch_size
            else:
                batch = np.concatenate((array[start:], array[:diff]))
                start = diff
            batch = batch.astype(np.float32)
            yield batch

