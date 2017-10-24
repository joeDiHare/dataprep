#! /usr/bin/env python

"""Parsing code for DICOMS and contour files"""

import dicom
from dicom.errors import InvalidDicomError

import numpy as np
from PIL import Image, ImageDraw

# added to make the script executable from console
import sys, os
import pandas as pd
from dataprep.dataprep.tests import test_files

def parse_contour_file(filename):
    """Parse the given contour filename

    :param filename: filepath to the contourfile to parse
    :return: list of tuples holding x, y coordinates of the contour
    """

    coords_lst = []

    with open(filename, 'r') as infile:
        for line in infile:
            coords = line.strip().split()

            x_coord = float(coords[0])
            y_coord = float(coords[1])
            coords_lst.append((x_coord, y_coord))

    return coords_lst


def parse_dicom_file(filename):
    """Parse the given DICOM filename

    :param filename: filepath to the DICOM file to parse
    :return: dictionary with DICOM image data
    """

    try:
        dcm = dicom.read_file(filename)
        dcm_image = dcm.pixel_array

        try:
            intercept = dcm.RescaleIntercept
        except AttributeError:
            intercept = 0.0
        try:
            slope = dcm.RescaleSlope
        except AttributeError:
            slope = 0.0

        if intercept != 0.0 and slope != 0.0:
            dcm_image = dcm_image*slope + intercept
        dcm_dict = {'pixel_data' : dcm_image}
        return dcm_dict
    except InvalidDicomError:
        #ToDo propagate the error
        raise
        # return None


def poly_to_mask(polygon, width, height):
    """Convert polygon to mask

    :param polygon: list of pairs of x, y coords [(x1, y1), (x2, y2), ...]
     in units of pixels
    :param width: scalar image width
    :param height: scalar image height
    :return: Boolean mask of shape (height, width)
    """

    # http://stackoverflow.com/a/3732128/1410871
    img = Image.new(mode='L', size=(width, height), color=0)
    ImageDraw.Draw(img).polygon(xy=polygon, outline=0, fill=1)
    mask = np.array(img).astype(bool)
    return mask


def get_IDs(data_directory, id_file_name = '/link.csv'):
    """Read the ID csv

    :param data_directory: where the data is stored
    :param id_file_name: file name
    :return dataframe
    """

    filename = data_directory + id_file_name
    return pd.read_csv(filename)


def main():
    """ Fetch and bind data into dictionary
     Side note: I could have used a Data Class to do this, but dictionaries in python are just as efficient and have built-in routines to add/remove data.

    :param data_directory: where the data is located
    :return: dict containing i-contour, o-contour, mask, dicom_image, and nner, outerBoolean mask of shape (height, width)
    """

    if sys.argv[0] is None:
        data_directory = 'data'

    #####################
    # Test the data input
    #####################
    # test_files(data_directory)

    df_IDs = get_IDs(data_directory)

    d = dict()
    filedicom = ''
    i_contour_directory, i_contour_filename = data_directory + '/contourfiles/{}/i-contours/','IM-0001-{}-icontour-manual.txt'
    o_contour_directory, o_contour_filename = data_directory + '/contourfiles/{}/o-contours/','IM-0001-{}-ocontour-manual.txt'
    dicom_directory,     dicom_filename     = data_directory + '/dicoms/{}/', '{},dcm'
    for _ in df_IDs.size:
        list_dir_i_contour = os.listdir(i_contour_directory.format(df_IDs.original_id[_]))
        for s in list_dir_i_contour:
            no = s.split('-')[2]

            i_contour = parse_contour_file(i_contour_directory.format(df_IDs.original_id[_])+
                                           i_contour_filename.format(no))
            o_contour = parse_contour_file(o_contour_directory.format(df_IDs.original_id[_])+
                                           o_contour_filename.format(no))
            mask = poly_to_mask(i_contour, width=350, height=350)
            img = parse_dicom_file(dicom_directory.format(df_IDs.patient_id[_])+dicom_filename.format(no.strip('0')))

        ###########
        # bind data into one dictionary
        d[_] = {'i_contour': i_contour,
                'o_contour': o_contour,
                'mask' : mask,
                'dicom': img,
                'attributes': {
                    'file_dicom': filedicom,
                    },
                }



if __name__ == '__main__':
    # main should return 0 for success, something else (usually 1) for error.
    sys.exit(main())