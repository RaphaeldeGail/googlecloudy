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
module: gcp_resourcemanager_organization_info
description:
- Gets an organization information.
- The root node in the resource hierarchy to which a particular entity's (a company, for example) resources belong.
short_description: Gets a GCP organization information
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  domain:
    description:
    - The primary domain name of the organization.
    - For example, demodomain.demo
    required: true
    type: str
'''

EXAMPLES = '''
- name: Gets a GCP organization information
  gcp_resourcemanager_organization_info:
    domain: demodomain.demo
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
'''

RETURN = '''
resources:
  description: List of resources
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description:
      - The resource name of the organization.
      - This is the organization's relative path in the API.
      - Its format is "organizations/[organizationId]". For example, "organizations/1234".
      returned: success
      type: str
    displayName:
      description:
      - A human-readable string that refers to the Organization in the Google Cloud console.
      - This string is set by the server and cannot be changed.
      - The string will be set to the primary domain (for example, "google.com") of the G Suite customer that owns the organization.
      returned: success
      type: str
    owner:
      description:
      - The owner of this Organization.
      - The owner should be specified on creation.
      - Once set, it cannot be changed. This field is required.
      returned: success
      type: dict
      contains:
        directoryCustomerId:
          description:
          - The G Suite customer id used in the Directory API.
          returned: success
          type: str
'''

API = 'https://cloudresourcemanager.googleapis.com/v1'

################################################################################
# Imports
################################################################################
from ansible_collections.raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils import (
    navigate_hash,
    GcpSession,
    GcpModule
)
import json

################################################################################
# Main
################################################################################


def main():
    module = GcpModule(argument_spec=dict(
        domain=dict(type='str', required=True)
    ), supports_check_mode=True)

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloudplatformorganizations.readonly']

    if module.check_mode:
        result = module.params
        result['changed'] = False
        module.exit_json(**result)

    return_value = {'resources': search_list(module, f'{collection(module)}:search')}
    module.exit_json(**return_value)


def search_list(module, link):
    auth = GcpSession(module, 'resourcemanager')
    params = {
        'filter': f'domain:{module.params.get("domain")}'
    }
    return auth.search(link, return_if_object, array_name='organizations', data=params)


def return_if_object(module, response):
    # If not found, return nothing.
    if response.status_code == 404:
        return {
            'result': None,
            'status_code': response.status_code,
            'url': response.url
        }

    # If no content, return nothing.
    if response.status_code == 204:
        return {
            'result': None,
            'status_code': response.status_code,
            'url': response.url
        }

    try:
        module.raise_for_status(response)
        result = response.json()
    except getattr(json.decoder, 'JSONDecodeError', ValueError) as inst:
        module.fail_json(msg="Invalid JSON response with error: %s" % inst)

    if navigate_hash(result, ['error', 'errors']):
        module.fail_json(msg=navigate_hash(result, ['error', 'errors']))

    full_result = {
        'result': result,
        'status_code': response.status_code,
        'url': response.url
    }

    return full_result


def collection(module):
    return "{api}/organizations".format(api=API, **module.params)


if __name__ == "__main__":
    main()
