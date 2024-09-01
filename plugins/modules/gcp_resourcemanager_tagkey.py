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
module: gcp_resourcemanager_tagkey
description:
- Manages a tagkey.
- A TagKey, used to group a set of TagValues.
short_description: Manages a tagKey
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
  parent:
    description:
    - Immutable.
    - The resource name of the TagKey's parent.
    - A TagKey can be parented by an Organization or a Project.
    - 'For a TagKey parented by an Organization, its parent must be in the form organizations/{org_id}.'
    - 'For a TagKey parented by a Project, its parent can be in the form projects/{projectId} or projects/{projectNumber}.'
    required: true
    type: str
  short_name:
    description:
    - Immutable.
    - The user friendly name for a TagKey.
    - The short name should be unique for TagKeys within the same tag namespace.
    - The short name must be 1-63 characters, beginning and ending with an
      alphanumeric character ([a-z0-9A-Z]) with dashes (-), underscores (_), dots (.), and alphanumerics between.
    required: true
    type: str
  description:
    description:
    - User-assigned description of the TagKey.
    - Must not exceed 256 characters.
    type: str
  purpose:
    description:
    - A purpose denotes that this Tag is intended for use in policies of a
      specific policy engine, and will involve that policy engine in management operations involving this Tag.
    - A purpose does not grant a policy engine exclusive rights to the Tag, and it may be referenced by other policy engines.
    - A purpose cannot be changed once set.
    type: str
  purpose_data:
    description:
    - Purpose data corresponds to the policy system that the tag is intended for.
    - See documentation for Purpose for formatting of this field.
    - Purpose data cannot be changed once set.
    type: dict
'''

EXAMPLES = '''
- name: Creates a tagKey
  raphaeldegail.googlecloudy.gcp_resourcemanager_tagkey:
    short_name: demokey
    parent: organizations/1234
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: present

- name: Deletes a tagKey
  raphaeldegail.googlecloudy.gcp_resourcemanager_tagkey:
    short_name: demokey
    parent: organizations/1234
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: absent
'''

RETURN = '''
name:
  description:
  - Immutable.
  - The resource name for a TagKey.
  - Must be in the format tagKeys/{tag_key_id}, where tag_key_id is the generated numeric id for the TagKey.
  returned: success
  type: str
parent:
  description:
  - Immutable.
  - The resource name of the TagKey's parent.
  - A TagKey can be parented by an Organization or a Project.
  - For a TagKey parented by an Organization, its parent must be in the form organizations/{org_id}.
  - For a TagKey parented by a Project, its parent can be in the form projects/{projectId} or projects/{projectNumber}.
  returned: success
  type: str
shortName:
  description:
  - Immutable.
  - The user friendly name for a TagKey.
  - The short name should be unique for TagKeys within the same tag namespace.
  - The short name must be 1-63 characters, beginning and ending with an
    alphanumeric character ([a-z0-9A-Z]) with dashes (-), underscores (_), dots (.), and alphanumerics between.
  returned: success
  type: str
namespacedName:
  description:
  - Immutable.
  - Namespaced name of the TagKey.
  returned: success
  type: str
description:
  description:
  - User-assigned description of the TagKey.
  - Must not exceed 256 characters.
  returned: success
  type: str
createTime:
  description:
  - Creation time.
  - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
  - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
  returned: success
  type: str
updateTime:
  description:
  - Update time.
  - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
  - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
  returned: success
  type: str
etag:
  description:
  - Entity tag which users can pass to prevent race conditions.
  returned: success
  type: str
purpose:
  description:
  - A purpose denotes that this Tag is intended for use in policies of a
    specific policy engine, and will involve that policy engine in management operations involving this Tag.
  - A purpose does not grant a policy engine exclusive rights to the Tag, and it may be referenced by other policy engines.
  returned: success
  type: str
purposeData:
  description:
  - Purpose data corresponds to the policy system that the tag is intended for.
  returned: success
  type: dict
'''

ACTIVE = "ACTIVE"

API = 'https://cloudresourcemanager.googleapis.com/v3'

################################################################################
# Imports
################################################################################

from ansible_collections.raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils import (
    return_if_object,
    wait_for_operation,
    remove_nones,
    list_differences,
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
            parent=dict(required=True, type='str'),
            short_name=dict(required=True, type='str'),
            description=dict(type='str'),
            purpose=dict(type='str'),
            purpose_data=dict(type='dict')
        )
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-platform']

    state = module.params['state']

    fetch = fetch_resource(module, collection())
    changed = False
    difference = None

    if fetch:
        module.params['name'] = fetch.get('name')
        before = response_to_hash(fetch)
        after = resource_to_request(module)
        # parent is an immutable field
        del before['parent']
        del after['parent']
        difference = list_differences(after, before)
        if state == 'present':
            if difference:
                update(module, self_link(module))
                fetch = fetch_resource(module, collection())
                changed = True
        else:
            delete(module, self_link(module))
            fetch = {}
            changed = True
    else:
        if state == 'present':
            fetch = create(module, collection())
            changed = True
        else:
            fetch = {}

    fetch.update({'changed': changed})
    fetch.update({'diff': difference} if difference else {})

    module.exit_json(**fetch)


def fetch_resource(module, link):
    auth = GcpSession(module, 'resourcemanager')
    keylist = auth.list(
        link,
        return_if_object,
        params={'parent': module.params['parent']},
        array_name='tagKeys'
    )
    result = None
    for key in keylist:
        if key.get('shortName') == module.params['short_name']:
            result = key

    return result


def create(module, link):
    auth = GcpSession(module, 'resourcemanager')
    return wait_for_operation(module, auth.post(link, resource_to_request(module)), api=API)


def update(module, link):
    auth = GcpSession(module, 'resourcemanager')
    return wait_for_operation(module, auth.patch(link, resource_to_request(module)), api=API)


def delete(module, link):
    auth = GcpSession(module, 'resourcemanager')
    return wait_for_operation(module, auth.delete(link), api=API)


def resource_to_request(module):
    request = {
        'parent': module.params.get('parent'),
        'shortName': module.params.get('short_name'),
        'description': module.params.get('description'),
        'purpose': module.params.get('purpose'),
        'purposeData': module.params.get('purpos_data')
    }
    return remove_nones(request)


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(response):
    result = {
        'parent': response.get('parent'),
        'shortName': response.get('shortName'),
        'description': response.get('description'),
        'purpose': response.get('purpose'),
        'purposeData': response.get('purposeData')
    }
    return remove_nones(result)


def self_link(module):
    return "{api}/{name}".format(api=API, **module.params)


def collection():
    return "{api}/tagKeys".format(api=API)


if __name__ == '__main__':
    main()
