#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_instance_private_nic
short_description: Manage Scaleway instance's private_nic
description:
    - This module can be used to manage Scaleway instance's private_nic.
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
    server_id:
        description: server_id
        type: str
        required: true
    private_network_id:
        description: private_network_id
        type: str
        required: true
    zone:
        description: zone
        type: str
        required: false
    tags:
        description: tags
        type: list
        elements: str
        required: false
"""

EXAMPLES = r"""
- name: Create a private_nic
  quantumsheep.scaleway.scaleway_instance_private_nic:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    server_id: "aaaaaa"
    private_network_id: "aaaaaa"
"""

RETURN = r"""
---
private_nic:
    description: The private_nic information
    returned: when I(state=present)
    type: dict
    sample:
        private_nic:
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
        resource = api.get_private_nic(server_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_private_nic(**not_none_params)

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = InstanceV1APIUtils(client)

    private_nic = module.params.pop("private_nic", None)

    if private_nic is not None:
        resource = api.get_private_nic(
            server_id=private_nic, region=module.params["region"]
        )
    else:
        module.fail_json(msg="private_nic is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_private_nic(
        server_id=resource.private_nic, region=module.params["region"]
    )

    module.exit_json(
        changed=True,
        msg=f"instance's private_nic {resource.private_nic} deleted",
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
        server_id=dict(
            type="str",
            required=True,
        ),
        private_network_id=dict(
            type="str",
            required=True,
        ),
        zone=dict(
            type="str",
            required=False,
        ),
        tags=dict(
            type="list",
            required=False,
            elements="str",
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
