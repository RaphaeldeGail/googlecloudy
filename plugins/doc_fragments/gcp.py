# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Google Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    # GCP doc fragment.
    DOCUMENTATION = r'''
author: Raphaël de Gail (@RaphaeldeGail)
requirements:
- python >= 3.11
- requests >= 2.32.2
- google-auth >= 2.33.0
options:
    access_token:
        description:
        - An OAuth2 access token if credential type is accesstoken.
        type: str
    project:
        description:
        - The Google Cloud Platform project to use for API calls.
        type: str
    auth_kind:
        description:
        - The type of credential used.
        type: str
        required: true
        choices:
        - application
        - machineaccount
        - serviceaccount
        - accesstoken
    service_account_contents:
        description:
        - The contents of a Service Account JSON file, either in a dictionary or as a
          JSON string that represents it.
        type: jsonarg
    service_account_file:
        description:
        - The path of a Service Account JSON file if serviceaccount is selected as type.
        type: path
    service_account_email:
        description:
        - An optional service account email address if machineaccount is selected and
          the user does not wish to use the default email.
        type: str
    scopes:
        description:
        - Array of scopes to be used
        type: list
        elements: str
    env_type:
        description:
        - Specifies which Ansible environment you're running this module within.
        - This should not be set unless you know what you're doing.
        - This only alters the User Agent string for any API requests.
        type: str
notes:
  - for authentication, you can set service_account_file using the
    c(GCP_SERVICE_ACCOUNT_FILE) env variable.
  - for authentication, you can set service_account_contents using the
    c(GCP_SERVICE_ACCOUNT_CONTENTS) env variable.
  - For authentication, you can set service_account_email using the
    C(GCP_SERVICE_ACCOUNT_EMAIL) env variable.
  - For authentication, you can set auth_kind using the C(GCP_AUTH_KIND) env
    variable.
  - For authentication, you can set scopes using the C(GCP_SCOPES) env variable.
  - Environment variables values will only be used if the playbook values are
    not set.
  - The I(service_account_email) and I(service_account_file) options are
    mutually exclusive.
'''

    IAM = r'''
options:
    bindings:
        description:
        - Associates a list of members, or principals, with a role.
          Optionally, may specify a condition that determines how and when the bindings are applied.
          Each of the bindings must contain at least one principal.
        - The bindings in a Policy can refer to up to 1,500 principals; up to 250 of these principals can be Google groups.
          Each occurrence of a principal counts towards these limits.
          For example, if the bindings grant 50 different roles to user:alice@example.com, and not to any other principal,
          then you can add another 1,450 principals to the bindings in the Policy.
        required: true
        type: list
        elements: dict
        suboptions:
            role:
                description:
                - Role that is assigned to the list of members, or principals.
                  For example, roles/viewer, roles/editor, or roles/owner.
                required: true
                type: str
            members:
                description:
                - Specifies the principals requesting access for a Google Cloud resource.
                - "members can have the following values:"
                - "- allUsers: A special identifier that represents anyone who is on the internet; with or without a Google account."
                - "- allAuthenticatedUsers: A special identifier that represents anyone who is authenticated with a Google account or a service account.
                  Does not include identities that come from external identity providers (IdPs) through identity federation."
                - "- user:{emailid}: An email address that represents a specific Google account.
                  For example, alice@example.com."
                - "- serviceAccount:{emailid}: An email address that represents a Google service account.
                  For example, my-other-app@appspot.gserviceaccount.com."
                - "- serviceAccount:{projectid}.svc.id.goog[{namespace}/{kubernetes-sa}]: An identifier for a Kubernetes service account.
                  For example, my-project.svc.id.goog[my-namespace/my-kubernetes-sa]."
                - "- group:{emailid}: An email address that represents a Google group.
                  For example, admins@example.com."
                - "- domain:{domain}: The G Suite domain (primary) that represents all the users of that domain.
                  For example, google.com or example.com."
                - "- principal://iam.googleapis.com/locations/global/workforcePools/{pool_id}/subject/{subject_attribute_value}:
                  A single identity in a workforce identity pool."
                - "- principalSet://iam.googleapis.com/locations/global/workforcePools/{pool_id}/group/{groupId}: All workforce identities in a group."
                - "- principalSet://iam.googleapis.com/locations/global/workforcePools/{pool_id}/attribute.{attribute_name}/{attribute_value}:
                  All workforce identities with a specific attribute value."
                - "- principalSet://iam.googleapis.com/locations/global/workforcePools/{pool_id}/*: All identities in a workforce identity pool."
                - "- principal://iam.googleapis.com/projects/{projectNumber}/locations/global/workloadIdentityPools/{pool_id}/subject/{subject_attribute_value}:
                  A single identity in a workload identity pool."
                - "- principalSet://iam.googleapis.com/projects/{projectNumber}/locations/global/workloadIdentityPools/{pool_id}/group/{groupId}:
                  A workload identity pool group."
                - "- principalSet://iam.googleapis.com/projects/{projectNumber}/locations/global/workloadIdentityPools/{pool_id}/attribute.{attribute_name}/{attribute_value}:
                  All identities in a workload identity pool with a certain attribute."
                - "- principalSet://iam.googleapis.com/projects/{projectNumber}/locations/global/workloadIdentityPools/{pool_id}/*:
                  All identities in a workload identity pool."
                - "- deleted:user:{emailid}?uid={uniqueid}: An email address (plus unique identifier) representing a user that has been recently deleted.
                  For example, alice@example.com?uid=123456789012345678901.
                  If the user is recovered, this value reverts to user:{emailid} and the recovered user retains the role in the binding."
                - "- deleted:serviceAccount:{emailid}?uid={uniqueid}:
                  An email address (plus unique identifier) representing a service account that has been recently deleted.
                  For example, my-other-app@appspot.gserviceaccount.com?uid=123456789012345678901.
                  If the service account is undeleted, this value reverts to serviceAccount:{emailid} and the undeleted
                  service account retains the role in the binding."
                - "- deleted:group:{emailid}?uid={uniqueid}:
                  An email address (plus unique identifier) representing a Google group that has been recently deleted.
                  For example, admins@example.com?uid=123456789012345678901.
                  If the group is recovered, this value reverts to group:{emailid} and the recovered group retains the role in the binding."
                - "- deleted:principal://iam.googleapis.com/locations/global/workforcePools/{pool_id}/subject/{subject_attribute_value}:
                  Deleted single identity in a workforce identity pool.
                  For example, deleted:principal://iam.googleapis.com/locations/global/workforcePools/my-pool-id/subject/my-subject-attribute-value."
                required: true
                type: list
                elements: str
            condition:
                description:
                - The condition that is associated with this binding.
                - If the condition evaluates to true, then this binding applies to the current request.
                - If the condition evaluates to false, then this binding does not apply to the current request.
                  However, a different role binding might grant the same role to one or more of the principals in this binding.
                required: false
                type: dict
                suboptions:
                    expression:
                        description:
                        - Textual representation of an expression in Common Expression Language syntax.
                        required: true
                        type: str
                    title:
                        description:
                        - Title for the expression, i.e. a short string describing its purpose.
                          This can be used e.g. in UIs which allow to enter the expression.
                        required: false
                        type: str
                    description:
                        description:
                        - Description of the expression.
                          This is a longer text which describes the expression, e.g. when hovered over it in a UI.
                        required: false
                        type: str
                    location:
                        description:
                        - String indicating the location of the expression for error reporting, e.g. a file name and a position in the file.
                        required: false
                        type: str
    policy_version:
        description:
        - Specifies the format of the policy.
          Requests that specify an invalid value are rejected.
          Any operation that affects conditional role bindings must specify version 3.
        - "This requirement applies to the following operations:"
        - Getting a policy that includes a conditional role binding
        - Adding a conditional role binding to a policy
        - Changing a conditional role binding in a policy
        - Removing any role binding, with or without a condition, from a policy that includes conditions
        - "Important: If you use IAM Conditions, you must include the etag field whenever you call setIamPolicy."
        - If you omit this field, then IAM allows you to overwrite a version 3 policy with a version 1 policy,
          and all of the conditions in the version 3 policy are lost.
        - If a policy does not include any conditions, operations on that policy may specify any valid version or leave the field unset.
        choices:
        - '1'
        - '2'
        - '3'
        default: '1'
        type: str
'''
