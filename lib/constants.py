#!/usr/bin/env python3
import os

# Get base dirs
lib_dir = os.path.dirname(os.path.realpath(__file__))
main_dir = os.path.dirname(os.path.dirname(__file__))

# Cached data directory
CACHED_DATA_DIR = "%s/cache" % (main_dir)
USERS_FILE = f"{CACHED_DATA_DIR}/users.json"
DEVICES_FILE = f"{CACHED_DATA_DIR}/devices.json"

# Recency checks of devices and users
SECONDS_SINCE_CHECKIN_TO_BE_ACTIVE = 86400 * 14                             # 2 weeks == 1 day of seconds * 14
SECONDS_BETWEEN_DEPROVISION_AND_ACTIVE_DEVICE = 86400 * 14                   # 14 days...give time for user to return the laptop

# User types
USER_TYPES_TO_ANALYZE = [ "Full Time" ]
USER_STATUSES_TO_ANALYZE = [ "ACTIVE" ]
DEPROVISIONED_STATUSES = [ "DEPROVISIONED" ]