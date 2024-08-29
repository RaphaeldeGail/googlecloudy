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
module: gcp_iam_workload_identity_provider_info
description:
- Gets a GCP workload identity pool provider information.
- This describes the configuration for an external identity provider.
short_description: Gets a GCP workload identity pool provider information
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  name:
    description:
    - The name of the provider.
    - For example, some-provider.
    required: true
    type: str
  pool_name:
    description:
    - The resource name for the workload identity pool hosting the provider.
    - For example, projects/000/locations/global/workloadIdentityPools/some-pool.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Gets a GCP workload identity pool provider information
  raphaeldegail.googlecloudy.gcp_iam_workload_identity_provider_info:
    name: sample-provider
    pool_name: projects/000/locations/global/workloadIdentityPools/sample-pool
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
'''

RETURN = '''
name:
  description:
  - The resource name of the provider.
  returned: success
  type: str
displayName:
  description:
  - A display name for the provider.
  returned: success
  type: str
description:
  description:
  - A description for the provider.
  returned: success
  type: str
state:
  description:
  - The state of the provider.
  returned: success
  type: str
disabled:
  description:
  - Whether the provider is disabled.
  - You cannot use a disabled provider to exchange tokens.
  - However, existing tokens still grant access.
  returned: success
  type: bool
attributeMapping:
  description:
  - Maps attributes from authentication credentials issued by an external identity provider to Google Cloud attributes, such as subject and segment.
  - Each key must be a string specifying the Google Cloud IAM attribute to map to.
  returned: success
  type: dict
attributeCondition:
  description:
  - A Common Expression Language expression, in plain text, to restrict what
    otherwise valid authentication credentials issued by the provider should not be accepted.
  returned: success
  type: str
expireTime:
  description:
  - Time after which the workload identity pool provider will be permanently purged and cannot be recovered.
  returned: success
  type: str
oidc:
  description:
  - An OpenId Connect 1.0 identity provider.
  returned: success
  type: dict
  contains:
    issuerUri:
      description:
      - The OIDC issuer URL.
      returned: success
      type: str
    allowedAudiences:
      description:
      - Acceptable values for the aud field (audience) in the OIDC token.
      returned: success
      type: list
      elements: str
    jwksJson:
      description:
      - OIDC JWKs in JSON String format.
      returned: success
      type: str
'''

ACTIVE = "ACTIVE"

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
    """Main function"""

    module = GcpModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            pool_name=dict(required=True, type='str')
        ),
        supports_check_mode=True
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/iam']

    fetch = fetch_resource(module, self_link(module))
    changed = False

    fetch.update({'changed': changed})

    module.exit_json(**fetch)


def self_link(module):
    return "{api}/{pool_name}/providers/{name}".format(api=API, **module.params)


if __name__ == '__main__':
    main()
