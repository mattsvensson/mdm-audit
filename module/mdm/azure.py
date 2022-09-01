#!/usr/bin/env python3
'''
'''
import requests
import json
from getpass import getpass
from lib.logger import logger
BASE_URL="https://graph.microsoft.com/v1.0"


def get_azure_devices_normalized():
    # Get Credentials
    azure_tenant = input("Azure Tenant ID: ")
    azure_app_id = input("Azure App ID: ")
    azure_client_secret = getpass("Azure client secret: ")

    # Make the headers for follow-on requests
    headers = make_headers(azure_tenant=azure_tenant, azure_app_id=azure_app_id, azure_client_secret=azure_client_secret)

    # Getting Azure managed devices...because some devices are in the system but not managed.
    logger.log.warning("Getting managed devices")
    managed_devices = get_azure_managed_devices(headers=headers)

    # Get the Azure devices
    logger.log.warning("Getting devices from Azure")
    devices = get_azure_devices(headers=headers)

    # Get the Azure device registration info (emails...becaues they aren't in the devices :/ )
    logger.log.warning("Getting device registration information from Azure.  This will take a minute...")
    registered_devices = get_azure_device_registration_info(devices=devices, headers=headers)

    # Normalize the devices
    logger.log.warning("Normalizing Azure devices")
    normalized_devices = normalize_azure_devices(devices=devices, registered_devices=registered_devices, managed_devices=managed_devices)

    # Return the normalized devices
    return normalized_devices


def make_headers(azure_tenant, azure_app_id, azure_client_secret):
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': azure_app_id,
        'client_secret': azure_client_secret,
        'scope':'https://graph.microsoft.com/.default',
    }
    token_r = requests.post(f'https://login.microsoftonline.com/{azure_tenant}/oauth2/v2.0/token', data=token_data)
    token = token_r.json().get('access_token')
    headers={"Accept":"application/json", "Authorization":f"Bearer {token}"}
    return headers


def get_azure_devices(headers):
    r_devices = requests.get(f"{BASE_URL}/devices", headers=headers)
    r_devices_json = json.loads(r_devices.text)

    devices = []
    while True:
        # Add the next set of data if there are any
        if 'value' in r_devices_json:
            for device in r_devices_json['value']:
                devices.append(device)
        else:
            break

        # Go to the next set of data
        if '@odata.nextLink' in r_devices_json:
            r_devices = requests.get(r_devices_json['@odata.nextLink'], headers=headers)
            r_devices_json = json.loads(r_devices.text)
        else:
            break

    return devices


def get_azure_device_registration_info(devices, headers):
    device_registration_info = []
    for device in devices:
        r_device_user = requests.get(f"{BASE_URL}/devices/{device['id']}/registeredUsers", headers=headers)
        r_device_user_json = json.loads(r_device_user.text)

        # Not try to find a matching employee
        if 'value' in r_device_user_json and r_device_user_json['value']:
            if r_device_user_json['value'][0]:
                device_info = r_device_user_json['value'][0]
                device_info['deviceId'] = device['id']              # Have to add in the ID to be able to then reference back to it later
                device_info.pop('@odata.type')
                device_registration_info.append(device_info)

    return device_registration_info


def get_azure_managed_devices(headers):
    r_devices = requests.get(f"{BASE_URL}/deviceManagement/managedDevices", headers=headers)
    r_devices_json = json.loads(r_devices.text)

    devices = []
    while True:
        # Add the next set of data if there are any
        if 'value' in r_devices_json:
            for device in r_devices_json['value']:
                devices.append(device)
        else:
            break

        # Go to the next set of data
        if '@odata.nextLink' in r_devices_json:
            r_devices = requests.get(r_devices_json['@odata.nextLink'], headers=headers)
            r_devices_json = json.loads(r_devices.text)
        else:
            break

    return devices


def normalize_azure_devices(devices, registered_devices, managed_devices):
    normalized_devices = []

    for device in devices:
        # Make a new base device
        new_device = {
            "source": 'azure',
            "mdm": '',
            "manufacturer":  device['manufacturer'] if device['manufacturer'] else '',
            "model":  device['model'] if device['model'] else '',
            "operating_system":  device['operatingSystem'] if device['operatingSystem'] else '',
            "computer_name": device['displayName'],
            "last_contact_time": device['approximateLastSignInDateTime'] if device['approximateLastSignInDateTime'] else '', 
            "last_report_date": device['approximateLastSignInDateTime'] if device['approximateLastSignInDateTime'] else '', 
            "email": ''
        }

        # Get the registration information (email)
        for registered_device in registered_devices:
            if device['id'] == registered_device['deviceId']:
                # Set the email for the device
                new_device['email'] = registered_device['userPrincipalName']

        # Get if it's in MDM and the last sync date/time
        for managed_device in managed_devices:
            if device['deviceId'] == managed_device['azureADDeviceId']:
                new_device['mdm'] = 'Intune'
                new_device['last_contact_time'] = managed_device['lastSyncDateTime'] if managed_device['lastSyncDateTime'] else ''
                new_device['last_report_date'] = managed_device['lastSyncDateTime'] if managed_device['lastSyncDateTime'] else ''

        # Add the device
        normalized_devices.append(new_device)

    return normalized_devices