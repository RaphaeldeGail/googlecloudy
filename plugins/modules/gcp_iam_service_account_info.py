#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Google
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

################################################################################
# Documentation
################################################################################

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ["preview"], 'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gcp_iam_service_account_info
description:
- Gets a service account information.
- A service account is an account for an application or a virtual machine (VM) instance, not a person.
short_description: Gets a GCP service account information
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  name:
    description:
    - The name of the service account.
    - For example, my-service-account.
    required: false
    type: str
  project_id:
    description:
    - The resource ID of the project hosting the service account.
    - For example, tokyo-rain-123.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Gets a GCP service account information
  raphaeldegail.googlecloudy.gcp_iam_service_account_info:
    name: my-service-account
    project_id: tokyo-rain-123
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
'''

RETURN = '''
name:
  description:
  - The resource name of the service account.
  - "Use one of the following formats:"
  - "- projects/{PROJECT_ID}/serviceAccounts/{EMAIL_ADDRESS}"
  - "- projects/{PROJECT_ID}/serviceAccounts/{UNIQUE_ID}"
  returned: success
  type: str
projectId:
  description:
  - The ID of the project that owns the service account.
  returned: success
  type: str
uniqueId:
  description:
  - The unique, stable numeric ID for the service account.
  returned: success
  type: str
email:
  description:
  - The email address of the service account.
  returned: success
  type: str
displayName:
  description:
  - A user-specified, human-readable name for the service account.
  - The maximum length is 100 UTF-8 bytes.
  returned: success
  type: str
oauth2ClientId:
  description:
  - The OAuth 2.0 client ID for the service account.
  returned: success
  type: str
description:
  description:
  - A user-specified, human-readable description of the service account.
  - The maximum length is 256 UTF-8 bytes.
  returned: success
  type: str
disabled:
  description:
  - Whether the service account is disabled.
  returned: success
  type: bool
'''

API = 'https://iam.googleapis.com/v1'

################################################################################
# Imports
################################################################################

from ansible_collections.raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils import (
    fetch_resource,
    GcpModule
)

################################################################################
# Main
################################################################################


def main():
    """Main function"""

    module = GcpModule(
        argument_spec=dict(name=dict(type='str'), project_id=dict(required=True, type='str')),
        supports_check_mode=True
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/iam']

    result = fetch_resource(module, self_link(module), True)
    fetch = result['result']
    changed = False

    if not fetch:
        fetch = {'status_code': fetch['status_code'], 'url': fetch['url']}

    fetch.update({'changed': changed})

    module.exit_json(**fetch)


def self_link(module):
    return "{api}/projects/{project_id}/serviceAccounts/{name}@{project_id}.iam.gserviceaccount.com".format(api=API, **module.params)


if __name__ == '__main__':
    main()
