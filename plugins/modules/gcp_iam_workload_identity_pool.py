#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Raphaël de Gail
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

################################################################################
# Documentation
################################################################################

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ["preview"], 'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gcp_iam_workload_identity_pool
description:
- Manages a workload identity pool
- A workload identity pool represents a collection of workload identities.
- You can define IAM policies to grant these identities access to Google Cloud resources.
short_description: Manages a GCP workload identity pool
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
    - The name of the pool.
    - For example, demo-pool.
    required: true
    type:  str
  display_name:
    description:
    - A display name for the pool.
    - Cannot exceed 32 characters.
    type: str
  description:
    description:
    - A description of the pool.
    - Cannot exceed 256 characters.
    default: ''
    type: str
  disabled:
    description:
    - Whether the pool is disabled.
    - You cannot use a disabled pool to exchange tokens, or use existing tokens to access resources.
    - If the pool is re-enabled, existing tokens grant access again.
    default: False
    type: bool
  project_id:
    description:
    - The resource ID of the project hosting the service account.
    - For example, tokyo-rain-123.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Creates or updates a GCP workload identity pool
  raphaeldegail.googlecloudy.gcp_iam_workload_identity_pool:
    name: demo-pool
    display_name: Demo Pool
    project_id: tokyo-rain-123
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: present
'''

RETURN = '''
name:
  description:
  - The resource name of the pool.
  returned: success
  type: str
displayName:
  description:
  - A display name for the pool.
  returned: success
  type: str
description:
  description:
  - A description of the pool.
  returned: success
  type: str
state:
  description:
  - The state of the pool.
  returned: success
  type: str
disabled:
  description:
  - Whether the pool is disabled.
  returned: success
  type: bool
expireTime:
  description:
  - Time after which the workload identity pool will be permanently purged and cannot be recovered.
  returned: success
  type: str
'''

ACTIVE = "ACTIVE"

API = 'https://iam.googleapis.com/v1'

################################################################################
# Imports
################################################################################

from ansible_collections.raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils import (
    wait_for_operation,
    list_differences,
    fetch_resource,
    remove_nones,
    GcpSession,
    GcpModule,
)

################################################################################
# Main
################################################################################


def main():
    """Main function"""

    module = GcpModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            name=dict(required=True, type='str'),
            display_name=dict(type='str'),
            description=dict(default='', type='str'),
            disabled=dict(default=False, type='bool'),
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
        if fetch.get('state') == ACTIVE:
            if state == 'present':
                difference = list_differences(resource_to_request(module), response_to_hash(fetch))
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
                module.fail_json(msg='The resource to create is in a DELETED state.')
            else:
                fetch = {}
    else:
        if state == 'present':
            create(module, collection(module))
            fetch = fetch_resource(module, self_link(module))
            changed = True
        else:
            fetch = {}

    fetch.update({'changed': changed})
    fetch.update({'diff': difference} if difference else {})

    module.exit_json(**fetch)


def create(module, link):
    auth = GcpSession(module, 'iam')
    return wait_for_operation(
        module,
        auth.post(f'{link}?workloadIdentityPoolId={module.params["name"]}', resource_to_request(module)),
        api=API
    )


def update(module, link):
    auth = GcpSession(module, 'iam')
    return wait_for_operation(
        module,
        auth.patch(f'{link}?updateMask=displayName,description,disabled', resource_to_request(module)),
        api=API
    )


def delete(module, link):
    auth = GcpSession(module, 'iam')
    return wait_for_operation(module, auth.delete(link), api=API)


def resource_to_request(module):
    request = {
        'displayName': module.params.get('display_name'),
        'description': module.params.get('description'),
        'disabled': module.params.get('disabled'),
    }
    return remove_nones(request)


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(response):
    result = {
        'displayName': response.get('displayName'),
        'description': response.get('description'),
        'disabled': response.get('disabled')
    }
    return remove_nones(result)


def self_link(module):
    return "{api}/projects/{project_id}/locations/global/workloadIdentityPools/{name}".format(api=API, **module.params)


def collection(module):
    return "{api}/projects/{project_id}/locations/global/workloadIdentityPools".format(api=API, **module.params)


if __name__ == '__main__':
    main()
