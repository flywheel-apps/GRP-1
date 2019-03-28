#!/usr/bin/env python

import os
import re
import json
import pandas as pd
import numpy as np


def import_file(filepath):
    """
    This function determines the file data type and appropriately
    imports the file as a pandas object
    It also partially accounts for the bug where date
    parsing in pandas cannot be set to False for pd.read_excel()

    :param filepath: path to the excel file
    :type filepath: str
    :returns:  data_frame, a pandas dataframe without date
    """
    if filepath.endswith(('.xls', '.xlsx')):
        # read in dataframe from xls/xlsx
        dataframe = pd.read_excel(filepath)

        # if there are no datetimes series found, return  the
        if dataframe.select_dtypes('datetime64').empty:
            return dataframe
        # otherwise, convert to string and replace any NaT with NaN
        else:
            print('fixing datetime')
            # select the offending columns
            dtcolumns = dataframe.select_dtypes('datetime64').columns
            # loop over the columns
            for column in dtcolumns:
                # convert to string type
                dataframe[column] = dataframe[column].astype('str')
                # handle NaTs
                dataframe[column] = dataframe[column].replace('NaT', np.nan)
            return dataframe
    elif filepath.endswith('.csv'):
        dataframe = pd.read_csv(filepath)
        return dataframe
    else:
        print('File type is not supported')


def convert_value(value):
    """
    converts all objects to strings and handles trailing .0 on ints
    since pandas likes to spit out floats
    """
    if type(value) == str:
        return value
    else:
        # convert to string
        value = str(value)
        # clip trailing .0
        value = re.sub('\.0+$', '',value)
        return value


def export_to_dict(dataframe):
    """
    This function exports a pandas dataframe object
    to a dictionary

    :param dataframe: a pandas DataFrame object
    :type filepath: DataFrame
    :returns:  output_dic (dict) - the output object to be converted to json

    """
    # for now, assume subject is the first column
    subject_column = dataframe.columns[0]
    # get the count of the non-null subjects
    subject_count = dataframe[subject_column].count()
    # check that the above returned a value
    if type(subject_count) != np.int64:
        print("subject_count is not a valid integer. Dictionary not created.")
    # if there's only one subject, account for possibility of list columnns
    elif subject_count == 1:
        print("Processing single subject...")
        output_dict = {}
        for column in dataframe:
            if dataframe[column].count() > 1:
                output_dict[column] = dataframe[column].dropna().tolist()
            else:
                value = dataframe[column][0]
                value = convert_value(value)
                output_dict[column] = value
        # output_json = json.dumps(output_dict)
        return output_dict
    elif subject_count < 1:
        print("No subjects in DataFrame. Dictionary not created.")
    else:
        print("Processing multiple subjects...")
        output_dict = {}
        dataframe = dataframe.astype("str")
        for index, row in dataframe.iterrows():
            key = row[subject_column]
            value = row.to_dict()
            output_dict[key] = value
        # output_json = json.dumps(output_dict)
        return output_dict


# Gear basics
input_folder = '/flywheel/v0/input/file/'
output_folder = '/flywheel/v0/output/'

# Declare the output path
output_filepath = os.path.join(output_folder, '.metadata.json')

# declare config file path
config_file_path = '/flywheel/v0/config.json'

with open(config_file_path) as config_data:
    config = json.load(config_data)

meta_filepath = config['inputs']['spreadsheet-file']['location']['path']
file_name = config['inputs']['spreadsheet-file']['location']['name']

hierarchy_level = config['inputs']['spreadsheet-file']['hierarchy']['type']

# prepare object for .metadata.json file
metadata_json_out = {
    hierarchy_level: {
    }
}


meta_dataframe = import_file(meta_filepath)
meta_obj = export_to_dict(meta_dataframe)

metadata_json_out[hierarchy_level]['info'] = meta_obj

with open(output_filepath, 'w') as outfile:
    json.dump(metadata_json_out, outfile, separators=(', ', ': '), sort_keys=True, indent=4)
