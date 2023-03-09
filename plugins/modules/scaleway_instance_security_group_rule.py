#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_instance_security_group_rule
short_description: Manage Scaleway instance's security_group_rule
description:
    - This module can be used to manage Scaleway instance's security_group_rule.
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
    security_group_id:
        description: security_group_id
        type: str
        required: true
    ip_range:
        description: ip_range
        type: str
        required: true
    position:
        description: position
        type: int
        required: true
    editable:
        description: editable
        type: bool
        required: true
    zone:
        description: zone
        type: str
        required: false
    protocol:
        description: protocol
        type: str
        required: true
        choices:
            - TCP
            - UDP
            - ICMP
            - ANY
    direction:
        description: direction
        type: str
        required: true
        choices:
            - inbound
            - outbound
    action:
        description: action
        type: str
        required: true
        choices:
            - accept
            - drop
    dest_port_from:
        description: dest_port_from
        type: int
        required: false
    dest_port_to:
        description: dest_port_to
        type: int
        required: false
"""

EXAMPLES = r"""
- name: Create a security_group_rule
  quantumsheep.scaleway.scaleway_instance_security_group_rule:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    security_group_id: "aaaaaa"
    ip_range: "aaaaaa"
    position: "aaaaaa"
    editable: true
    protocol: "aaaaaa"
    direction: "aaaaaa"
    action: "aaaaaa"
"""

RETURN = r"""
---
security_group_rule:
    description: The security_group_rule information
    returned: when I(state=present)
    type: dict
    sample:
        rule:
            aaaaaa: bbbbbb
            cccccc: dddddd
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
    from scaleway.instance.v1 import InstanceV1APIUtils

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = InstanceV1APIUtils(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_security_group_rule(security_group_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_security_group_rule(**not_none_params)

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = InstanceV1APIUtils(client)

    rule = module.params.pop("rule", None)

    if rule is not None:
        resource = api.get_security_group_rule(
            security_group_id=rule, region=module.params["region"]
        )
    else:
        module.fail_json(msg="rule is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_security_group_rule(
        security_group_id=resource.rule, region=module.params["region"]
    )

    module.exit_json(
        changed=True,
        msg=f"instance's security_group_rule {resource.rule} deleted",
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
        security_group_id=dict(
            type="str",
            required=True,
        ),
        ip_range=dict(
            type="str",
            required=True,
        ),
        position=dict(
            type="int",
            required=True,
        ),
        editable=dict(
            type="bool",
            required=True,
        ),
        zone=dict(
            type="str",
            required=False,
        ),
        protocol=dict(
            type="str",
            required=True,
            choices=["TCP", "UDP", "ICMP", "ANY"],
        ),
        direction=dict(
            type="str",
            required=True,
            choices=["inbound", "outbound"],
        ),
        action=dict(
            type="str",
            required=True,
            choices=["accept", "drop"],
        ),
        dest_port_from=dict(
            type="int",
            required=False,
        ),
        dest_port_to=dict(
            type="int",
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
