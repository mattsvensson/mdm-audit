#!/usr/bin/env python3
###############################################
## Purpose: Provies argument parsing capability
###############################################
import argparse

parser = argparse.ArgumentParser(description='''''')

###############################################
## Select IDP anbd MDM to import
###############################################
parser.add_argument('--idp', default='', help='IDP data to import (e.g. Okta)')
parser.add_argument('--mdm', default='', help='MDMs data to import (e.g. jamf,azure)')
parser.add_argument('--run_checks', action='store_true', help='Just run the checks')

###############################################
## Debug Options
###############################################
parser.add_argument('-v', '--print_verbose', action='store_true', help="Print verbose (warning, error, and critical)")
parser.add_argument('-vv', '--print_very_verbose', action='store_true', help="Print very verbose (everything)")



#Compile the argument paser options
args = parser.parse_args()
