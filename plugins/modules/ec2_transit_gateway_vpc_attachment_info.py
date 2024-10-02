#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: ec2_transit_gateway_vpc_attachment_info
short_description: describes AWS Transit Gateway VPC attachments
version_added: 4.0.0
description:
  - Describes AWS Transit Gateway VPC Attachments.
options:
  id:
    description:
      - The ID of the Transit Gateway Attachment.
      - Mutually exclusive with O(name) and O(filters).
    type: str
    required: false
    aliases: ["attachment_id"]
  name:
    description:
      - The V(Name) tag of the Transit Gateway attachment.
    type: str
    required: false
  filters:
    description:
      - A dictionary of filters to apply. Each dict item consists of a filter key and a filter value.
      - Setting a V(tag:Name) filter will override the O(name) parameter.
    type: dict
    required: false
  include_deleted:
    description:
      - If O(include_deleted=True), then attachments in a deleted state will
        also be returned.
      - Setting a V(state) filter will override the O(include_deleted) parameter.
    type: bool
    required: false
    default: false
author:
  - Mark Chappell (@tremble)
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
- name: Describe a specific Transit Gateway attachment
  community.aws.ec2_transit_gateway_vpc_attachment_info:
    id: "tgw-attach-0123456789abcdef0"

- name: Describe all attachments attached to a transit gateway
  community.aws.ec2_transit_gateway_vpc_attachment_info:
    filters:
      transit-gateway-id: "tgw-0fedcba9876543210"

- name: Describe all attachments in an account
  community.aws.ec2_transit_gateway_vpc_attachment_info:
    filters:
      transit-gateway-id: "tgw-0fedcba9876543210"
"""

RETURN = r"""
transit_gateway_attachments:
  description: The attributes of the Transit Gateway attachments.
  type: list
  elements: dict
  returned: success
  contains:
    creation_time:
      description:
        - An ISO 8601 date time stamp of when the attachment was created.
      type: str
      returned: success
      example: "2022-03-10T16:40:26+00:00"
    options:
      description:
        - Additional VPC attachment options.
      type: dict
      returned: success
      contains:
        appliance_mode_support:
          description:
            - Indicates whether appliance mode support is enabled.
          type: str
          returned: success
          example: "enable"
        dns_support:
          description:
            - Indicates whether DNS support is enabled.
          type: str
          returned: success
          example: "disable"
        ipv6_support:
          description:
            - Indicates whether IPv6 support is disabled.
          type: str
          returned: success
          example: "disable"
    state:
      description:
        - The state of the attachment.
      type: str
      returned: success
      example: "deleting"
    subnet_ids:
      description:
        - The IDs of the subnets in use by the attachment.
      type: list
      elements: str
      returned: success
      example: ["subnet-0123456789abcdef0", "subnet-11111111111111111"]
    tags:
      description:
        - A dictionary representing the resource tags.
      type: dict
      returned: success
    transit_gateway_attachment_id:
      description:
        - The ID of the attachment.
      type: str
      returned: success
      example: "tgw-attach-0c0c5fd0b0f01d1c9"
    transit_gateway_id:
      description:
        - The ID of the transit gateway that the attachment is connected to.
      type: str
      returned: success
      example: "tgw-0123456789abcdef0"
    vpc_id:
      description:
        - The ID of the VPC that the attachment is connected to.
      type: str
      returned: success
      example: "vpc-0123456789abcdef0"
    vpc_owner_id:
      description:
        - The ID of the account that the VPC belongs to.
      type: str
      returned: success
      example: "123456789012"
"""

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.transitgateway import AttachmentValidator


def main():
    argument_spec = dict(
        id=dict(type="str", required=False, aliases=["attachment_id"]),
        name=dict(type="str", required=False),
        filters=dict(type="dict", required=False),
        include_deleted=dict(type="bool", required=False, default=False),
    )

    mutually_exclusive = [
        ["id", "name"],
        ["id", "filters"],
    ]

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=mutually_exclusive,
    )

    # name = module.params.get("name", None)
    # id = module.params.get("id", None)
    # opt_filters = module.params.get("filters", None)
     # Retrieve input parameters from the module
    name = module.params.get("name", None)
    attachment_id = module.params.get("id", None)
    opt_filters = module.params.get("filters", None)
    include_deleted = module.params.get("include_deleted", False)

    client = module.client("ec2")

    # search_manager = TransitGatewayVpcAttachmentManager(client, module=module)
    # filters = dict()

    # if name:
    #     filters["tag:Name"] = name

    # if not module.params.get("include_deleted"):
    #     # Attachments lurk in a 'deleted' state, for a while, ignore them so we
    #     # can reuse the names
    #     filters["state"] = search_manager.get_states()

    # if opt_filters:
    #     filters.update(opt_filters)

    # attachments = search_manager.list(filters=filters, id=id)

    # module.exit_json(changed=False, attachments=attachments, filters=filters)
    # Use the AttachmentValidator to validate and find existing attachments if required
    validator = AttachmentValidator(client, module)
    filters = {}

    # Add filter by name if provided
    if name:
        filters["tag:Name"] = name

    # Include only active states if "include_deleted" is False
    if not include_deleted:
        # Use the helper method to get states that are not "deleted"
        filters["state"] = "available"

    # Include any additional filters provided by the user
    if opt_filters:
        filters.update(opt_filters)

    # Find the existing attachments based on the provided filters and ID using AttachmentValidator
    attachment_ids = []
    if attachment_id:
        attachment_ids.append(attachment_id)
    else:
        attachment = validator.find_existing_attachment(filters=filters)
        if attachment:
            attachment_ids.append(attachment["TransitGatewayAttachmentId"])

    # Prepare the results
    attachments = []
    for attach_id in attachment_ids:
        attachments.append({"transit_gateway_attachment_id": attach_id})

    # Return the results as output
    module.exit_json(changed=False, attachments=attachments, filters=filters)



if __name__ == "__main__":
    main()
