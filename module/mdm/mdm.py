#!/usr/bin/env python3
import sys
import json
from lib.arg_parser import args
from lib.logger import logger


def get_devices_from_mdm_normalized():
    # Base devices array
    devices_normalized = []

    for mdm in args.mdm.split(","):
        if mdm not in ('azure','jamf'):
            logger.log.warning(f"{mdm} is not a supported MDM at this time.")
            sys.exit(1)
        else:
            if mdm == "jamf":
                from module.mdm.jamf import get_jamf_devices_normalized
                devices_normalized.extend(get_jamf_devices_normalized())
            elif mdm == "azure":
                from module.mdm.azure import get_azure_devices_normalized
                devices_normalized.extend(get_azure_devices_normalized())


    return devices_normalized