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

DOCUMENTATION = '''
---
module: gcp_billing_account_iam_info
description:
- Gets the access control policy for a billing account.
- The caller must have the billing.accounts.getIamPolicy permission on the account, which is often given to billing account viewers.
short_description: Gets the access control policy for a GCP billing account
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  billing_account_id:
    description:
    - The resource ID of the billing account hosting the policy.
    - For example, 012345-567890-ABCDEF.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Gets the access control policy for a GCP billing account
  raphaeldegail.googlecloudy.gcp_billing_account_iam_info:
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
    fetch_resource,
    GcpModule
)

################################################################################
# Main
################################################################################


def main():
    """Main function"""

    module = GcpModule(
        argument_spec=dict(
            billing_account_id=dict(required=True, type='str')
        ),
        supports_check_mode=True
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-billing.readonly']

    fetch = fetch_resource(module, f'{self_link(module)}:getIamPolicy', False)['result']
    changed = False

    fetch.update({'changed': changed})

    module.exit_json(**fetch)


def self_link(module):
    return "{api}/billingAccounts/{billing_account_id}".format(api=API, **module.params)


if __name__ == '__main__':
    main()
