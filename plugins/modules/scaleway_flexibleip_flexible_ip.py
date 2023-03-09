#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_flexibleip_flexible_ip
short_description: Manage Scaleway flexibleip's flexible_ip
description:
    - This module can be used to manage Scaleway flexibleip's flexible_ip.
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
    fip_id:
        description: fip_id
        type: str
        required: false
    description:
        description: description
        type: str
        required: true
    is_ipv6:
        description: is_ipv6
        type: bool
        required: true
    zone:
        description: zone
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
    server_id:
        description: server_id
        type: str
        required: false
    reverse:
        description: reverse
        type: str
        required: false
"""

EXAMPLES = r"""
- name: Create a flexible_ip
  quantumsheep.scaleway.scaleway_flexibleip_flexible_ip:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    description: "aaaaaa"
    is_ipv6: true
"""

RETURN = r"""
---
flexible_ip:
    description: The flexible_ip information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        organization_id: 00000000-0000-0000-0000-000000000000
        project_id: 00000000-0000-0000-0000-000000000000
        description: "aaaaaa"
        tags:
            - aaaaaa
            - bbbbbb
        updated_at: "aaaaaa"
        created_at: "aaaaaa"
        status: ready
        ip_address: "aaaaaa"
        mac_address:
            aaaaaa: bbbbbb
            cccccc: dddddd
        server_id: 00000000-0000-0000-0000-000000000000
        reverse: "aaaaaa"
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
    from scaleway import Client, ScalewayException
    from scaleway.flexibleip.v1alpha1 import FlexibleipV1Alpha1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = FlexibleipV1Alpha1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_flexible_ip(fip_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_flexible_ip(**not_none_params)
    resource = api.wait_for_flexible_ip(
        fip_id=resource.id, region=module.params["region"]
    )

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = FlexibleipV1Alpha1API(client)

    id = module.params.pop("id", None)

    if id is not None:
        resource = api.get_flexible_ip(fip_id=id, region=module.params["region"])
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_flexible_ip(fip_id=resource.id, region=module.params["region"])

    try:
        api.wait_for_flexible_ip(fip_id=resource.id, region=module.params["region"])
    except ScalewayException as e:
        if e.status_code != 404:
            raise e

    module.exit_json(
        changed=True,
        msg=f"flexibleip's flexible_ip {resource.id} deleted",
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
        fip_id=dict(type="str"),
        description=dict(
            type="str",
            required=True,
        ),
        is_ipv6=dict(
            type="bool",
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
        tags=dict(
            type="list",
            required=False,
            elements="str",
        ),
        server_id=dict(
            type="str",
            required=False,
        ),
        reverse=dict(
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
