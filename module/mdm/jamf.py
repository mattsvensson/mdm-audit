#!/usr/bin/env python3
'''
'''
import requests
from requests.auth import HTTPBasicAuth
import json
from getpass import getpass
from lib.logger import logger
HEADERS_JAMF = {
    "Accept": "application/json"
}
DEVICES_PER_PAGE = 1000


def get_jamf_devices_normalized():
    # Get Credentials
    jamf_domain = input("Jamf Domain (e.g. domain.jamfcloud.com): ")
    jamf_username = input("Jamf username: ")
    jamf_password = getpass("Jamf password: ")


    # Get jamf devices
    logger.log.warning("Getting devices from Jamf")
    devices =  get_jamf_devices(jamf_domain=jamf_domain, jamf_username=jamf_username, jamf_password=jamf_password)

    # Normalize the devices then return them
    devices_normalized = normalize_jamf_devices(devices=devices)    
    logger.log.warning(f"Got {len(devices_normalized)} devices from Jamf")
    return devices_normalized


def get_jamf_devices(jamf_domain, jamf_username, jamf_password):
    # Get all computers
    response = requests.post(f"https://{jamf_domain}/api/v1/auth/token", auth=HTTPBasicAuth(jamf_username, jamf_password), headers=HEADERS_JAMF)
    response_json = json.loads(response.text)

    auth_headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {response_json['token']}"

    }

    devices = []
    total_count = 0
    page = 0
    while True:
        # Get the current page and parse the results as json
        inventory_response = requests.get(f"https://{jamf_domain}/api/v1/computers-inventory?section=GENERAL&section=USER_AND_LOCATION&section=HARDWARE&page-size={DEVICES_PER_PAGE}&page={page}", headers=auth_headers)
        inventory_response_json = json.loads(inventory_response.text)

        # Be sure total count of devices is set
        total_count = inventory_response_json['totalCount']

        # Add current set of results
        devices.extend(inventory_response_json['results'])
        
        # See if at the end....
        if len(devices) == total_count:
            break
        else:
            page += 1

    return devices


def normalize_jamf_devices(devices):
    devices_normalized = []

    for device in devices:
        devices_normalized.append(
            {
                "source": 'jamf',
                "mdm": 'jamf',
                "manufacturer":  device['hardware']['make'] if device['hardware'] else '',
                "model":  device['hardware']['model'] if device['hardware'] else '',
                "operating_system":  device['operatingSystem'] if device['operatingSystem'] else '',
                "computer_name": device['general']['name'],
                "last_contact_time": f'''{device['general']['lastContactTime'].split(".")[0]}Z''' if device['general']['lastContactTime'] else '',
                "last_report_date": f'''{device['general']['reportDate'].split(".")[0]}Z''' if device['general']['reportDate'] else '',
                "email": device['userAndLocation']['email'] 
            }
        )

    return devices_normalized