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
module: gcp_billing_association
description:
- Sets or updates the billing account associated with a project.
- Associating a project with an open billing account enables billing on the project and allows charges for resource usage.
- If the project already had a billing account, this method changes the billing account used for resource usage charges.
- The current authenticated user must have ownership privileges for both the project and the billing account.
- You can disable billing on the project by setting the billing_account_id field to empty.
short_description: Sets or updates the billing account associated with a GCP project
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  billing_account_id:
    description:
    - The resource ID of the billing account associated with the project, if any.
    - For example, 012345-567890-ABCDEF.
    required: true
    type: str
  project_id:
    description:
    - The resource ID of the project for which billing information is retrieved.
    - For example, tokyo-rain-123.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Sets or updates the billing account associated with a GCP project
  raphaeldegail.googlecloudy.gcp_billing_association:
    billing_account_id: 012345-567890-ABCDEF
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
    return_if_object,
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
            billing_account_id=dict(required=True, type='str'),
            project_id=dict(required=True, type='str'),
        )
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-billing']

    fetch = fetch_resource(module, self_link(module), False)['result']
    changed = False

    difference = list_differences(resource_to_request(module), response_to_hash(fetch))
    if difference:
        create(module, self_link(module))
        fetch = fetch_resource(module, self_link(module), False)['result']
        changed = True

    fetch.update({'changed': changed})
    fetch.update({'diff': difference} if difference else {})

    module.exit_json(**fetch)


def create(module, link):
    auth = GcpSession(module, 'billing')
    return return_if_object(module, auth.put(link, resource_to_request(module)))['result']


def resource_to_request(module):
    request = {
        'billingAccountName': f'billingAccounts/{module.params.get("billing_account_id")}' if module.params.get('billing_account_id') else None
    }
    return remove_nones(request)


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(response):
    result = {
        'billingAccountName': response.get('billingAccountName')
    }
    return remove_nones(result)


def self_link(module):
    return "{api}/projects/{project_id}/billingInfo".format(api=API, **module.params)


if __name__ == '__main__':
    main()
