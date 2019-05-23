#!/usr/bin/env python

import os
import re
import json
import pandas as pd
import numpy as np
import jsonschema
import logging


# Initialize logging
logging.basicConfig()
log = logging.getLogger('grp-1')

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
        value = re.sub('\\.0+$', '',value)
        return value


def export_to_dict(dataframe):
    """
    This function exports a pandas dataframe object
    to a dictionary

    :param dataframe: a pandas DataFrame object
    :type filepath: DataFrame
    :returns:  output_dic (dict) - the output object to be converted to json

    """

    output_dict = {}
    dataframe = dataframe.astype("str")
    for index, row in dataframe.iterrows():
        key = index
        value = row.to_dict()
        output_dict[key] = value
    # output_json = json.dumps(output_dict)
    return output_dict


def validate_against_template(input_dict, template):
    """
    This is a function for validating a dictionary against a template. Given
    an input_dict and a template object, it will create a JSON schema validator
    and construct an object that is a list of error dictionaries. It will write a
    JSON file to the specified error_log_path and return the validation_errors object as
    well as log each error.message to log.errors

    :param input_dict: a dictionary of representing a row of a spreadsheet to be validated
    :param template: a template dictionary to validate against
    :return: validation_errors, an object containing information on validation errors
    """
    # Initialize json schema validator
    validator = jsonschema.Draft7Validator(template)
    # Initialize list object for storing validation errors
    validation_errors = []
    for error in sorted(validator.iter_errors(input_dict), key=str):
        # Create a temporary dictionary for the individual error
        tmp_dict = {}
        # Get error type
        tmp_dict['error_type'] = error.validator
        # Get error message and log it
        tmp_dict['error_message'] = error.message
        log.error(error.message)
        # Required field errors are a little special and need to be handled
        # separately to get the field. We don't get the schema because it
        # will print the entire template schema
        if error.validator == "required":
            # Get the item failing validation from the error message
            tmp_dict['item'] = 'info.' + error.message.split("'")[1]
        # Get additional information for pattern and type errors
        elif error.validator in ("pattern", "type"):
            # Get the value of the field that failed validation
            tmp_dict['error_value'] = error.instance
            # Get the field that failed validation
            tmp_dict['item'] = 'Column: {}'.format(str(error.path.pop()))
            # Get the schema object used to validate in failed validation
            tmp_dict['schema'] = error.schema
        elif error.validator == "anyOf":
            tmp_dict['schema'] = {"anyOf": error.schema['anyOf']}
        else:
            pass
        # revalidate key so that validation errors can be revalidated in the future
        tmp_dict['revalidate'] = False
        # Append individual error object to the return validation_errors object
        validation_errors.append(tmp_dict)

    return validation_errors


if __name__ == '__main__':

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

    df = import_file(meta_filepath)
    input_dict = export_to_dict(df)

    # Set template json filepath (if provided)
    if config['inputs'].get('json-template'):
        template_filepath = config['inputs']['json-template']['location']['path']
    else:
        template_filepath = None
    # Set default validation template
    template = {}

    # Import JSON template (if provided)
    if template_filepath:
        with open(template_filepath) as template_data:
            import_template = json.load(template_data)
        template.update(import_template)
    json_template = template.copy()
    print(json_template)
    # Validate header data against json schema template
    error_file_name = file_name + '.error.log.json'
    error_filepath = os.path.join(output_folder, error_file_name)
    validation_errors = {}
    for index in input_dict:
        errors = validate_against_template(input_dict[index], json_template)
        if errors:
            key = "Row {}".format(index + 1)
            validation_errors[key] = errors
    print(validation_errors)
    if validation_errors:
        with open(error_filepath, 'w') as outfile:
            json.dump(validation_errors, outfile, separators=(', ', ': '), sort_keys=True, indent=4)
