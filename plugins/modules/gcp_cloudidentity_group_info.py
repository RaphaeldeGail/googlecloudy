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
module: gcp_cloudidentity_group_info
description:
- Gets a group information within the Cloud Identity Groups API.
- A Group is a collection of entities, where each entity is either a user, another group, or a service account..
short_description: Gets a Google group information
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  name:
    description:
    - The resource name of the Group.
    - Shall be of the form groups/{group}.
    type: str
  group_key:
    description:
    - The EntityKey of the Group.
    type: dict
    suboptions:
      id:
        description:
        - The ID of the entity.
        - For Google-managed entities, the id should be the email address of an existing group or user.
        - Email addresses need to adhere to name guidelines for users and groups.
        - For external-identity-mapped entities, the id must be a string conforming to the Identity Source\'s requirements.
        - Must be unique within a namespace.
        required: true
        type: str
      namespace:
        description:
        - The namespace in which the entity exists.
        - If not specified, the EntityKey represents a Google-managed entity such as a Google user or a Google Group.
        - If specified, the EntityKey represents an external-identity-mapped group.
        - The namespace must correspond to an identity source created in Admin Console and must be in the form of identitysources/{identity_source}.
        type: str
  parent:
    description:
    - Immutable.
    - The resource name of the entity under which this Group resides in the Cloud Identity resource hierarchy.
    - Must be of the form identitysources/{identity_source} for external identity-mapped groups or customers/{customerId} for Google Groups.
    - The customerId must begin with "C" (for example, 'C046psxkn').
    type: str
notes:
  - The I(name) and I(group_key) options are
    mutually exclusive.
  - The I(name) and I(parent) options are
    mutually exclusive.
  - You need to set either one of the I(name) or I(group_key) options.
  - The I(group_key) option also requires the I(parent) option.
'''

EXAMPLES = '''
- name: Gets a Google group information from name
  raphaeldegail.googlecloudy.gcp_cloudidentity_group_info:
    name: groups/1234
    service_account_file: "/tmp/auth.pem"
    state: present

- name: Gets a Google group information from email
  raphaeldegail.googlecloudy.gcp_cloudidentity_group_info:
    group_key:
      id: 'demogroup@demodomain.demo'
    parent: customers/C00zzzzzz
    service_account_file: "/tmp/auth.pem"
    state: present
'''

RETURN = '''
name:
  description:
  - The resource name of the Group.
  - Shall be of the form groups/{group}.
  returned: success
  type: str
groupKey:
  description:
  - The EntityKey of the Group.
  returned: success
  type: dict
  contains:
    id:
      description:
      - The ID of the entity.
      returned: success
      type: str
    namespace:
      description:
      - The namespace in which the entity exists.
      returned: success
      type: str
additionalGroupKeys:
  description:
  - Additional group keys associated with the Group.
  returned: success
  type: list
  elements: dict
  contains:
    id:
      description:
      - The ID of the entity.
      returned: success
      type: str
    namespace:
      description:
      - The namespace in which the entity exists.
      returned: success
      type: str
parent:
  description:
  - The resource name of the entity under which this Group resides in the Cloud Identity resource hierarchy.
  returned: success
  type: str
displayName:
  description:
  - The display name of the Group.
  returned: success
  type: str
description:
  description:
  - An extended description to help users determine the purpose of a Group.
  returned: success
  type: str
createTime:
  description:
  - The time when the Group was created.
  - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
  - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
  returned: success
  type: str
updateTime:
  description:
  - The time when the Group was created.
  - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
  - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
  returned: success
  type: str
labels:
  description:
  - One or more label entries that apply to the Group.
  returned: success
  type: dict
dynamicGroupMetadata:
  description:
  - Dynamic group metadata like queries and status.
  returned: success
  type: dict
  contains:
    queries:
      description:
      - Memberships will be the union of all queries.
      returned: success
      type: list
      elements: dict
      contains:
        resourceType:
          description:
          - Resource type for the Dynamic Group Query.
          returned: success
          type: str
        query:
          description:
          - Query that determines the memberships of the dynamic group.
          returned: success
          type: str
    status:
      description:
      - Status of the dynamic group.
      returned: success
      type: dict
      contains:
        status:
          description:
          - Status of the dynamic group.
          returned: success
          type: str
        statusTime:
          description:
          - The latest time at which the dynamic group is guaranteed to be in the given status.
          - If status is UP_TO_DATE, the latest time at which the dynamic group was confirmed to be up-to-date.
          - If status is UPDATING_MEMBERSHIPS, the time at which dynamic group was created.
          - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
          - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
          returned: success
          type: str
'''

ACTIVE = "ACTIVE"

API = 'https://cloudidentity.googleapis.com/v1'

################################################################################
# Imports
################################################################################

from ansible_collections.raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils import (
    fetch_resource,
    return_if_object,
    GcpModule,
    GcpSession,
)

################################################################################
# Main
################################################################################


def main():
    """Main function"""

    module = GcpModule(
        argument_spec=dict(
            group_key=dict(no_log=False, type='dict', options=dict(
                id=dict(required=True, type='str'),
                namespace=dict(type='str')
            )),
            parent=dict(type='str'),
            name=dict(type='str')
        ),
        mutually_exclusive=[('name', 'group_key'), ('name', 'parent')],
        required_one_of=[('name', 'group_key')],
        required_by={
            'group_key': 'parent',
        },
        supports_check_mode=True
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-identity.groups.readonly']

    if module.params.get('name'):
        fetch = fetch_resource(module, self_link(module), True)
    else:
        fetch = fetch_by_name(module, collection(module))
    changed = False

    if not fetch:
        fetch = {}

    fetch.update({'changed': changed})

    module.exit_json(**fetch)


def fetch_by_name(module, link):
    """Fetch the existing resource by its name.

    Args:
        module: raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils.GcpModule, the ansible module.
        link: str, the URL to call for the API operation.

    Returns:
        dict, the JSON-formatted response for the API call, if it exists.
    """
    auth = GcpSession(module, 'cloudidentity')
    params = {
        'parent': module.params.get('parent'),
        'view': 'FULL'
    }
    return_list = auth.list(link, return_if_object, params=params, array_name='groups')
    for group in return_list:
        if group.get('groupKey').get('id') == module.params.get('group_key').get('id'):
            group.update({'parent': module.params.get('parent')})
            return group
    return None


def self_link(module):
    return "{api}/{name}".format(api=API, **module.params)


def collection(module):
    return "{api}/groups".format(api=API, **module.params)


if __name__ == '__main__':
    main()
