# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from copy import deepcopy
try:
    from botocore.exceptions import BotoCoreError
    from botocore.exceptions import ClientError
except ImportError:
    pass

from typing import NoReturn, Optional
from typing import Dict
from typing import Any
from typing import List

from .modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.waiters import get_waiter

from ansible_collections.amazon.aws.plugins.module_utils.transformation import ansible_dict_to_boto3_filter_list

from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AnsibleEC2Error
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_vpc_attachments
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import create_vpc_attachment
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import modify_vpc_attachment
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import delete_vpc_attachment
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import get_tgw_vpc_attachment
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ensure_ec2_tags
from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_subnets
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_specifications
from ansible_collections.amazon.aws.plugins.module_utils.transformation import boto3_resource_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.tagging import ansible_dict_to_boto3_tag_list
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

import logging
logging.basicConfig(filename = '/tmp/file.log',
                    level = logging.DEBUG,
                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

# class TransitGatewayVpcAttachmentManager:
#     TAG_RESOURCE_TYPE = "transit-gateway-attachment"

#     def __init__(self, client, module: AnsibleAWSModule, id: Optional[str] = None) -> None:
#         self.module = module
#         self.subnet_updates = dict()
#         self.id = id
#         self.changed = False
#         self.results = {"changed": False}
#         self.wait = module.params.get("wait")
#         self.connection = client
#         self.check_mode = self.module.check_mode
#         self.original_resource = dict()
#         self.updated_resource = dict()
#         self.resource_updates = dict()
#         self.preupdate_resource = dict()
#         self.wait_timeout = None

#         # Name parameter is unique (by region) and can not be modified.
#         logging.debug(f"self.id boh init: {self.id}")
#         if self.id:
#             resource = deepcopy(self.get_resource())
#             logging.debug(f"resource boh init: {resource}")
#             self.original_resource = resource
#         logging.debug(f"self.original_resource boh init: {self.original_resource}")

#     def get_id_params(self, id: Optional[str] = None, id_list: bool = False) -> Dict[str, List[str]]:
#         if not id:
#             id = self.id
#         if not id:
#             # Users should never see this, but let's cover ourself
#             self.module.fail_json(msg="Attachment identifier parameter missing")

#         if id_list:
#             return dict(TransitGatewayAttachmentIds=[id])
#         return dict(TransitGatewayAttachmentId=id)

#     def filter_immutable_resource_attributes(self, resource: Dict[str, Any]) -> Dict[str, Any]:
#         resource = deepcopy(resource)
#         resource.pop("TransitGatewayId", None)
#         resource.pop("VpcId", None)
#         resource.pop("VpcOwnerId", None)
#         resource.pop("State", None)
#         resource.pop("SubnetIds", None)
#         resource.pop("CreationTime", None)
#         resource.pop("Tags", None)
#         return resource

#     def set_option(self, name: str, value: Optional[bool]) -> bool:
#         if value is None:
#             return False
#         # For now VPC Attachment options are all enable/disable
#         if value:
#             value = "enable"
#         else:
#             value = "disable"

#         options = deepcopy(self.preupdate_resource.get("Options", dict()))
#         options.update(self.resource_updates.get("Options", dict()))
#         options[name] = value

#         return self.set_resource_value("Options", options)

#     def set_tags(self, tags: Dict[str, Any], purge_tags: bool) -> NoReturn:
#         logging.debug(f"set tags self.id: {self.id}")
#         if self.id:
#             result = ensure_ec2_tags(self.connection, self.module, self.id, resource_type=self.TAG_RESOURCE_TYPE, tags=tags, purge_tags=purge_tags)
#             logging.debug(f"tags update: {result}")
#             self.changed = result

#     def set_resource_value(self, key, value, description: Optional[str] = None, immutable: bool = False):
#         if value is None:
#             return False
#         if value == self.get_resource_value(key):
#             return False
#         if immutable and self.original_resource:
#             if description is None:
#                 description = key
#             self.module.fail_json(msg=f"{description} can not be updated after creation")
#         logging.debug(f"key: {key}")
#         logging.debug(f"value: {value}")
#         self.resource_updates[key] = value
#         logging.debug(f"self.resource_updates: {self.resource_updates}")
#         logging.debug(f"self.self.original_resource: {self.original_resource}")
#         self.changed = True
#         return True

#     def get_resource_value(self, key, default=None):
#         default_value = self.preupdate_resource.get(key, default)
#         return self.resource_updates.get(key, default_value)

#     def set_dns_support(self, value: Optional[bool]) -> bool:
#         return self.set_option("DnsSupport", value)

#     def set_multicast_support(self, value: Optional[bool]) -> bool:
#         return self.set_option("MulticastSupport", value)

#     def set_ipv6_support(self, value: Optional[bool]) -> bool:
#         return self.set_option("Ipv6Support", value)

#     def set_appliance_mode_support(self, value: Optional[bool]) -> bool:
#         return self.set_option("ApplianceModeSupport", value)

#     def set_transit_gateway(self, tgw_id: str) -> bool:
#         return self.set_resource_value("TransitGatewayId", tgw_id)

#     def set_vpc(self, vpc_id: str) -> bool:
#         return self.set_resource_value("VpcId", vpc_id)

#     def set_wait(self, wait: bool) -> bool:
#         if wait is None:
#             return False
#         if wait == self.wait:
#             return False

#         self.wait = wait
#         return True

#     def set_wait_timeout(self, timeout: int) -> bool:
#         if timeout is None:
#             return False
#         if timeout == self.wait_timeout:
#             return False

#         self.wait_timeout = timeout
#         return True

#     def set_subnets(self, subnets: Optional[List[str]] = None, purge: bool = True) -> bool:
#         if subnets is None:
#             return False

#         current_subnets = set(self.preupdate_resource.get("SubnetIds", []))
#         desired_subnets = set(subnets)
#         if not purge:
#             desired_subnets = desired_subnets.union(current_subnets)

#         # We'll pull the VPC ID from the subnets, no point asking for
#         # information we 'know'.
#         try:
#             subnet_details = describe_subnets(self.connection, SubnetIds=list(desired_subnets))
#         except AnsibleEC2Error as e:
#             self.module.fail_json_aws_error(e)
#         vpc_id = self.subnets_to_vpc(desired_subnets, subnet_details)
#         self.set_resource_value("VpcId", vpc_id, immutable=True)

#         # Only one subnet per-AZ is permitted
#         azs = [s.get("AvailabilityZoneId") for s in subnet_details]
#         if len(azs) != len(set(azs)):
#             self.module.fail_json(
#                 msg="Only one attachment subnet per availability zone may be set.",
#                 availability_zones=azs,
#                 subnets=subnet_details,
#             )

#         subnets_to_add = list(desired_subnets.difference(current_subnets))
#         subnets_to_remove = list(current_subnets.difference(desired_subnets))
#         if not subnets_to_remove and not subnets_to_add:
#             return False
#         self.subnet_updates = dict(add=subnets_to_add, remove=subnets_to_remove)
#         self.set_resource_value("SubnetIds", list(desired_subnets))
#         return True

#     @staticmethod
#     def subnets_to_vpc(client, module, subnets: List[str], subnet_details: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
#         if not subnets:
#             return None

#         if subnet_details is None:
#             try:
#                 subnet_details = describe_subnets(client, SubnetIds=list(subnets))
#             except AnsibleEC2Error as e:
#                 module.fail_json_aws_error(e)

#         vpcs = [s.get("VpcId") for s in subnet_details]
#         if len(set(vpcs)) > 1:
#             module.fail_json(
#                 msg="Attachment subnets may only be in one VPC, multiple VPCs found",
#                 vpcs=list(set(vpcs)),
#                 subnets=subnet_details,
#             )

#         return vpcs[0]

#     def merge_resource_changes(self, filter_immutable=True, creation=False):
#         resource = deepcopy(self.preupdate_resource)
#         resource.update(self.resource_updates)

#         if filter_immutable:
#             resource = self.filter_immutable_resource_attributes(resource)

#         if creation and self.module.params.get("tags") is not None:
#             logging.debug(f"creation: {creation}")
#             resource["TagSpecifications"] = boto3_tag_specifications(self.module.params.get("tags"), types=[self.TAG_RESOURCE_TYPE])

#         logging.debug(f"resource here :{resource}")
#         return resource

#     def wait_tgw_attachment_deleted(self, **params: Any) -> None:
#         if self.wait:
#             try:
#                 waiter = get_waiter(self.connection, "transit_gateway_vpc_attachment_deleted")
#                 waiter.wait(**params)
#             except (BotoCoreError, ClientError) as e:
#                 self.module.fail_json_aws(e)

#     def wait_tgw_attachment_available(self, **params: Any) -> None:
#         if self.wait:
#             try:
#                 waiter = get_waiter(self.connection, "transit_gateway_vpc_attachment_available")
#                 waiter.wait(**params)
#             except (BotoCoreError, ClientError) as e:
#                 self.module.fail_json_aws(e)

#     def do_deletion_wait(self, id: Optional[str] = None, **params: Any) -> None:
#         all_params = self.get_id_params(id=id, id_list=True)
#         all_params.update(**params)
#         return self.wait_tgw_attachment_deleted(**all_params)

#     def do_creation_wait(self, id: Optional[str] = None, **params: Any) -> None:
#         all_params = self.get_id_params(id=id, id_list=True)
#         all_params.update(**params)
#         return self.wait_tgw_attachment_available(**all_params)

#     def do_update_wait(self, id: Optional[str] = None, **params: Any) -> None:
#         all_params = self.get_id_params(id=id, id_list=True)
#         all_params.update(**params)
#         return self.wait_tgw_attachment_available(**all_params)

#     @property
#     def waiter_config(self):
#         params = dict()
#         if self.wait_timeout:
#             delay = min(5, self.wait_timeout)
#             max_attempts = self.wait_timeout // delay
#             config = dict(Delay=delay, MaxAttempts=max_attempts)
#             params["WaiterConfig"] = config
#         return params

#     def wait_for_deletion(self):
#         if not self.wait:
#             return
#         params = self.waiter_config
#         self.do_deletion_wait(**params)

#     def wait_for_creation(self):
#         if not self.wait:
#             return
#         params = self.waiter_config
#         self.do_creation_wait(**params)

#     def wait_for_update(self):
#         if not self.wait:
#             return
#         params = self.waiter_config
#         self.do_update_wait(**params)

#     def generate_updated_resource(self):
#         """
#         Merges all pending changes into self.updated_resource
#         Used during check mode where it's not possible to get and
#         refresh the resource
#         """
#         return self.merge_resource_changes(filter_immutable=False)

#     def flush_create(self):
#         changed = True

#         if not self.module.check_mode:
#             changed = self.do_create_resource()
#             self.wait_for_creation()
#             self.do_creation_wait()
#             self.updated_resource = self.get_resource()
#         else:  # (CHECK MODE)
#             self.updated_resource = self.normalize_tgw_attachment(self.generate_updated_resource())

#         self.resource_updates = dict()
#         self.changed = changed
#         return True

#     def check_updates_pending(self):
#         if self.resource_updates:
#             return True
#         return False

#     def do_create_resource(self) -> Optional[Dict[str, Any]]:
#         params = self.merge_resource_changes(filter_immutable=False, creation=True)
#         try:
#             response = create_vpc_attachment(self.connection, **params)
#         except AnsibleEC2Error as e:
#             self.module.fail_json_aws_error(e)
#         if response:
#             self.id = response.get("TransitGatewayAttachmentId", None)
#         return response

#     def do_update_resource(self) -> bool:
#         if self.preupdate_resource.get("State", None) == "pending":
#             # Resources generally don't like it if you try to update before creation
#             # is complete.  If things are in a 'pending' state they'll often throw
#             # exceptions.

#             self.wait_for_creation()
#         elif self.preupdate_resource.get("State", None) == "deleting":
#             self.module.fail_json(msg="Deletion in progress, unable to update", route_tables=[self.original_resource])

#         updates = self.filter_immutable_resource_attributes(self.resource_updates)
#         subnets_to_add = self.subnet_updates.get("add", [])
#         subnets_to_remove = self.subnet_updates.get("remove", [])
#         if subnets_to_add:
#             updates["AddSubnetIds"] = subnets_to_add
#         if subnets_to_remove:
#             updates["RemoveSubnetIds"] = subnets_to_remove

#         if not updates:
#             return False

#         if self.module.check_mode:
#             return True

#         updates.update(self.get_id_params(id_list=False))
#         try:
#             modify_vpc_attachment(self.connection, **updates)
#         except AnsibleEC2Error as e:
#             self.module.fail_json_aws_error(e)
#         return True

#     def get_resource(self) -> Optional[Dict[str, Any]]:
#         return self.get_attachment()

#     def delete(self, id: Optional[str] = None) -> bool:
#         if id:
#             id_params = self.get_id_params(id=id, id_list=True)
#             result = get_tgw_vpc_attachment(self.connection, self.module, **id_params)
#         else:
#             result = self.preupdate_resource

#         self.updated_resource = dict()

#         if not result:
#             return False

#         if result.get("State") == "deleting":
#             self.wait_for_deletion()
#             return False

#         if self.module.check_mode:
#             self.changed = True
#             return True

#         id_params = self.get_id_params(id=id, id_list=False)

#         try:
#             result = delete_vpc_attachment(self.connection, **id_params)
#         except AnsibleEC2Error as e:
#             self.module.fail_json_aws_error(e)

#         self.changed |= bool(result)

#         self.wait_for_deletion()
#         return bool(result)

#     # def list(self, filters: Optional[Dict[str, Any]] = None, id: Optional[str] = None) -> List[Dict[str, Any]]:
#     #     params = dict()
#     #     if id:
#     #         params["TransitGatewayAttachmentIds"] = [id]
#     #     if filters:
#     #         params["Filters"] = ansible_dict_to_boto3_filter_list(filters)
#     #     logging.debug(f"params list: {params}")
#     #     try:
#     #         attachments = describe_vpc_attachments(self.connection, **params)
#     #     except AnsibleEC2Error as e:
#     #         self.module.fail_json_aws_error(e)
#     #     logging.debug(f"attachments list: {attachments}")
#     #     if not attachments:
#     #         return []

#     #     return [self.normalize_tgw_attachment(a) for a in attachments]

#     def get_attachment(self, id: Optional[str] = None) -> Optional[Dict[str, Any]]:
#         # RouteTable needs a list, Association/Propagation needs a single ID
#         id_params = self.get_id_params(id=id, id_list=True)
#         result = get_tgw_vpc_attachment(self.connection, self.module, **id_params)

#         if not result:
#             return None

#         logging.debug(f"result: {result}")

#         if not id:
#             self.preupdate_resource = deepcopy(result)
#             logging.debug(f"self.preupdate_resource: {self.preupdate_resource}")

#         attachment = self.normalize_tgw_attachment(result)
#         logging.debug(f"attachment: {attachment}")

#         return attachment

#     def normalize_tgw_attachment(self, resource: Dict[str, Any]) -> Dict[str, Any]:
#         return boto3_resource_to_ansible_dict(resource)

#     def get_states(self) -> List[str]:
#         return [
#             "available",
#             "deleting",
#             "failed",
#             "failing",
#             "initiatingRequest",
#             "modifying",
#             "pendingAcceptance",
#             "pending",
#             "rollingBack",
#             "rejected",
#             "rejecting",
#         ]

#     def flush_update(self):
#         logging.debug(f"self.check_updates_pending(): {self.check_updates_pending()}")
#         if not self.check_updates_pending():
#             self.updated_resource = self.original_resource
#             return False

#         if not self.module.check_mode:
#             self.do_update_resource()
#             self.wait_for_update()
#             self.updated_resource = self.get_resource()
#         else:  # (CHECK_MODE)
#             self.updated_resource = self.normalize_tgw_attachment(self.generate_updated_resource())

#         self._resource_updates = dict()
#         return True

#     def flush_changes(self):
#         logging.debug(f"flush changes self.original_resource: {self.original_resource}")
#         if self.original_resource:
#             logging.debug("Inside update")
#             logging.debug(f"self.original_resource update: {self.original_resource}")
#             return self.flush_update()
#         else:
#             return self.flush_create()


class TransitGatewayAttachmentStateManager:
    def __init__(self, client, module, attachment_id):
        self.client = client
        self.module = module
        self.attachment_id = attachment_id

    def create_attachment(self, params):
        # Create a new transit gateway attachment

        if params.get("Tags"):
            params["TagSpecifications"] = boto3_tag_specifications(params.get("Tags"), types=["transit-gateway-attachment"])
            params.pop("Tags")

        try:
            response = create_vpc_attachment(self.client, **params)
        except AnsibleEC2Error as e:
            self.module.fail_json_aws_error(e)
        self.attachment_id = response['TransitGatewayAttachmentId']
        return self.attachment_id

    def delete_attachment(self):
        # Delete the transit gateway attachment
        if self.attachment_id:
            if not self.module.check_mode:
                params = dict(TransitGatewayAttachmentId=self.attachment_id)
                try:
                    delete_vpc_attachment(self.client, **params)
                except AnsibleEC2Error as e:
                    self.module.fail_json_aws_error(e)
            return True
        return False

    @property
    def waiter_config(self):
        params = dict()
        if self.module.params.get("wait_timeout"):
            delay = min(5, self.module.params.get("wait_timeout"))
            max_attempts =self.module.params.get("wait_timeout") // delay
            config = dict(Delay=delay, MaxAttempts=max_attempts)
            params["WaiterConfig"] = config
        return params

    def wait_for_state_change(self, desired_state):
        # Wait until attachment reaches the desired state
        params = {"TransitGatewayAttachmentIds": [self.attachment_id]}
        params.update(self.waiter_config)
        try:
            waiter = get_waiter(self.client, f'transit_gateway_vpc_attachment_{desired_state}')
            waiter.wait(**params)
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

class AttachmentConfigurationManager:
    def __init__(self, client, module, attachment_id, existing, validator):
        self.client = client
        self.module = module
        self.validator = validator
        self.attachment_id = attachment_id

        self.existing = existing or {}
        self.resource_updates = {}
        self.subnets_to_add = []
        self.subnets_to_remove = []

    def get_resource_updates(self):
        return self.resource_updates

    def set_subnets(self, subnets: Optional[List[str]] = None, purge: bool = True):
        # Set or update the subnets associated with the attachment
        if subnets is None:
            return False

        current_subnets = set(self.existing.get("SubnetIds", []))
        desired_subnets = set(subnets)
        if not purge:
            desired_subnets = desired_subnets.union(current_subnets)

        # We'll pull the VPC ID from the subnets, no point asking for
        # information we 'know'.
        try:
            subnet_details = describe_subnets(self.client, SubnetIds=list(desired_subnets))
        except AnsibleEC2Error as e:
            self.module.fail_json_aws_error(e)
        vpc_id = self.validator.subnets_to_vpc(desired_subnets, subnet_details)
        self._set_resource_value("VpcId", vpc_id, immutable=True)
        #self.to_be_updated["vpc_id"] = vpc_id

        # Only one subnet per-AZ is permitted
        azs = [s.get("AvailabilityZoneId") for s in subnet_details]
        if len(azs) != len(set(azs)):
            self.module.fail_json(
                msg="Only one attachment subnet per availability zone may be set.",
                availability_zones=azs,
                subnets=subnet_details,
            )

        logging.debug(f"desired_subnets: {desired_subnets}")
        logging.debug(f"current_subnets: {current_subnets}")
        self.subnets_to_add = list(desired_subnets.difference(current_subnets))
        self.subnets_to_remove = list(current_subnets.difference(desired_subnets))
        logging.debug(f"self.subnets_to_add: {self.subnets_to_add}")
        logging.debug(f"self.subnets_to_remove: {self.subnets_to_remove}")
        self._set_resource_value("SubnetIds", list(desired_subnets))
        #self.to_be_updated["subnets"] = desired_subnets

    def set_dns_support(self, value):
        # Set or modify DNS support for the attachment
        # if dns_support is not None:
        #     if dns_support is False:
        #         self.dns_support = "disable"
        #     if dns_support is True:
        #         self.dns_support = "enable"
        return self._set_option("DnsSupport", value)

    def set_ipv6_support(self, value):
        # Set or modify IPv6 support for the attachment
        # if ipv6_support is not None:
        #     if ipv6_support is False:
        #         self.ipv6_support = "disable"
        #     if ipv6_support is True:
        #         self.ipv6_support = "enable"
        return self._set_option("Ipv6Support", value)

    def set_appliance_mode_support(self, value):
        # Set or modify appliance mode support for the attachment
        # if appliance_mode_support is not None:
        #     if appliance_mode_support is False:
        #         self.appliance_mode_support = "disable"
        #     if appliance_mode_support is True:
        #         self.appliance_mode_support = "enable"
        return self._set_option("ApplianceModeSupport", value)

    def set_transit_gateway(self, tgw_id):
        return self._set_resource_value("TransitGatewayId", tgw_id)

    def set_vpc(self, vpc_id):
        return self._set_resource_value("VpcId", vpc_id)

    def set_tags(self, tags, purge_tags):
        current_tags = boto3_tag_list_to_ansible_dict(self.existing.get("Tags", None))

        if purge_tags:
            desired_tags = deepcopy(tags)
        else:
            desired_tags = deepcopy(current_tags)
            desired_tags.update(tags)

        self._set_resource_value("Tags", desired_tags)

    def _get_resource_value(self, key, default=None):
        default_value = self.existing.get(key, default)
        return self.resource_updates.get(key, default_value)

    def _set_option(self, name: str, value: Optional[bool]) -> bool:
        if value is None:
            return False
        # For now VPC Attachment options are all enable/disable
        if value:
            value = "enable"
        else:
            value = "disable"

        options = deepcopy(self.existing.get("Options", dict()))
        options.update(self.resource_updates.get("Options", dict()))
        options[name] = value

        return self._set_resource_value("Options", options)

    def _set_resource_value(self, key, value, description: Optional[str] = None, immutable: bool = False):
        if value is None:
            return False
        if value == self._get_resource_value(key):
            return False
        if immutable and self.existing:
            if description is None:
                description = key
            self.module.fail_json(msg=f"{description} can not be updated after creation")

        self.resource_updates[key] = value

        return True

    def filter_immutable_resource_attributes(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        resource = deepcopy(resource)
        resource.pop("TransitGatewayId", None)
        resource.pop("VpcId", None)
        resource.pop("VpcOwnerId", None)
        resource.pop("State", None)
        resource.pop("SubnetIds", None)
        resource.pop("CreationTime", None)
        resource.pop("Tags", None)
        return resource

    def apply_configuration(self):
        # Apply any configuration changes to the attachment
        if self.attachment_id:
            updates = self.filter_immutable_resource_attributes(self.resource_updates)

            if self.subnets_to_add == [] and self.subnets_to_add == [] and not updates:
                return False

            if self.subnets_to_add:
                updates["AddSubnetIds"] = self.subnets_to_add
            if self.subnets_to_remove:
                updates["RemoveSubnetIds"] = self.subnets_to_remove

            updates["TransitGatewayAttachmentId"] = self.attachment_id

            if not self.module.check_mode:
                try:
                    modify_vpc_attachment(self.client, **updates)
                except AnsibleEC2Error as e:
                    self.module.fail_json_aws_error(e)
            return True
        return False


class AttachmentValidator:
    def __init__(self, client, module, attachment_id=None):
        self.client = client
        self.module = module
        self.attachment_id = attachment_id

    def get_states(self) -> List[str]:
        return [
            "available",
            "deleting",
            "failed",
            "failing",
            "initiatingRequest",
            "modifying",
            "pendingAcceptance",
            "pending",
            "rollingBack",
            "rejected",
            "rejecting",
        ]

    # def validate_parameters(self, module_params):
    #     # Validate if all required parameters are provided
    #     if not self.attachment_id and module_params.get("state") == "present":
    #         if not module_params.get("transit_gateway"):
    #             self.module.fail_json(
    #                 "No existing attachment found. To create a new attachment"
    #                 " the `transit_gateway` parameter must be provided."
    #             )
    #         if module_params.get("subnets"):
    #             self.module.fail_json(
    #                 "No existing attachment found. To create a new attachment"
    #                 " the `subnets` parameter must be provided."
    #             )

    def find_existing_attachment(self, filters=None, attachment_id=None):
        # Find an existing attachment based on filters
        params = dict()
        if attachment_id:
            params = dict(TransitGatewayAttachmentIds=[attachment_id])
        elif filters:
            params = dict(Filters=ansible_dict_to_boto3_filter_list(filters))
        try:
            attachments = describe_vpc_attachments(self.client, **params)
        except AnsibleEC2Error as e:
            self.module.fail_json_aws_error(e)
        if len(attachments) > 1:
            raise ValueError("Multiple matching attachments found, provide an ID.")
        return attachments[0] if attachments else None

    def subnets_to_vpc(self, subnets: List[str], subnet_details: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
        if not subnets:
            return None

        if subnet_details is None:
            try:
                subnet_details = describe_subnets(self.client, SubnetIds=list(subnets))
            except AnsibleEC2Error as e:
                self.module.fail_json_aws_error(e)

        vpcs = [s.get("VpcId") for s in subnet_details]
        if len(set(vpcs)) > 1:
            self.module.fail_json(
                msg="Attachment subnets may only be in one VPC, multiple VPCs found",
                vpcs=list(set(vpcs)),
                subnets=subnet_details,
            )

        return vpcs[0]

class TransitGatewayVpcAttachmentManager:
    def __init__(self, client, module, existing, attachment_id=None):
        self.client = client
        self.module = module
        self.attachment_id = attachment_id
        self.existing = existing or {}
        self.updated = {}
        self.changed = False

        # Split responsibilities
        self.validator = AttachmentValidator(client, module, attachment_id)
        self.state_manager = TransitGatewayAttachmentStateManager(client, module, attachment_id)
        self.config_manager = AttachmentConfigurationManager(client, module, attachment_id, existing, self.validator)

    def merge_resource_changes(self, filter_immutable=True, creation=False):
        resource = deepcopy(self.existing)
        resource.update(self.config_manager.get_resource_updates())

        if filter_immutable:
            resource = self.config_manager.filter_immutable_resource_attributes(resource)

        logging.debug(f"resource here :{resource}")
        return resource

    def create_or_modify_attachment(self):
        # Validate input
        # self.validator.validate_parameters(self.module.params)

        # Create or modify
        logging.debug(f"create self.attachment_id: {self.attachment_id}")
        self.config_manager.set_transit_gateway(self.module.params.get("transit_gateway"))
        self.config_manager.set_subnets(self.module.params["subnets"], self.module.params.get("purge_subnets", True))
        self.config_manager.set_dns_support(self.module.params.get("dns_support"))
        self.config_manager.set_ipv6_support(self.module.params.get("ipv6_support"))
        self.config_manager.set_appliance_mode_support(self.module.params.get("appliance_mode_support"))

        tags = self.module.params.get("tags")
        purge_tags = self.module.params.get("purge_tags")
        if self.module.params.get("name"):
            new_tags = dict(Name=self.module.params.get("name"))
            if tags is None:
                purge_tags = False
            else:
                new_tags.update(tags)
            tags = new_tags

        self.config_manager.set_tags(tags, purge_tags)

        if not self.existing:
            if not self.module.check_mode:
                params = self.merge_resource_changes(filter_immutable=False, creation=True)
                self.attachment_id = self.state_manager.create_attachment(params)
                if self.module.params.get("wait"):
                    self.state_manager.wait_for_state_change("available")
            self.changed = True

        else:
            if self.existing.get("State", None) == "pending":
                # Resources generally don't like it if you try to update before creation
                # is complete. If things are in a 'pending' state they'll often throw
                # exceptions.
                self.state_manager.wait_for_state_change("available")
            elif self.existing.get("State", None) == "deleting":
                self.module.fail_json(msg="Deletion in progress, unable to update", route_tables=[self.original_resource])
            # Apply configuration and tags
            if self.config_manager.apply_configuration():
                self.changed = True
                if self.module.params.get("wait"):
                    self.state_manager.wait_for_state_change("available")

            self.changed |= ensure_ec2_tags(self.client, self.module, self.attachment_id, resource_type="transit-gateway-attachment", tags=tags, purge_tags=purge_tags)

        if self.module.check_mode and not self.existing:
            logging.debug("ISNIDEEEEEEEE")
            self.updated = camel_dict_to_snake_dict(self.config_manager.get_resource_updates(), ignore_list=["Tags"])
            logging.debug(f"self.updated: {self.updated}")
        else:
            if self.module.check_mode:
                self.updated = camel_dict_to_snake_dict(self.merge_resource_changes(filter_immutable=False, creation=False), ignore_list=["Tags"])
            else:
                self.updated = boto3_resource_to_ansible_dict(self.validator.find_existing_attachment(attachment_id=self.attachment_id))

    def delete_attachment(self):
        # Delete
        self.changed |= self.state_manager.delete_attachment()
        if self.module.params.get("wait"):
            self.state_manager.wait_for_state_change("deleted")
