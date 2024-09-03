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
module: gcp_iam_organization_role_info
description:
- Gets the definition of a Role in an organization.
- A role in the Identity and Access Management API.
short_description: Gets the definition of a Role in a GCP organization
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  name:
    description:
    - The name of the role.
    required: true
    type: str
  organization_id:
    description:
    - The resource ID of the organization hosting the role.
    - For example, 1234.
    required: True
    type: str
'''

EXAMPLES = '''
- name: Gets the definition of a Role in a GCP organization
  raphaeldegail.googlecloudy.gcp_iam_organization_role_info:
    name: myCustomRole
    organization_id: 1234
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
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
    GcpModule
)

################################################################################
# Main
################################################################################


def main():
    '''Main function'''

    module = GcpModule(
        argument_spec=dict(
            name=dict(required=True, type="str"),
            organization_id=dict(required=True, type="str"),
        ),
        supports_check_mode=True
    )

    if not module.params["scopes"]:
        module.params["scopes"] = ["https://www.googleapis.com/auth/iam"]

    fetch = fetch_resource(module, self_link(module), True)['result']
    changed = False

    fetch.update({"changed": changed})

    module.exit_json(**fetch)


def self_link(module):
    return "{api}/organizations/{organization_id}/roles/{name}".format(api=API, **module.params)


if __name__ == "__main__":
    main()
