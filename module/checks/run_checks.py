#!/usr/local/bin/env python3
import json
from lib.constants import USERS_FILE, DEVICES_FILE, SECONDS_SINCE_CHECKIN_TO_BE_ACTIVE, SECONDS_BETWEEN_DEPROVISION_AND_ACTIVE_DEVICE, USER_TYPES_TO_ANALYZE, USER_STATUSES_TO_ANALYZE, DEPROVISIONED_STATUSES
from lib.logger import logger
from datetime import datetime


def run_checks():
    logger.log.critical(f"Running checks")

    with open(USERS_FILE, "r") as users_file:
        users = json.loads(users_file.read())
        with open(DEVICES_FILE, "r") as devices_file:
            devices = json.loads(devices_file.read())

            ##################################################################################################################
            # Jamf Specific Checks
            ##################################################################################################################
            check_for_jamf_devices_no_users_set(devices)
            check_for_possibly_broken_jamf_agent(devices)

            ##################################################################################################################
            # Azure Specific Checks
            ##################################################################################################################
            check_for_azure_unmanaged_devices(devices)

            ##################################################################################################################
            # General Checks
            ##################################################################################################################
            check_for_users_with_no_active_device_assigned(users, devices)
            check_for_deprovisioned_user_with_active_device(users, devices)


##################################################################################################################
# Jamf Specific Checks
##################################################################################################################
def check_for_jamf_devices_no_users_set(devices):
    for device in devices:
        if device['source'] == 'jamf':
            if device['email'] == '' or device['email'] is None:
                if device['last_contact_time']:
                    seconds_since_checkin = (datetime.utcnow() - datetime.strptime(device['last_contact_time'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
                    if seconds_since_checkin < SECONDS_SINCE_CHECKIN_TO_BE_ACTIVE:
                        logger.log.critical(f"Jamf device with no email set: {device['computer_name']}")


def check_for_possibly_broken_jamf_agent(devices):
    for device in devices:
        if device['source'] =='jamf':
            if device['last_contact_time']:
                seconds_since_checkin = (datetime.utcnow() - datetime.strptime(device['last_contact_time'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
                if seconds_since_checkin < SECONDS_SINCE_CHECKIN_TO_BE_ACTIVE:
                    seconds_between_checkin_and_last_report = (datetime.strptime(device['last_contact_time'], '%Y-%m-%dT%H:%M:%SZ') - datetime.strptime(device['last_report_date'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
                    if seconds_between_checkin_and_last_report > SECONDS_SINCE_CHECKIN_TO_BE_ACTIVE:
                        logger.log.critical(f"Jamf agent may be broken: {device['computer_name']} - {device['email']}")


##################################################################################################################
# Azure Specific Checks
##################################################################################################################
def check_for_azure_unmanaged_devices(devices):
    for device in devices:
        if device['source'] =='azure':
            if device['mdm'] =='':
                seconds_since_checkin = (datetime.utcnow() - datetime.strptime(device['last_contact_time'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
                if seconds_since_checkin < SECONDS_SINCE_CHECKIN_TO_BE_ACTIVE:
                    # If it doesn't have all of these attributes, it's likely a VM
                    if device['manufacturer'] and device['model'] and device['operating_system']:
                        logger.log.critical(f"Azure device is registered but not in MDM {device['computer_name']} - {device['manufacturer']} - {device['model']} - {device['operating_system']}")


##################################################################################################################
# General Checks
##################################################################################################################
def check_for_users_with_no_active_device_assigned(users, devices):
    users_with_active_devices = []

    for user in users:
        for device in devices:
            if device['email'] == user['email'] and device['last_contact_time']:
                try:
                    seconds_since_checkin = (datetime.utcnow() - datetime.strptime(device['last_contact_time'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
                except:
                    seconds_since_checkin = (datetime.utcnow() - datetime.strptime(device['last_contact_time'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
                if seconds_since_checkin < SECONDS_SINCE_CHECKIN_TO_BE_ACTIVE:
                    users_with_active_devices.append(user['email'])

    for user in users:
        if user['status'] in USER_STATUSES_TO_ANALYZE:
            if user['user_type'] in USER_TYPES_TO_ANALYZE:
                if user['email'] not in users_with_active_devices:
                    logger.log.critical(f"No Device Assigned to {user['email']}")


def check_for_deprovisioned_user_with_active_device(users, devices):
    users_with_active_devices = {}

    for user in users:
        for device in devices:
            if device['email'] == user['email'] and device['last_contact_time']:
                seconds_since_deprovision = (datetime.utcnow() - datetime.strptime(user['status_changed'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
                # Long ago departed user
                if seconds_since_deprovision > SECONDS_BETWEEN_DEPROVISION_AND_ACTIVE_DEVICE:
                    seconds_since_checkin = (datetime.utcnow() - datetime.strptime(device['last_contact_time'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
                    # Recently active device
                    if seconds_since_checkin < SECONDS_BETWEEN_DEPROVISION_AND_ACTIVE_DEVICE:
                        users_with_active_devices[device['email']] = f'''{device['computer_name']} - User deprovisioned: {user['status_changed']} - Device last Active: {device['last_contact_time']}'''


    for user in users:
        if user['status'] in DEPROVISIONED_STATUSES:
            if user['user_type'] in USER_TYPES_TO_ANALYZE:
                if user['email'] in users_with_active_devices.keys():
                    logger.log.critical(f"Deprovisioned user with active device {users_with_active_devices[user['email']]}")