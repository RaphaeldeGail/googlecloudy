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
module: gcp_resourcemanager_tagkey_info
description:
- Gets a tagKey information.
- A TagKey, used to group a set of TagValues.
short_description: Gets a GCP tagKey information
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
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
'''

EXAMPLES = '''
- name: Gets a GCP tagKey information
  raphaeldegail.googlecloudy.gcp_resourcemanager_tagkey_info:
    short_name: demokey
    parent: organizations/1234
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
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
            parent=dict(required=True, type='str'),
            short_name=dict(required=True, type='str')
        ),
        supports_check_mode=True
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-platform']

    fetch = fetch_resource(module, collection())
    changed = False

    if not fetch:
        fetch = {}

    fetch.update({'changed': changed})

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


def collection():
    return "{api}/tagKeys"


if __name__ == '__main__':
    main()
