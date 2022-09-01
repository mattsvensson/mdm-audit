#!/usr/bin/env python3
import sys
from getpass import getpass
import json
import requests
from lib.logger import logger


def get_okta_users_normalized():
    try:
        # Get Credentials
        okta_domain = input("Okta Domain (e.g. domain.okta.com): ")
        okta_api_key = getpass("Okta API Key: ")

        logger.log.warning("Getting users from Okta")

        # Make Headers
        headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json",
            "Authorization" : "SSWS {}".format(okta_api_key)
        }

        # Add active and de-provisioned users
        users = get_okta_users(okta_domain=okta_domain, headers=headers, deprovisioned=False)
        users.extend(get_okta_users(okta_domain=okta_domain, headers=headers, deprovisioned=True))

        # Return all users
        return normalize_users(users)
    except Exception as e:
        logger.log.critical(f"Error getting Okta users: {str(e)}")
        sys.exit(1)


def get_okta_users(okta_domain, headers, deprovisioned):
    users = []
    
    if deprovisioned:
        url = f"https://{okta_domain}/api/v1/users?limit=200&search=status+eq+%22DEPROVISIONED%22"
    else:
        url = f"https://{okta_domain}/api/v1/users?limit=200"

    r = requests.get(url, headers=headers)
    r_json = json.loads(r.text.strip())
    next_url = r.headers['link'].split('<')[2].split('>')[0] if 'link' in r.headers else ''

    while True:
        for user in r_json:
            users.append(user)
        logger.log.info(f"Have {len(users)} so far...checking next batch after {r_json[-1]['id']}...")
        if next_url:
            r = requests.get(next_url, headers=headers)
            r_json = json.loads(r.text.strip())
            try:
                next_url = r.headers['link'].split('<')[2].split('>')[0] if 'link' in r.headers else ''
            except:
                next_url = ''
        else:
            break

    logger.log.info(f"Returning {len(users)} users")
    return users


def normalize_users(users):
    normalized_users = []

    for user in users:
        normalized_users.append(
            {
                "email": user['profile']['email'] if 'email' in user['profile'] else '',
                "status": user['status'],
                "created": f'''{user['created'].split(".")[0]}Z''' if user['created'] else '',
                "status_changed":  f'''{user['statusChanged'].split(".")[0]}Z''' if user['statusChanged'] else '',
                "user_type": user['profile']['userType'] if 'userType' in user['profile'] else ''
            }
        )

    return normalized_users