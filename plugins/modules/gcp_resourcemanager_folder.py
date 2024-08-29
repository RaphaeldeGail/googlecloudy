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
module: gcp_resourcemanager_folder
description:
- Manages a folder.
- A folder in an organization's resource hierarchy, used to organize that organization's resources.
short_description: Manages a GCP folder
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
    - The folder's parent's resource name.
    required: true
    type: str
  display_name:
    description:
    - The folder's display name.
    - A folder's display name must be unique amongst its siblings.
    - For example, no two folders with the same parent can share the same display name.
    - The display name must start and end with a letter or digit, may contain
      letters, digits, spaces, hyphens and underscores and can be no longer than 30 characters.
    - 'This is captured by the regular expression: [\\p{L}\\p{N}]([\\p{L}\\p{N}_- ]{0,28}[\\p{L}\\p{N}])?.'
    required: true
    type: str
'''

EXAMPLES = '''
- name: Creates a GCP folder
  raphaeldegail.googlecloudy.gcp_resourcemanager_folder:
    parent: organizations/1234
    display_name: demofolder
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: present
'''

RETURN = '''
name:
  description:
  - The resource name of the folder.
  - "Its format is folders/{folder_id}, for example: folders/1234."
  returned: success
  type: str
parent:
  description:
  - The folder's parent's resource name.
  returned: success
  type: str
displayName:
  description:
  - The folder's display name.
  returned: success
  type: str
state:
  description:
  - The lifecycle state of the folder.
  returned: success
  type: str
createTime:
  description:
  - Timestamp when the folder was created.
  - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
  - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
  returned: success
  type: str
updateTime:
  description:
  - Timestamp when the folder was last modified.
  - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
  - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
  returned: success
  type: str
deleteTime:
  description:
  - Timestamp when the folder was requested to be deleted.
  - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
  - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
  returned: success
  type: str
etag:
  description:
  - A checksum computed by the server based on the current value of the folder resource.
  - This may be sent on update and delete requests to ensure the client has an up-to-date value before proceeding.
  returned: success
  type: str
'''

ACTIVE = "ACTIVE"

API = 'https://cloudresourcemanager.googleapis.com/v3'

################################################################################
# Imports
################################################################################

from ansible_collections.raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils import (
    wait_for_operation,
    remove_nones,
    list_differences,
    return_if_object,
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
            display_name=dict(required=True, type='str')
        )
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-platform']

    state = module.params['state']

    fetch = fetch_resource(module, collection(module))
    changed = False
    difference = None

    if fetch:
        module.params['name'] = fetch.get('name')
        difference = list_differences(resource_to_request(module), response_to_hash(fetch))
        if state == 'present':
            if difference:
                update(module, self_link(module))
                fetch = fetch_resource(module, self_link(module))
                changed = True
        elif fetch.get('state') == ACTIVE:
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


def fetch_resource(module, link):
    auth = GcpSession(module, 'resourcemanager')
    folderlist = auth.list(
        f'{link}:search',
        return_if_object,
        params={'query': f'parent={module.params["parent"]} AND displayName="{module.params["display_name"]}"'},
        array_name='folders'
    )
    result = folderlist[0] if len(folderlist) > 0 else None

    return result


def create(module, link):
    auth = GcpSession(module, 'resourcemanager')
    return wait_for_operation(module, auth.post(link, resource_to_request(module)), api=API)


def update(module, link):
    auth = GcpSession(module, 'resourcemanager')
    return wait_for_operation(module, auth.put(link, resource_to_request(module)), api=API)


def delete(module, link):
    auth = GcpSession(module, 'resourcemanager')
    return wait_for_operation(module, auth.delete(link), api=API)


def resource_to_request(module):
    request = {
        'parent': module.params.get('parent'),
        'displayName': module.params.get('display_name'),
    }
    return remove_nones(request)


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(response):
    result = {
        'parent': response.get('parent'),
        'displayName': response.get('displayName')
    }
    return remove_nones(result)


def self_link(module):
    return "{api}/{name}".format(api=API, **module.params)


def collection(module):
    return "{api}/folders".format(api=API, **module.params)


if __name__ == '__main__':
    main()
