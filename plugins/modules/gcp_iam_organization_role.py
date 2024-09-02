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

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = '''
---
module: gcp_iam_organization_role
description:
- Manages a Role in an organization.
- A role in the Identity and Access Management API.
short_description: Manages a Role in a GCP organization
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
  name:
    description:
    - The name of the role.
    required: true
    type: str
  title:
    description:
    - A human-readable title for the role. Typically this is limited to 100 UTF-8
      bytes.
    required: false
    type: str
  description:
    description:
    - Human-readable description for the role.
    required: false
    type: str
  included_permissions:
    description:
    - Names of permissions this role grants when bound in an IAM policy.
    elements: str
    required: false
    type: list
  stage:
    description:
    - The current launch stage of the role.
    choices:
    - ALPHA
    - BETA
    - GA
    - DEPRECATED
    - DISABLED
    - EAP
    required: false
    type: str
  organization_id:
    description:
    - The Google Cloud Platform organization for the role.
    required: True
    type: str
'''

EXAMPLES = '''
- name: Manages a Role in a GCP organization
  raphaeldegail.googlecloudy.gcp_iam_organization_role:
    name: myCustomRole
    title: My Custom Role
    description: My custom role description
    included_permissions:
    - iam.roles.list
    - iam.roles.create
    - iam.roles.delete
    organization_id: 1234
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: present
'''

RETURN = '''
name:
  description:
  - The name of the role.
  returned: success
  type: str
title:
  description:
  - A human-readable title for the role. Typically this is limited to 100 UTF-8 bytes.
  returned: success
  type: str
description:
  description:
  - Human-readable description for the role.
  returned: success
  type: str
includedPermissions:
  description:
  - Names of permissions this role grants when bound in an IAM policy.
  returned: success
  type: list
stage:
  description:
  - The current launch stage of the role.
  - If the ALPHA launch stage has been selected for a role,
    the stage field will not be included in the returned definition for the role.
  returned: success
  type: str
deleted:
  description:
  - The current deleted state of the role.
  returned: success
  type: bool
'''

API = 'https://iam.googleapis.com/v1'

################################################################################
# Imports
################################################################################

from ansible_collections.raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils import (
    fetch_resource,
    list_differences,
    return_if_object,
    remove_nones,
    GcpSession,
    GcpModule
)

################################################################################
# Main
################################################################################


def main():
    '''Main function'''

    module = GcpModule(
        argument_spec=dict(
            state=dict(default="present", choices=["present", "absent"], type="str"),
            name=dict(required=True, type="str"),
            title=dict(type="str"),
            description=dict(type="str"),
            included_permissions=dict(type="list", elements="str"),
            stage=dict(choices=["ALPHA", "BETA", "GA", "DEPRECATED", "DISABLED", "EAP"], type="str"),
            organization_id=dict(required=True, type="str"),
        )
    )

    if not module.params["scopes"]:
        module.params["scopes"] = ["https://www.googleapis.com/auth/iam"]

    state = module.params["state"]

    fetch = fetch_resource(module, self_link(module), True)['result']
    changed = False
    difference = None

    if fetch:
        difference = list_differences(resource_to_request(module), response_to_hash(fetch))
        if state == "present":
            if fetch.get("deleted"):
                undelete(module, self_link(module), fetch["etag"])
                changed = True
            elif difference:
                update(module, self_link(module), difference)
                fetch = fetch_resource(module, self_link(module))['result']
                changed = True
        elif not fetch.get("deleted"):
            delete(module, self_link(module))
            fetch = {}
            changed = True
    else:
        if state == "present":
            fetch = create(module, collection(module))
            changed = True
        else:
            fetch = {}

    fetch.update({"changed": changed})
    fetch.update({'diff': difference} if difference else {})

    module.exit_json(**fetch)


def create(module, link):
    auth = GcpSession(module, "iam")
    return return_if_object(module, auth.post(link, resource_to_create(module)))['result']


def update(module, link, difference):
    auth = GcpSession(module, "iam")
    params = {
        "updateMask": updateMask(difference)
    }
    request = resource_to_request(module)
    del request["name"]
    return return_if_object(module, auth.patch(link, request, params=params))['result']


def delete(module, link):
    auth = GcpSession(module, "iam")
    return return_if_object(module, auth.delete(link), allow_not_found=True)['result']


def undelete(module, link, etag):
    auth = GcpSession(module, "iam")
    return return_if_object(module, auth.post(f'{link}:undelete', {
        "etag": etag
    }))['result']


def updateMask(difference):
    update_mask = []
    update_mask = list(set(difference.get('remove', {}).keys()) | set(difference.get('add', {}).keys()))
    return ",".join(update_mask)


def resource_to_request(module):
    request = {
        "name": module.params.get("name"),
        "title": module.params.get("title"),
        "description": module.params.get("description"),
        "includedPermissions": module.params.get("included_permissions"),
        "stage": module.params.get("stage"),
    }
    return remove_nones(request)


def resource_to_create(module):
    role = resource_to_request(module)
    del role["name"]
    return {"roleId": module.params["name"], "role": role}


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(response):
    return {
        "name": response.get("name", '').split("/")[-1],
        "title": response.get("title"),
        "description": response.get("description"),
        "includedPermissions": response.get("includedPermissions"),
        "stage": response.get("stage")
    }


def self_link(module):
    return "{api}/organizations/{organization_id}/roles/{name}".format(api=API, **module.params)


def collection(module):
    return "{api}/organizations/{organization_id}/roles".format(api=API, **module.params)


if __name__ == "__main__":
    main()
