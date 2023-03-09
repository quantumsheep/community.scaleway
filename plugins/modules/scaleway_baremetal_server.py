#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_baremetal_server
short_description: Manage Scaleway baremetal's server
description:
    - This module can be used to manage Scaleway baremetal's server.
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
        required: false
    offer_id:
        description: offer_id
        type: str
        required: true
    name:
        description: name
        type: str
        required: true
    description:
        description: description
        type: str
        required: true
    zone:
        description: zone
        type: str
        required: false
    organization_id:
        description: organization_id
        type: str
        required: false
    project_id:
        description: project_id
        type: str
        required: false
    tags:
        description: tags
        type: list
        elements: str
        required: false
    install:
        description: install
        type: dict
        required: false
    option_ids:
        description: option_ids
        type: list
        elements: str
        required: false
"""

EXAMPLES = r"""
- name: Create a server
  quantumsheep.scaleway.scaleway_baremetal_server:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    offer_id: "aaaaaa"
    name: "aaaaaa"
    description: "aaaaaa"
"""

RETURN = r"""
---
server:
    description: The server information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        organization_id: 00000000-0000-0000-0000-000000000000
        project_id: 00000000-0000-0000-0000-000000000000
        name: "aaaaaa"
        description: "aaaaaa"
        updated_at: "aaaaaa"
        created_at: "aaaaaa"
        status: delivering
        offer_id: 00000000-0000-0000-0000-000000000000
        offer_name: "aaaaaa"
        tags:
            - aaaaaa
            - bbbbbb
        ips:
            - aaaaaa
            - bbbbbb
        domain: "aaaaaa"
        boot_type: normal
        zone: "aaaaaa"
        install:
            aaaaaa: bbbbbb
            cccccc: dddddd
        ping_status: ping_status_up
        options:
            - aaaaaa
            - bbbbbb
        rescue_server:
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
    from scaleway import Client, ScalewayException
    from scaleway.baremetal.v1 import BaremetalV1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = BaremetalV1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_server(server_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_server(**not_none_params)
    resource = api.wait_for_server(
        server_id=resource.id, region=module.params["region"]
    )

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = BaremetalV1API(client)

    id = module.params.pop("id", None)
    name = module.params.pop("name", None)

    if id is not None:
        resource = api.get_server(server_id=id, region=module.params["region"])
    elif name is not None:
        resources = api.list_servers_all(name=name, region=module.params["region"])
        if len(resources) == 0:
            module.exit_json(msg="No server found with name {name}")
        elif len(resources) > 1:
            module.exit_json(msg="More than one server found with name {name}")
        else:
            resource = resources[0]
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_server(server_id=resource.id, region=module.params["region"])

    try:
        api.wait_for_server(server_id=resource.id, region=module.params["region"])
    except ScalewayException as e:
        if e.status_code != 404:
            raise e

    module.exit_json(
        changed=True,
        msg=f"baremetal's server {resource.name} ({resource.id}) deleted",
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
        server_id=dict(type="str"),
        offer_id=dict(
            type="str",
            required=True,
        ),
        name=dict(
            type="str",
            required=True,
        ),
        description=dict(
            type="str",
            required=True,
        ),
        zone=dict(
            type="str",
            required=False,
        ),
        organization_id=dict(
            type="str",
            required=False,
        ),
        project_id=dict(
            type="str",
            required=False,
        ),
        tags=dict(
            type="list",
            required=False,
            elements="str",
        ),
        install=dict(
            type="dict",
            required=False,
        ),
        option_ids=dict(
            type="list",
            required=False,
            elements="str",
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=(["server_id", "name"],),
        supports_check_mode=True,
    )

    if not HAS_SCALEWAY_SDK:
        module.fail_json(msg=missing_required_lib("scaleway"))

    core(module)


if __name__ == "__main__":
    main()
