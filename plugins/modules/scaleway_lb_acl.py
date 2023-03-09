#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_lb_acl
short_description: Manage Scaleway lb's acl
description:
    - This module can be used to manage Scaleway lb's acl.
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
    acl_id:
        description: acl_id
        type: str
        required: false
    frontend_id:
        description: frontend_id
        type: str
        required: true
    action:
        description: action
        type: dict
        required: true
    index:
        description: index
        type: int
        required: true
    description:
        description: description
        type: str
        required: true
    region:
        description: region
        type: str
        required: false
        choices:
            - fr-par
            - nl-ams
            - pl-waw
    name:
        description: name
        type: str
        required: false
    match:
        description: match
        type: dict
        required: false
"""

EXAMPLES = r"""
- name: Create a acl
  quantumsheep.scaleway.scaleway_lb_acl:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    frontend_id: "aaaaaa"
    action:
        aaaaaa: bbbbbb
        cccccc: dddddd
    index: "aaaaaa"
    description: "aaaaaa"
"""

RETURN = r"""
---
acl:
    description: The acl information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        name: "aaaaaa"
        match:
            aaaaaa: bbbbbb
            cccccc: dddddd
        action:
            aaaaaa: bbbbbb
            cccccc: dddddd
        frontend:
            aaaaaa: bbbbbb
            cccccc: dddddd
        index: 3
        created_at: "aaaaaa"
        updated_at: "aaaaaa"
        description: "aaaaaa"
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
    from scaleway.lb.v1 import LbV1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = LbV1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_acl(acl_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_acl(**not_none_params)

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = LbV1API(client)

    id = module.params.pop("id", None)
    name = module.params.pop("name", None)

    if id is not None:
        resource = api.get_acl(acl_id=id, region=module.params["region"])
    elif name is not None:
        resources = api.list_acls_all(name=name, region=module.params["region"])
        if len(resources) == 0:
            module.exit_json(msg="No acl found with name {name}")
        elif len(resources) > 1:
            module.exit_json(msg="More than one acl found with name {name}")
        else:
            resource = resources[0]
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_acl(acl_id=resource.id, region=module.params["region"])

    module.exit_json(
        changed=True,
        msg=f"lb's acl {resource.name} ({resource.id}) deleted",
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
        acl_id=dict(type="str"),
        frontend_id=dict(
            type="str",
            required=True,
        ),
        action=dict(
            type="dict",
            required=True,
        ),
        index=dict(
            type="int",
            required=True,
        ),
        description=dict(
            type="str",
            required=True,
        ),
        region=dict(
            type="str",
            required=False,
            choices=["fr-par", "nl-ams", "pl-waw"],
        ),
        name=dict(
            type="str",
            required=False,
        ),
        match=dict(
            type="dict",
            required=False,
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=(["acl_id", "name"],),
        supports_check_mode=True,
    )

    if not HAS_SCALEWAY_SDK:
        module.fail_json(msg=missing_required_lib("scaleway"))

    core(module)


if __name__ == "__main__":
    main()
