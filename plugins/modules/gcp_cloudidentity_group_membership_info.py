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
module: gcp_cloudidentity_group_membership_info
description:
- Gets a membership information within the Cloud Identity Groups API.
- A Membership defines a relationship between a Group and an entity belonging to that Group, referred to as a "member".
short_description: Gets a membership information in a Google group
extends_documentation_fragment:
- raphaeldegail.googlecloudy.gcp
options:
  name:
    description:
    - The resource name of the Membership.
    - 'Shall be of the form groups/{group}/memberships/{membership}.'
    type: str
  preferred_member_key:
    description:
    - Immutable.
    - The EntityKey of the member.
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
  group_id:
    description:
    - the resource ID of the group hosting the member.
    - For example, 1234.
    required: true
    type: str
'''

EXAMPLES = '''
- name: Gets a membership information in a Google group
  raphaeldegail.googlecloudy.gcp_cloudidentity_group_membership_info:
    preferred_member_key:
      id: 'demouser@demodomain.demo'
    group_id: 1234
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
'''

RETURN = '''
name:
  description:
  - The resource name of the Membership.
  - Shall be of the form groups/{group}/memberships/{membership}.
  returned: success
  type: str
preferredMemberKey:
  description:
  - The EntityKey of the member.
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
createTime:
  description:
  - The time when the Membership was created.
  - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
  - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
  returned: success
  type: str
updateTime:
  description:
  - The time when the Membership was last updated.
  - A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
  - 'Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".'
  returned: success
  type: str
roles:
  description:
  - The MembershipRoles that apply to the Membership.
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description:
      - The name of the MembershipRole.
      returned: success
      type: str
    expiryDetail:
      description:
      - The expiry details of the MembershipRole.
      returned: success
      type: dict
      contains:
        expireTime:
          description:
          - The time at which the MembershipRole will expire.
          returned: success
          type: str
    restrictionEvaluations:
      description:
      - Evaluations of restrictions applied to parent group on this membership.
      returned: success
      type: dict
      contains:
        memberRestrictionEvaluation:
          description:
          - Evaluation of the member restriction applied to this membership.
          - Empty if the user lacks permission to view the restriction evaluation.
          returned: success
          type: dict
          contains:
            state:
              description:
              - The current state of the restriction.
              returned: success
              type: str
type:
  description:
  - The type of the membership.
  returned: success
  type: str
deliverySetting:
  description:
  - Delivery setting associated with the membership.
  returned: success
  type: str
'''

ACTIVE = "ACTIVE"

API = 'https://cloudidentity.googleapis.com/v1'

################################################################################
# Imports
################################################################################

from ansible_collections.raphaeldegail.googlecloudy.plugins.module_utils.gcp_utils import (
    return_if_object,
    fetch_resource,
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
            name=dict(type='str'),
            preferred_member_key=dict(no_log=False, type='dict', options=dict(
                id=dict(required=True, type='str'),
                namespace=dict(type='str')
            )),
            group_id=dict(required=True, type='str')
        ),
        mutually_exclusive=[('name', 'preferred_member_key')],
        required_one_of=[('name', 'preferred_member_key')],
        supports_check_mode=True
    )

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/cloud-identity.groups']

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
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        link: str, the URL to call for the API operation.

    Returns:
        dict, the JSON-formatted response for the API call, if it exists.
    """
    auth = GcpSession(module, 'cloudidentity')
    params = {
        'view': 'FULL'
    }
    return_list = auth.list(link, return_if_object, params=params, array_name='memberships')
    for member in return_list:
        if member.get('preferredMemberKey').get('id') == module.params.get('preferred_member_key').get('id'):
            member.update({'parent': module.params.get('parent')})
            return member
    return None


def self_link(module):
    return "{api}/{name}".format(api=API, **module.params)


def collection(module):
    return "{api}/groups/{group_id}/memberships".format(api=API, **module.params)


if __name__ == '__main__':
    main()
