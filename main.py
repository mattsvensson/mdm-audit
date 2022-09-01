#!/usr/bin/env python3
import sys
import json
from lib.arg_parser import args
from lib.logger import logger
from lib.constants import CACHED_DATA_DIR, USERS_FILE, DEVICES_FILE
from module.mdm.mdm import get_devices_from_mdm_normalized
from module.checks.run_checks import run_checks

def run_audit():
    # Import/re-import IDP and MDM data if desired
    if args.idp:
        cache_users_from_idp()
    if args.mdm:
        cache_devices_from_mdm()

    # Run checks
    logger.log.critical(f"Running checks")
    run_checks()


def cache_users_from_idp():
    from module.idp.okta import get_okta_users_normalized
    if args.idp == "okta":
        users = get_okta_users_normalized()
    else:
        logger.log.critical("Okta is the only currently supported IDP")
        sys.exit(1)

    # Cache the users
    with open(USERS_FILE, "w+") as f:
        f.write(json.dumps(users))


def cache_devices_from_mdm():
    # Get devices from all of the MDMs
    devices_normalized = get_devices_from_mdm_normalized()

    # Cache the devices
    logger.log.critical(f"Writing {len(devices_normalized)} devices to the cache")
    with open(DEVICES_FILE, "w+") as f:
        f.write(json.dumps(devices_normalized))


if __name__ == "__main__":
    run_audit()