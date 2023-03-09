#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_rdb_endpoint
short_description: Manage Scaleway rdb's endpoint
description:
    - This module can be used to manage Scaleway rdb's endpoint.
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
    endpoint_id:
        description: endpoint_id
        type: str
        required: false
    instance_id:
        description: instance_id
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
    endpoint_spec:
        description: endpoint_spec
        type: dict
        required: false
"""

EXAMPLES = r"""
- name: Create a endpoint
  quantumsheep.scaleway.scaleway_rdb_endpoint:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    instance_id: "aaaaaa"
"""

RETURN = r"""
---
endpoint:
    description: The endpoint information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        ip: "aaaaaa"
        port: 3
        name: "aaaaaa"
        private_network:
            aaaaaa: bbbbbb
            cccccc: dddddd
        load_balancer:
            aaaaaa: bbbbbb
            cccccc: dddddd
        direct_access:
            aaaaaa: bbbbbb
            cccccc: dddddd
        hostname: "aaaaaa"
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
    from scaleway.rdb.v1 import RdbV1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = RdbV1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_endpoint(endpoint_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_endpoint(**not_none_params)

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = RdbV1API(client)

    id = module.params.pop("id", None)
    name = module.params.pop("name", None)

    if id is not None:
        resource = api.get_endpoint(endpoint_id=id, region=module.params["region"])
    elif name is not None:
        resources = api.list_endpoints_all(name=name, region=module.params["region"])
        if len(resources) == 0:
            module.exit_json(msg="No endpoint found with name {name}")
        elif len(resources) > 1:
            module.exit_json(msg="More than one endpoint found with name {name}")
        else:
            resource = resources[0]
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_endpoint(endpoint_id=resource.id, region=module.params["region"])

    module.exit_json(
        changed=True,
        msg=f"rdb's endpoint {resource.name} ({resource.id}) deleted",
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
        endpoint_id=dict(type="str"),
        instance_id=dict(
            type="str",
            required=True,
        ),
        region=dict(
            type="str",
            required=False,
            choices=["fr-par", "nl-ams", "pl-waw"],
        ),
        endpoint_spec=dict(
            type="dict",
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
