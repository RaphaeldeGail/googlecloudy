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
module: gcp_iam_workload_identity_provider
description:
- Manages a workload identity pool provider.
- This sets the configuration for an external identity provider.
short_description: Manages a GCP workload identity pool provider
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
    - The name of the provider.
    - For example, some-provider.
    required: true
    type: str
  display_name:
    description:
    - A display name for the provider.
    - Cannot exceed 32 characters.
    type: str
  description:
    description:
    - A description for the provider.
    - Cannot exceed 256 characters.
    default: ''
    type: str
  disabled:
    description:
    - Whether the provider is disabled.
    - You cannot use a disabled provider to exchange tokens.
    - However, existing tokens still grant access.
    default: False
    type: bool
  attribute_mapping:
    description:
    - Maps attributes from authentication credentials issued by an external identity provider to Google Cloud attributes, such as subject and segment.
    - Each key must be a string specifying the Google Cloud IAM attribute to map to.
    - For OIDC providers, you must supply a custom mapping, which must include the google.subject attribute.
    - For more information,
      https://cloud.google.com/iam/docs/reference/rest/v1/projects.locations.workloadIdentityPools.providers#resource:-workloadidentitypoolprovider
    type: dict
  attribute_condition:
    description:
    - A Common Expression Language expression, in plain text, to restrict what
      otherwise valid authentication credentials issued by the provider should not be accepted.
    - For more information,
      https://cloud.google.com/iam/docs/reference/rest/v1/projects.locations.workloadIdentityPools.providers#resource:-workloadidentitypoolprovider
    type: str
  oidc:
    description:
    - An OpenId Connect 1.0 identity provider.
    type: dict
    suboptions:
      issuer_uri:
        description:
        - The OIDC issuer URL.
        - Must be an HTTPS endpoint.
        required: true
        type: str
      allowed_audiences:
        description:
        - Acceptable values for the aud field (audience) in the OIDC token.
        - Token exchange requests are rejected if the token audience does not match one of the configured values.
        - Each audience may be at most 256 characters.
        - A maximum of 10 audiences may be configured.
        type: list
        elements: str
      jwks_json:
        description:
        - OIDC JWKs in JSON String format.
        type: str
  pool_name:
    description:
    - The resource name for the workload identity pool hosting the provider.
    - For example, projects/000/locations/global/workloadIdentityPools/some-pool.
    required: true
    type: str
notes:
- If 'state' is present, an OIDC provider should be provided.
'''

EXAMPLES = '''
- name: Creates a GCP workload identity pool provider
  raphaeldegail.googlecloudy.gcp_iam_workload_identity_provider:
    name: sample-provider
    pool_name: projects/000/locations/global/workloadIdentityPools/sample-pool
    oidc:
      issuer_uri: 'https://some-url.demo'
    attribute_mapping:
      google.subject: assertion.sub
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: present

- name: Deletes a GCP workload identity pool provider
  raphaeldegail.googlecloudy.gcp_iam_workload_identity_provider:
    name: sample-provider
    pool_name: projects/000/locations/global/workloadIdentityPools/sample-pool
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
    state: absent
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
    remove_nones,
    wait_for_operation,
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
            name=dict(required=True, type='str'),
            display_name=dict(type='str'),
            description=dict(default='', type='str'),
            disabled=dict(default=False, type='bool'),
            attribute_mapping=dict(type='dict'),
            attribute_condition=dict(type='str'),
            oidc=dict(type='dict', options=dict(
                issuer_uri=dict(required=True, type='str'),
                allowed_audiences=dict(type='list', elements='str'),
                jwks_json=dict(type='str')
            )),
            pool_name=dict(required=True, type='str')
        ),
        required_if=[
            ('state', 'present', ('oidc', ), True)
        ]
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/iam']

    state = module.params['state']

    fetch = fetch_resource(module, self_link(module))
    changed = False
    difference = None

    if fetch:
        if state == 'present':
            if fetch.get('state') == 'DELETED':
                module.fail_json(msg='The resource is scheduled for deletion and will not be undeleted. %s' % fetch)
            difference = list_differences(resource_to_request(module), response_to_hash(fetch))
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
            create(module, collection(module))
            fetch = fetch_resource(module, self_link(module))
            module.fail_json(msg=fetch)
            changed = True
        else:
            fetch = {}

    fetch.update({'changed': changed})
    fetch.update({'diff': difference} if difference else {})

    module.exit_json(**fetch)


def create(module, link):
    auth = GcpSession(module, 'iam')
    return wait_for_operation(
        module,
        auth.post(f'{link}?workloadIdentityPoolProviderId={module.params["name"]}', resource_to_request(module)),
        api=API
    )


def update(module, link):
    auth = GcpSession(module, 'iam')
    return wait_for_operation(
        module,
        auth.patch(
            f'{link}?updateMask=displayName,description,disabled,attributeMapping,attributeCondition,oidc',
            resource_to_request(module)
        ),
        api=API
    )


def delete(module, link):
    auth = GcpSession(module, 'iam')
    return wait_for_operation(module, auth.delete(link), api=API)


def resource_to_request(module):
    request = {
        "displayName": module.params.get('display_name'),
        "description": module.params.get('description'),
        "disabled": module.params.get('disabled'),
        "attributeMapping": module.params.get('attribute_mapping'),
        "attributeCondition": module.params.get('attribute_condition'),
        "oidc": {
            "issuerUri": module.params.get('oidc').get('issuer_uri'),
            "allowedAudiences": module.params.get('oidc').get('allowed_audiences'),
            "jwksJson": module.params.get('oidc').get('jwks_json')
        }
    }
    return remove_nones(request)


# Remove unnecessary properties from the response.
# This is for doing comparisons with Ansible's current parameters.
def response_to_hash(response):
    result = {
        "displayName": response.get('displayName', ''),
        "description": response.get('description', ''),
        "disabled": response.get('disabled', False),
        "attributeMapping": response.get('attributeMapping'),
        "attributeCondition": response.get('attributeCondition'),
        "oidc": {
            "issuerUri": response.get('oidc', {}).get('issuerUri'),
            "allowedAudiences": response.get('oidc', {}).get('allowedAudiences'),
            "jwksJson": response.get('oidc', {}).get('jwksJson')
        }
    }
    return remove_nones(result)


def self_link(module):
    return "{api}/{pool_name}/providers/{name}".format(api=API, **module.params)


def collection(module):
    return "{api}/{pool_name}/providers".format(api=API, **module.params)


if __name__ == '__main__':
    main()
