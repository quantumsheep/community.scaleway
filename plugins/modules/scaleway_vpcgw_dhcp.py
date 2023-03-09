#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_vpcgw_dhcp
short_description: Manage Scaleway vpcgw's dhcp
description:
    - This module can be used to manage Scaleway vpcgw's dhcp.
version_added: "2.1.0"
author:
    - Nathanael Demacon (@quantumsheep)
extends_documentation_fragment:
    - quantumsheep.scaleway.scaleway
    - quantumsheep.scaleway.scaleway_waitable_resource
requirements:
    - scaleway >= 0.9.0
options:
    state:
        description:
            - Indicate desired state of the target.
            - C(present) will create the resource.
            - C(absent) will delete the resource, if it exists.
        default: present
        choices: ["present", "absent"]
        type: str
    dhcp_id:
        description: dhcp_id
        type: str
        required: false
    subnet:
        description: subnet
        type: str
        required: true
    zone:
        description: zone
        type: str
        required: false
    project_id:
        description: project_id
        type: str
        required: false
    address:
        description: address
        type: str
        required: false
    pool_low:
        description: pool_low
        type: str
        required: false
    pool_high:
        description: pool_high
        type: str
        required: false
    enable_dynamic:
        description: enable_dynamic
        type: bool
        required: false
    valid_lifetime:
        description: valid_lifetime
        type: str
        required: false
    renew_timer:
        description: renew_timer
        type: str
        required: false
    rebind_timer:
        description: rebind_timer
        type: str
        required: false
    push_default_route:
        description: push_default_route
        type: bool
        required: false
    push_dns_server:
        description: push_dns_server
        type: bool
        required: false
    dns_servers_override:
        description: dns_servers_override
        type: list
        elements: str
        required: false
    dns_search:
        description: dns_search
        type: list
        elements: str
        required: false
    dns_local_name:
        description: dns_local_name
        type: str
        required: false
"""

EXAMPLES = r"""
- name: Create a dhcp
  quantumsheep.scaleway.scaleway_vpcgw_dhcp:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    subnet: "aaaaaa"
"""

RETURN = r"""
---
dhcp:
    description: The dhcp information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        organization_id: 00000000-0000-0000-0000-000000000000
        project_id: 00000000-0000-0000-0000-000000000000
        created_at: "aaaaaa"
        updated_at: "aaaaaa"
        subnet: "aaaaaa"
        address: "aaaaaa"
        pool_low: "aaaaaa"
        pool_high: "aaaaaa"
        enable_dynamic: true
        valid_lifetime: 00000000-0000-0000-0000-000000000000
        renew_timer: "aaaaaa"
        rebind_timer: "aaaaaa"
        push_default_route: true
        push_dns_server: true
        dns_servers_override: 00000000-0000-0000-0000-000000000000
        dns_search:
            - aaaaaa
            - bbbbbb
        dns_local_name: "aaaaaa"
        zone: "aaaaaa"
"""

from ansible.module_utils.basic import (
    AnsibleModule,
    missing_required_lib,
)
from ansible_collections.quantumsheep.scaleway.plugins.module_utils.scaleway import (
    scaleway_argument_spec,
    scaleway_waitable_resource_argument_spec,
    scaleway_get_client_from_module,
    scaleway_pop_client_params,
    scaleway_pop_waitable_resource_params,
)

try:
    from scaleway import Client
    from scaleway.vpcgw.v1 import VpcgwV1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = VpcgwV1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_dhcp(dhcp_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_dhcp(**not_none_params)

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = VpcgwV1API(client)

    id = module.params.pop("id", None)

    if id is not None:
        resource = api.get_dhcp(dhcp_id=id, region=module.params["region"])
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_dhcp(dhcp_id=resource.id, region=module.params["region"])

    module.exit_json(
        changed=True,
        msg=f"vpcgw's dhcp {resource.id} deleted",
    )


def core(module: AnsibleModule) -> None:
    client = scaleway_get_client_from_module(module)

    state = module.params.pop("state")
    scaleway_pop_client_params(module)
    scaleway_pop_waitable_resource_params(module)

    if state == "present":
        create(module, client)
    elif state == "absent":
        delete(module, client)


def main() -> None:
    argument_spec = scaleway_argument_spec()
    argument_spec.update(scaleway_waitable_resource_argument_spec())
    argument_spec.update(
        state=dict(type="str", default="present", choices=["absent", "present"]),
        dhcp_id=dict(type="str"),
        subnet=dict(
            type="str",
            required=True,
        ),
        zone=dict(
            type="str",
            required=False,
        ),
        project_id=dict(
            type="str",
            required=False,
        ),
        address=dict(
            type="str",
            required=False,
        ),
        pool_low=dict(
            type="str",
            required=False,
        ),
        pool_high=dict(
            type="str",
            required=False,
        ),
        enable_dynamic=dict(
            type="bool",
            required=False,
        ),
        valid_lifetime=dict(
            type="str",
            required=False,
        ),
        renew_timer=dict(
            type="str",
            required=False,
        ),
        rebind_timer=dict(
            type="str",
            required=False,
        ),
        push_default_route=dict(
            type="bool",
            required=False,
        ),
        push_dns_server=dict(
            type="bool",
            required=False,
        ),
        dns_servers_override=dict(
            type="list",
            required=False,
            elements="str",
        ),
        dns_search=dict(
            type="list",
            required=False,
            elements="str",
        ),
        dns_local_name=dict(
            type="str",
            required=False,
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    if not HAS_SCALEWAY_SDK:
        module.fail_json(msg=missing_required_lib("scaleway"))

    core(module)


if __name__ == "__main__":
    main()
