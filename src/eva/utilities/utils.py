# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import yaml

from eva.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


def camelcase_to_underscore(CamelCaseString):

    # Convert a string that looks like e.g. ThisIsAString to this_is_a_string
    # -----------------------------------------------------------------------

    # Create empty output string
    underscore_string = ''

    if not isinstance(CamelCaseString, str):
        msg = f'\'diagnostic name\': {CamelCaseString} - should be a str type. ' \
              f'Was actually a type: {type(CamelCaseString)}'
        raise TypeError(msg)

    # limit string to lower case or uppercase letters
    if not CamelCaseString.isalpha():
        msg = 'Only a-z A-Z characters allowed in module name. ' \
              f'Module name was: {CamelCaseString}, should be \'CamelCaseString\'.'
        raise ValueError(msg)

    # Loop over the elements in the string
    for element in CamelCaseString:

        # Check if element is upper case and if so prepend with underscore
        if element.isupper():
            new_element = '_'+element.lower()
        else:
            new_element = element

        # Add new element to the output string
        underscore_string = underscore_string+new_element

    # If this results in leading underscore then remove it
    if underscore_string[0] == "_":
        underscore_string = underscore_string[1:]

    return underscore_string


# --------------------------------------------------------------------------------------------------


def load_yaml_file(eva_config, logger):
    # utility function to help load a yaml file into a dict.

    if logger is None:
        logger = Logger('LoadYamlFile')

    try:
        with open(eva_config, 'r') as eva_config_opened:
            eva_dict = yaml.safe_load(eva_config_opened)
    except Exception as e:
        logger.abort('Eva diagnostics is expecting a valid yaml file, but it encountered ' +
                     f'errors when attempting to load: {eva_config}, error: {e}')

    return eva_dict


# --------------------------------------------------------------------------------------------------

def get_schema(YamlFile, configDict={}, logger=None):
    # read YamlFile into a dictionary containing a configuration,
    # and overwrite the default configuration with the input configDict

    if logger is None:
        logger = Logger('EvaSchema')

    # ignore some fields
    skipvars = ['type', 'comparison']

    # read schema from YAML file
    fullConfig = load_yaml_file(YamlFile, logger)

    # update full config dict based on input configDict
    for key, value in configDict.items():
        if key in fullConfig or skipvars:
            logger.trace(f'{key}:{value}')
            fullConfig[key] = value
        else:
            msg = f"'{key}' not in default schema. Not a valid entry."
            raise ValueError(msg)

    return fullConfig

# --------------------------------------------------------------------------------------------------


def update_object(myObj, configDict, logger=None):
    # update input object myObj attributes based on a dictionary
    # and return a new, updated myObj

    if logger is None:
        logger = Logger('EvaUpdateObject')

    # loop through input dictionary, update input object key values
    for key, value in configDict.items():
        if key in dir(myObj):
            logger.trace(f"Updating '{key}'")
        else:
            logger.trace(f"Adding '{key}'")
        setattr(myObj, key, value)

    return myObj


# --------------------------------------------------------------------------------------------------
