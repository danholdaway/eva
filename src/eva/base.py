#!/usr/bin/env python

# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# imports
from abc import ABC, abstractmethod
import argparse
import importlib
import json
import os
import re
import sys
import yaml

# local imports
from eva.utilities.logger import Logger
from eva.utilities.utils import camelcase_to_underscore


# --------------------------------------------------------------------------------------------------
def envvar_constructor(loader, node):
    # method to help substitute parent directory for a yaml env var
    return os.path.expandvars(node.value)


def load_yaml_file(yaml_file):
    # this yaml load function will allow a user to specify an environment
    # variable to substitute in a yaml file if the tag '!ENVVAR' exists
    # this will help developers create absolute system paths that are related
    # to the install path of the eva package.

    loader = yaml.SafeLoader
    loader.add_implicit_resolver(
        '!ENVVAR',
        re.compile(r'.*\$\{([^}^{]+)\}.*'),
        None
    )

    loader.add_constructor('!ENVVAR', envvar_constructor)
    yaml_dict = None
    with open(yaml_file, 'r') as ymlfile:
        yaml_dict = yaml.load(ymlfile, Loader=loader)

    return yaml_dict


class Config(dict):

    def __init__(self, dict_or_yaml):
        

        print("\nInitializing eva with the following parameters:")
        print("  Diagnostic:    ", eva_class_name)
        print("  Configuration: ", config)

        # Program can recieve a dictionary or a yaml file
        if type(dict_or_yaml) is dict:
            config = dict_or_yaml
        else:
            config = load_yaml_file(dict_or_yaml)

        pretty_config = json.dumps(config, indent=4)
        
        # Initialize the parent class with the config
        super().__init__(config)



# --------------------------------------------------------------------------------------------------


class Base(ABC):

    # Base class constructor
    def __init__(self, eva_class_name, config, logger):

        # Create message logger
        # ---------------------
        if logger is None:
            self.logger = Logger(eva_class_name)
        else:
            self.logger = logger

        # Create a configuration object
        # -----------------------------
        self.config = Config(config)

    @abstractmethod
    def execute(self):
        '''
        Each class must implement this method and it is where it will do all of its work.
        '''
        pass


# --------------------------------------------------------------------------------------------------


class Factory():

    def create_object(self, eva_class_name, config, logger):

        # Convert capitilized string to one with underscores
        eva_module_name = camelcase_to_underscore(eva_class_name)

        # Import class based on user selected task
        eva_class = getattr(importlib.import_module("eva.diagnostics."+eva_module_name),
                            eva_class_name)

        # Return implementation of the class (calls base class constructor that is above)
        return eva_class(eva_class_name, config, logger)


# --------------------------------------------------------------------------------------------------


def create_and_run(eva_class_name, config, logger=None):

    '''
    Given a class name and a config this method will create an object of the class name and execute
    the diagnostic defined therein. The config will determine how the diagnostic behaves. The
    config can be passed in using a path to the Yaml file or an already parsed dictionary.

    Args:
        eva_class_name : (str) Name of the class to be instantiated
        config : (str or dictionary) configuation that will guide the diagnostic
    '''

    # Create the diagnostic object
    creator = Factory()
    eva_object = creator.create_object(eva_class_name, config, logger)

    print(f'eva_object: {eva_object}')

    # Execute the diagnostic
    eva_object.execute()


# --------------------------------------------------------------------------------------------------


def loop_and_create_and_run(config):


    # Create dictionary from the input file
    app_dict = load_yaml_file(config)

    # Get the list of applications
    try:
        apps = app_dict['applications']
    except Exception:
        print('ABORT: When running standalone the input config must contain \'applications\' as ' +
              'a list')
        sys.exit("ABORT")

    # Loop over the applications and run
    for app in apps:
        app_name = app['application name']
        create_and_run(app_name, app)


# --------------------------------------------------------------------------------------------------


def main():

    # Arguments
    # ---------
    parser = argparse.ArgumentParser()
    parser.add_argument('args', nargs='+', type=str, help='Application name [optional] followed ' +
                        'by the configuration file [madatory]. E.g. eva ObsCorrelationScatter ' +
                        'conf.yaml')

    args = parser.parse_args()
    args_list = args.args

    # Make sure only 1 or 2 arguments are present
    assert len(args_list) <= 2, "The maximum number of arguments is two."

    # Check the file exists
    # ---------------------
    if len(args_list) == 2:
        application = args_list[0]
        config_in = args_list[1]
    else:
        application = None
        config_in = args_list[0]

    assert os.path.exists(config_in), "File " + config_in + "not found"

    # Run application or determine application(s) to run from config.
    if application is not None:
        # User specifies e.g. eva ObsCorrelationScatter ObsCorrelationScatterDriver.yaml
        create_and_run(application, config_in)
    else:
        # User specifies e.g. eva ObsCorrelationScatter ObsCorrelationScatterDriver.yaml
        loop_and_create_and_run(config_in)


# --------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------------------------------
