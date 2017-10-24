#! /usr/bin/env python

"""Parsing code for DICOMS and contour files"""

import dicom
from dicom.errors import InvalidDicomError

import numpy as np
from PIL import Image, ImageDraw

# added to make the script executable from console
import sys, os
import pandas as pd

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
        # print(dcm.Rows, dcm.Columns)
        return dcm_dict, dcm.Rows, dcm.Columns

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

def sanitize_input():
    #ToDo
    """Attempt to spot misclassified samples by checking that i-contours are inside o-contours.
    This is achieved by checking that, for a given x-coordinate, the followig is true (y1_o < y1_i < y2_i < y2_i) within some tolerance value.
    Method 2: check that the Area for o-contours is greater than i-contours.
    :return:
    """

def get_data():
    """ Fetch and bind data into dictionary
     Side note: I could have used a Data Class to do this, but dictionaries in python are just as efficient and have built-in routines to add/remove data.

    :param data_directory: where the data is located
    :return: dict containing i-contour, o-contour, mask, dicom_image, and nner, outerBoolean mask of shape (height, width)
    """

    if sys.argv[0] is None:
        data_directory = '../data'
    data_directory = '../data'
    # print(sys.argv)

    #####################
    # Test the data input
    #####################
    # test_files(data_directory)

    df_IDs = get_IDs(data_directory)

    data, data_binds = dict(), []
    filedicom = ''
    i_contour_directory, i_contour_filename = data_directory + '/contourfiles/{}/i-contours/','IM-0001-{}-icontour-manual.txt'
    o_contour_directory, o_contour_filename = data_directory + '/contourfiles/{}/o-contours/','IM-0001-{}-ocontour-manual.txt'
    dicom_directory,     dicom_filename     = data_directory + '/dicoms/{}/', '{}.dcm'
    for _ in range(len(df_IDs.patient_id)):
        print('Subject data',_)
        list_dir_i_contour = os.listdir(i_contour_directory.format(df_IDs.original_id[_]))
        list_dir_o_contour = os.listdir(o_contour_directory.format(df_IDs.original_id[_]))
        # print(list_dir_i_contour, list_dir_o_contour)
        tmp_dict, ind = dict(), 0
        for s in list_dir_i_contour:
            no = s.split('-')[2]

            # File locations
            i_contour_location = i_contour_directory.format(df_IDs.original_id[_])+ i_contour_filename.format(no)
            o_contour_location = o_contour_directory.format(df_IDs.original_id[_])+o_contour_filename.format(no)
            img_dicom_location = dicom_directory.format(df_IDs.patient_id[_])+dicom_filename.format(no.strip('0'))

            # Parse data
            i_contour = parse_contour_file(i_contour_location)
            o_contour = parse_contour_file(o_contour_location) if o_contour_location in list_dir_o_contour else None
            img, width, height = parse_dicom_file(img_dicom_location)
            mask = poly_to_mask(i_contour, width=width, height=height)

            ###########
            # bind data into one dictionary
            ind += 1
            tmp_dict[ind] = {'i_contour': i_contour,
                             'o_contour': o_contour,
                             'mask' : mask,
                             'dicom': img,
                             'frame': no,
                             'attributes': {
                                 'file_dicom': filedicom,
                                 'i_contour_location': i_contour_location,
                                 'o_contour_location': o_contour_location,
                                 'img_dicom_location': img_dicom_location,
                                 'width': width,
                                 'height': height,
                                 },
                             }
            # list of files locations
            data_binds.append([img_dicom_location, i_contour_location])
        data[_] = tmp_dict

    # return data, data_binds




if __name__ == '__main__':
    # main should return 0 for success, something else (usually 1) for error.
    sys.exit(get_data())