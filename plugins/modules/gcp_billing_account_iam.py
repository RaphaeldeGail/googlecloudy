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
module: gcp_billing_account_iam
description:
- Sets the access control policy for a billing account.
  Replaces any existing policy.
- The caller must have the billing.accounts.setIamPolicy permission on the account, which is often given to billing account administrators.
short_description: Sets the access control policy for a GCP billing account
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
- raphaeldegail.googlecloudy.gcp.iam
options:
  billing_account_id:
    description:
    - The resource ID of the billing account hosting the policy.
    - For example, 012345-567890-ABCDEF.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Sets the access control policy for a GCP billing account
  raphaeldegail.googlecloudy.gcp_billing_account_iam:
    bindings:
        role: roles/my.role
        members:
        - user:user1@example.com
        - group:group1@example.com
    policy_version: '1'
    billing_account_id: 012345-567890-ABCDEF
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
'''

RETURN = '''
version:
  description:
  - Specifies the format of the policy.
  returned: success
  type: int
bindings:
  description:
  - Associates a list of members, or principals, with a role.
    Optionally, may specify a condition that determines how and when the bindings are applied.
    Each of the bindings must contain at least one principal.
  returned: success
  type: list
  elements: dict
  contains:
    role:
      description:
      - Role that is assigned to the list of members, or principals.
        For example, roles/viewer, roles/editor, or roles/owner.
      returned: success
      type: str
    members:
      description:
      - Specifies the principals requesting access for a Google Cloud resource.
      returned: success
      type: list
      elements: str
    condition:
        description:
        - The condition that is associated with this binding.
        returned: success
        type: dict
        contains:
          expression:
              description:
              - Textual representation of an expression in Common Expression Language syntax.
              returned: success
              type: str
          title:
              description:
              - Title for the expression, i.e. a short string describing its purpose.
              returned: success
              type: str
          description:
              description:
              - Description of the expression.
              returned: success
              type: str
          location:
              description:
              - String indicating the location of the expression for error reporting, e.g. a file name and a position in the file.
              returned: success
              type: str
  sample:
  - role: roles/editor
    members: ['user:user1@example.com', 'group:group1@example.com']
'''

API = 'https://cloudbilling.googleapis.com/v1'

################################################################################
# Imports
################################################################################

from ansible_collections.raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils import (
    return_if_object,
    fetch_resource,
    list_differences,
    remove_nones,
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
            bindings=dict(
                required=True,
                type='list',
                elements='dict',
                options=dict(
                    role=dict(required=True, type='str'),
                    members=dict(required=True, type='list', elements='str'),
                    condition=dict(
                        type='dict',
                        options=dict(
                            expression=dict(required=True, type='str'),
                            title=dict(type='str'),
                            description=dict(type='str'),
                            location=dict(type='str')
                        )
                    )
                )
            ),
            policy_version=dict(default="1", choices=["1", "2", "3"], type='str'),
            billing_account_id=dict(required=True, type='str')
        )
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-billing']

    fetch = fetch_resource(module, f'{self_link(module)}:getIamPolicy', False)['result']
    changed = False

    difference = list_differences(resource_to_request(module).get('policy'), response_to_hash(fetch))
    if difference:
        set(module, self_link(module))
        fetch = fetch_resource(module, f'{self_link(module)}:getIamPolicy', False)['result']
        changed = True

    fetch.update({'changed': changed})
    fetch.update({'diff': difference} if difference else {})

    module.exit_json(**fetch)


def set(module, link):
    auth = GcpSession(module, 'iam')
    return return_if_object(module, auth.post(f'{link}:setIamPolicy', resource_to_request(module)))['result']


def resource_to_request(module):
    request = {
        'policy': {
            'version': int(module.params.get('policy_version')),
            'bindings': module.params.get('bindings'),
        },
        'updateMask': 'bindings,etag',
    }
    return remove_nones(request)


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(response):
    return {
        'version': int(response.get('version')),
        'bindings': response.get('bindings')
    }


def self_link(module):
    return "{api}/billingAccounts/{billing_account_id}".format(api=API, **module.params)


if __name__ == '__main__':
    main()
