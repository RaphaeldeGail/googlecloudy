# Googlecloudy Ansible Collection
This collection provides modules for the Google Cloud Platform with IAM and other resources missing from the official one.

This collection works with Ansible 2.16+

# Installation
```bash
ansible-galaxy collection install raphaeldegail.googlecloudy
```

# Resources Supported
  * Billing (gcp_billing_association, gcp_billing_account_iam)
  * Cloud Identity Group (gcp_cloudidentity_group, gcp_cloudidentity_group_membership)
  * Cloud IAM Workload Identity (gcp_iam_workloadidentitypool, gcp_iam_identityprovider)
  * Cloud IAM Organization Role (gcp_iam_organization_role)
  * Cloud IAM ServiceAccount (gcp_iam_service_account, gcp_iam_service_account_iam)
  * Resource Manager Folder (gcp_resourcemanager_folder, gcp_resourcemanager_folder_iam)
  * Resource Manager Organization (gcp_resourcemanager_organization_info, gcp_resourcemanager_organization_iam, gcp_resourcemanager_organization_iam_binding)
  * Resource Manager Project (gcp_resourcemanager_project_iam)
  * Resource Manager Tag (gcp_resourcemanager_tagkey, gcp_resourcemanager_tagkey_iam)
