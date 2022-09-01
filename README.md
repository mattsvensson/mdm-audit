# MDM Audit

## Purpose
Audit cloud MDM Device Assignments and Agent Status

## Answers it will provide
- Do all active users have an active device?
- Are all active devices assigned to a user?
- Are any deprovisioned users assigned an active device?
- Are there potential MDM agent issues? (e.g. agent has stopped checking in)
- Are any devices active in Azure AD but not in MDM?

## SaaS Option
If you would like to have this as a SaaS product vs a set of scripts, create an issue so the need can be scoped.

## Current Integrations (create issue to request new integrations)
IDP
- Okta

MDM
- Jamf
- Azure (Intune)

## Requirements
- Python3
- Python3 pip

## Execution

### Install requirements
    pip3 install -r requirements.txt

The below can all be used at the same time, if desired.

### Caching IDP data
    python3 main.py --idp=okta

### Caching MDM data example
All MDMs must be cached at the same time

    ```
    python3 main.py --mdm=jamf,azure
    ```

### Running checks
    python3 main.py --run_checks

## Example Output

    [*] No Device Assigned to {EMAIL}
    [*] Jamf device with no email set: {DEVICE_NAME}
    [*] Jamf agent may be broken: {DEVICE_NAME}
    [*] Azure device is registered but not in MDM {DEVICE_NAME} - {MANUFACTURER} - {MODEL} - {OPERATING_SYSTEM}
    [*] Deprovisioned user with active device {DEVICE_NAME} - User deprovisioned: {USER_STATUS_CHANGE_DATE} - Device last Active: {LAST_CONTACT_TIME}

## Customization

The lib/constants.py file has a couple of things that you can customize.  The current settings are a resonable balance.

1. USER_TYPES_TO_ANALYZE: IDP user types to analyze, e.g. "Full Time"

2. SECONDS_SINCE_CHECKIN_TO_BE_ACTIVE: How recently a device has to have checked in to be seen as "active"

3. SECONDS_BETWEEN_DEPROVISION_AND_ACTIVE_DEVICE: How long between a user being deprovisioned and their device still being active to be suspicious.  e.g. The employee has been gone for over 2 weeks but their device has been active within the last 2 weeks.


## mdm-audit commandments for new integrations

1. Thou shalt only have 1 IDP as your user source of truth.

2. Thou shalt use the below IDP normalization format.

    ```
    {
        "email": {STRING},
        "status": {STRING},
        "created": {STRING},
        "status_changed": {STRING},
        "user_type": {STRING}
    }
    ```

3. Thou shalt use the below MDM normalization format

    ```
    {
        "source": {STRING},
        "mdm": {STRING},
        "manufacturer": {STRING},
        "model": {STRING},
        "operating_system": {STRING},
        "computer_name": {STRING},
        "last_contact_time": {STRING},
        "last_report_date": {STRING},
        "email": {STRING},
    }
    ```

4. Thou shalt use the following time format:  

    ```2022-09-01T15:04:12Z```