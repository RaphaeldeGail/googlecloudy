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
module: gcp_billing_association_info
description:
- Gets the billing information for a project.
- The current authenticated user must have the resourcemanager.projects.get permission for the project,
  which can be granted by assigning the Project Viewer role.
short_description: Gets the billing information for a GCP project
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  project_id:
    description:
    - The resource ID of the project for which billing information is retrieved.
    - For example, tokyo-rain-123.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Gets the billing information for a GCP project
  raphaeldegail.googlecloudy.gcp_billing_association_info:
    project_id: tokyo-rain-123
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
'''

RETURN = '''
name:
  description:
  - The resource name for the ProjectBillingInfo;
    has the form projects/{projectId}/billingInfo.
  - For example, the resource name for the billing information for project tokyo-rain-123 would be
    projects/tokyo-rain-123/billingInfo.
  returned: success
  type: str
projectId:
  description:
  - The ID of the project that this ProjectBillingInfo represents, such as tokyo-rain-123.
  - This is a convenience field so that you don't need to parse the name field to obtain a project ID.
  returned: success
  type: str
billingAccountName:
  description:
  - The resource name of the billing account associated with the project, if any.
  - For example, billingAccounts/012345-567890-ABCDEF.
  returned: success
  type: str
billingEnabled:
  description:
  - True if the project is associated with an open billing account, to which usage on the project is charged.
  - False if the project is associated with a closed billing account, or no billing account at all,
    and therefore cannot use paid services.
  returned: success
  type: bool
'''

API = 'https://cloudbilling.googleapis.com/v1'

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
            project_id=dict(required=True, type='str'),
        ),
        supports_check_mode=True
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-billing.readonly']

    fetch = fetch_resource(module, self_link(module), False)
    changed = False

    fetch.update({'changed': changed})

    module.exit_json(**fetch)


def self_link(module):
    return "{api}/projects/{project_id}/billingInfo".format(api=API, **module.params)


if __name__ == '__main__':
    main()
