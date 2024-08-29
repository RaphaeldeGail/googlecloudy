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
module: gcp_iam_service_account
description:
- Manages a service account.
- A service account is an account for an application or a virtual machine (VM) instance, not a person.
short_description: Manages a GCP service account
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  state:
    description:
    - Whether the given object should exist in GCP
    choices:
    - present
    - absent
    default: present
    type: str
  name:
    description:
    - The name of the service account.
    - For example, my-service-account.
    required: false
    type: str
  display_name:
    description:
    - User specified description of service account.
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
- name: Manages a GCP service account
  raphaeldegail.googlecloudy.gcp_iam_service_account_info:
    name: my-service-account
    display_name: My Service Account
    project_id: tokyo-rain-123
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: present
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
    return_if_object,
    list_differences,
    remove_nones,
    fetch_resource,
    GcpSession,
    GcpModule
)

################################################################################
# Main
################################################################################


def main():
    """Main function"""

    module = GcpModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            name=dict(type='str'),
            display_name=dict(type='str'),
            project_id=dict(required=True, type='str')
        )
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/iam']

    state = module.params['state']

    fetch = fetch_resource(module, self_link(module))
    changed = False
    difference = None

    if fetch:
        difference = list_differences(resource_to_request(module), response_to_hash(fetch))
        if state == 'present':
            if difference:
                update(module, self_link(module))
                fetch = fetch_resource(module, self_link(module), False)
                changed = True
        else:
            delete(module, self_link(module))
            fetch = {}
            changed = True
    else:
        if state == 'present':
            fetch = create(module, collection(module))
            changed = True
        else:
            fetch = {}

    fetch.update({'changed': changed})
    fetch.update({'diff': difference} if difference else {})

    module.exit_json(**fetch)


def create(module, link):
    auth = GcpSession(module, 'iam')
    return return_if_object(module, auth.post(link, encode_request(resource_to_request(module))), err_path=['error', 'errors'])


def update(module, link):
    auth = GcpSession(module, 'iam')
    return return_if_object(module, auth.put(link, resource_to_request(module)), err_path=['error', 'errors'])


def delete(module, link):
    auth = GcpSession(module, 'iam')
    return return_if_object(module, auth.delete(link), err_path=['error', 'errors'])


def resource_to_request(module):
    request = {
        'name': module.params.get('name'),
        'displayName': module.params.get('display_name')
    }
    return remove_nones(request)


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(response):
    result = {
        'name': response.get('name', '').split('/')[-1].split('@')[0],
        'displayName': response.get('displayName'),
    }
    return remove_nones(result)


def encode_request(resource_request):
    """Structures the request as accountId + rest of request"""
    account_id = resource_request['name'].split('@')[0]
    del resource_request['name']
    return {'accountId': account_id, 'serviceAccount': resource_request}


def self_link(module):
    return "{api}/projects/{project_id}/serviceAccounts/{name}@{project_id}.iam.gserviceaccount.com".format(api=API, **module.params)


def collection(module):
    return "{api}/projects/{project_id}/serviceAccounts".format(api=API, **module.params)


if __name__ == '__main__':
    main()
