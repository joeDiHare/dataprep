#! /usr/bin/env python

"""Parsing code for DICOMS and contour files"""

import dicom
from dicom.errors import InvalidDicomError

import numpy as np
from PIL import Image, ImageDraw

# added to make the script executable from console
import sys, os
import pandas as pd

import warnings

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

        return dcm_dict, dcm.Rows, dcm.Columns

    except InvalidDicomError:
        # Propagate the error
        raise Exception('The DICOM image is not valid. Filename: {}'.format(filename))
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

def sanitize_input(i_contour, o_contour, i_contour_location, o_contour_location):
    """Attempt to detect errors in the data collection.
    Method1: For samples where both i-contours and o-contours are available, check that i-contours are withing o-contours.
    This is achieved by checking that, for a given x-coordinate, the following is true (y1_o < y1_i < y2_i < y2_i) within some tolerance value [tol].
    Method 2: check that the Area for o-contours is greater than i-contours [not implemented].
    :return:
    """
    if i_contour is None or o_contour is None:
        return
    i_c = np.abs(np.asarray(i_contour))
    o_c = np.abs(np.asarray(o_contour))
    d_i, d_o = dict(), dict()
    for _ in range(i_c.shape[1]):
        if i_c[_][0] in d_i:
            d_i[i_c[_][0]] = np.max(d_i[i_c[_][0]], i_c[_][1])
        else:
            d_i[i_c[_][0]] = i_c[_][1]
    for _ in range(o_c.shape[1]):
        if o_c[_][0] in d_o:
            d_o[o_c[_][0]] = np.max(d_o[o_c[_][0]], o_c[_][1])
        else:
            d_o[o_c[_][0]] = o_c[_][1]
    tol = 3
    for _ in d_i:
        if _ in d_o:
            if (max(d_o[_])-max(d_i[_])<tol or min(d_o[_])-min(d_i[_])<tol):
                warnings.warn('The following files did not pass the sanity check:\ni-contour: {}\no-contour: {}'.format(i_contour_location, o_contour_location))


def get_data(data_directory='/data'):
    """ Fetch and bind data into dictionary
     Side note: I could have used a Data Class to do this, but dictionaries in python are just as efficient and have built-in routines to add/remove data.

    :param data_directory: where the data is located
    :return: dict containing i-contour, o-contour, mask, dicom_image, and nner, outerBoolean mask of shape (height, width)
    """

    # if sys.argv[0] is None:
    #     data_directory = '../data'
    # data_directory = '../data'
    # print(sys.argv)
    print('cd (from parse_input.py):', os.getcwd())

    #####################
    # Test the data input
    #####################
    # test_files(data_directory)

    df_IDs = get_IDs(data_directory)

    data, data_binds = dict(), []
    ind=0
    filedicom = ''
    i_contour_directory, i_contour_filename = data_directory + '/contourfiles/{}/i-contours/','IM-0001-{}-icontour-manual.txt'
    o_contour_directory, o_contour_filename = data_directory + '/contourfiles/{}/o-contours/','IM-0001-{}-ocontour-manual.txt'
    dicom_directory,     dicom_filename     = data_directory + '/dicoms/{}/', '{}.dcm'
    for _ in range(len(df_IDs.patient_id)):
        print('Subject data',_)
        list_dir_i_contour = os.listdir(i_contour_directory.format(df_IDs.original_id[_]))
        list_dir_o_contour = os.listdir(o_contour_directory.format(df_IDs.original_id[_]))
        # print(list_dir_i_contour, list_dir_o_contour)
        # tmp_dict = dict()
        # ind = 0
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

            sanitize_input(i_contour, o_contour, i_contour_location, o_contour_location)

            ###########
            # bind data into one dictionary
            data[ind] = {'i_contour': i_contour,
                         'o_contour': o_contour,
                         'mask' : mask,
                         'dicom': img,
                         'frame': no,
                         'subject_no': _,
                         'ID_original': df_IDs.original_id[_],
                         'patient_id': df_IDs.patient_id[_],
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
            data_binds.append([ind, img_dicom_location, i_contour_location])
            ind += 1
        # data[_] = tmp_dict

    return data, data_binds
    # return data_binds


if __name__ == '__main__':
    # main should return 0 for success, something else (usually 1) for error.
    sys.exit(get_data())