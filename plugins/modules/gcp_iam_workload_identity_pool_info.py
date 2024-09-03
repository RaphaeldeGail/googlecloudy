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
module: gcp_iam_workload_identity_pool_info
description:
- Gets a workload identity pool information
- A workload identity pool represents a collection of workload identities.
- You can define IAM policies to grant these identities access to Google Cloud resources.
short_description: Gets a GCP workload identity pool information
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  name:
    description:
    - The name of the pool.
    - For example, demo-pool.
    required: true
    type:  str
  project_id:
    description:
    - The resource ID of the project hosting the service account.
    - For example, tokyo-rain-123.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Gets a GCP workload identity pool information
  raphaeldegail.googlecloudy.gcp_iam_workload_identity_pool_info:
    name: demo-pool
    project_id: tokyo-rain-123
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
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
    fetch_resource,
    GcpModule,
)

################################################################################
# Main
################################################################################


def main():
    """Main function"""

    module = GcpModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            project_id=dict(required=True, type='str')
        ),
        supports_check_mode=True
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/iam']

    result = fetch_resource(module, self_link(module), True)
    fetch = result['result']
    changed = False

    if not fetch:
        fetch = {'status_code': result['status_code'], 'url': result['url']}

    fetch.update({'changed': changed})

    module.exit_json(**fetch)


def self_link(module):
    return "{api}/projects/{project_id}/locations/global/workloadIdentityPools/{name}".format(api=API, **module.params)


if __name__ == '__main__':
    main()
