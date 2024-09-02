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
module: gcp_cloudidentity_group
description:
- Manages a group within the Cloud Identity Groups API.
- A Group is a collection of entities, where each entity is either a user, another group, or a service account..
short_description: Manages a Google group
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
  group_key:
    description:
    - The EntityKey of the Group.
    required: true
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
        - 'The namespace must correspond to an identity source created in Admin Console and must be in the form of identitysources/{identity_source}.'
        type: str
  parent:
    description:
    - Immutable.
    - The resource name of the entity under which this Group resides in the Cloud Identity resource hierarchy.
    - Must be of the form identitysources/{identity_source} for external identity-mapped groups or customers/{customerId} for Google Groups.
    - The customerId must begin with "C" (for example, 'C046psxkn').
    required: true
    type: str
  display_name:
    description:
    - The display name of the Group.
    type: str
  description:
    description:
    - An extended description to help users determine the purpose of a Group.
    - Must not be longer than 4,096 characters.
    type: str
  labels:
    description:
    - One or more label entries that apply to the Group.
    - Currently supported labels contain a key with an empty value.
    - Google Groups are the default type of group and have a label with a key of 'cloudidentity.googleapis.com/groups.discussion_forum' and an empty value.
    - Existing Google Groups can have an additional label with a key of 'cloudidentity.googleapis.com/groups.security' and an empty value added to them.
      This is an immutable change and the security label cannot be removed once added.
    - Dynamic groups have a label with a key of 'cloudidentity.googleapis.com/groups.dynamic'.
    - Identity-mapped groups for Cloud Search have a label with a key of 'system/groups/external' and an empty value.
    required: true
    type: dict
  dynamic_group_metadata_queries:
    description:
    - Dynamic group metadata queries.
    - Memberships will be the union of all queries.
    - Only one entry with USER resource is currently supported.
    - Customers can create up to 500 dynamic groups.
    type: list
    elements: dict
    suboptions:
      resource_type:
        description:
        - Resource type for the Dynamic Group Query.
        default: USER
        choices:
        - USER
        type: str
      query:
        description:
        - Query that determines the memberships of the dynamic group.
        - 'Examples:'
        - All users with at least one organizations.department of engineering.
          user.organizations.exists(org, org.department=='engineering')
        - All users with at least one location that has area of foo and building_id of bar.
          user.locations.exists(loc, loc.area=='foo' && loc.building_id=='bar')
        - All users with any variation of the name John Doe (case-insensitive queries add equalsIgnoreCase() to the value being queried).
          user.name.value.equalsIgnoreCase('jOhn DoE')
        type: str
'''

EXAMPLES = '''
- name: Manages a Google group
  raphaeldegail.googlecloudy.gcp_cloudidentity_group:
    group_key:
      id: 'demogroup@demodomain.demo'
    parent: customers/C00zzzzzz
    labels:
      cloudidentity.googleapis.com/groups.discussion_forum: ''
    auth_kind: serviceaccount
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
    wait_for_operation,
    return_if_object,
    list_differences,
    fetch_resource,
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
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            group_key=dict(required=True, no_log=False, type='dict', options=dict(
                id=dict(required=True, type='str'),
                namespace=dict(type='str')
            )),
            parent=dict(required=True, type='str'),
            display_name=dict(type='str'),
            description=dict(type='str'),
            labels=dict(required=True, type='dict'),
            dynamic_group_metadata_queries=dict(type='list', elements='dict', options=dict(
                resource_type=dict(default='USER', choices=['USER'], type='str'),
                query=dict(type='str')
            ))
        )
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-identity.groups']

    state = module.params['state']

    fetch = fetch_by_name(module, collection(module))
    changed = False
    difference = None

    if fetch:
        module.params['name'] = fetch.get('name')
        if state == 'present':
            difference = list_differences(resource_to_request(module), response_to_hash(fetch))
            if difference:
                update(module, self_link(module))
                fetch = fetch_resource(module, self_link(module), False)['result']
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
    auth = GcpSession(module, 'cloudidentity')
    params = {
        'initialGroupConfig': 'WITH_INITIAL_OWNER'
    }
    return wait_for_operation(module, auth.post(link, resource_to_request(module), params=params), api=API)


def update(module, link):
    auth = GcpSession(module, 'cloudidentity')
    return wait_for_operation(
        module,
        auth.patch(link, resource_to_request(module), params={'updateMask': 'displayName,description,labels'}),
        api=API
    )


def delete(module, link):
    auth = GcpSession(module, 'cloudidentity')
    return wait_for_operation(module, auth.delete(link), api=API)


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


def resource_to_request(module):
    request = {
        'groupKey': module.params.get('group_key'),
        'parent': module.params.get('parent'),
        'displayName': module.params.get('display_name') or module.params.get('group_key').get('id').split('@')[0],
        'description': module.params.get('description'),
        'labels': module.params.get('labels'),
        'dynamicGroupMetadata': {
            'queries': [
                {
                    'resourceType': query['resource_type'],
                    'query': query['query']
                } for query in module.params.get('dynamic_group_metadata_queries')
            ] if module.params.get('dynamic_group_metadata_queries') else []
        }
    }
    return remove_nones(request)


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(response):
    result = {
        'groupKey': response.get('groupKey'),
        'additionalGroupKeys': response.get('additionalGroupKeys'),
        'parent': response.get('parent'),
        'displayName': response.get('displayName'),
        'description': response.get('description'),
        'labels': response.get('labels'),
        'dynamicGroupMetadata': response.get('dynamicGroupMetadata')
    }
    return remove_nones(result)


def self_link(module):
    return "{api}/{name}".format(api=API, **module.params)


def collection(module):
    return "{api}/groups".format(api=API, **module.params)


if __name__ == '__main__':
    main()
