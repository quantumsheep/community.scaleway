#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_container
short_description: Manage Scaleway container's container
description:
    - This module can be used to manage Scaleway container's container.
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
    container_id:
        description: container_id
        type: str
        required: false
    namespace_id:
        description: namespace_id
        type: str
        required: true
    privacy:
        description: privacy
        type: str
        required: true
        choices:
            - unknown_privacy
            - public
            - private
    protocol:
        description: protocol
        type: str
        required: true
        choices:
            - unknown_protocol
            - http1
            - h2c
    http_option:
        description: http_option
        type: str
        required: true
        choices:
            - unknown_http_option
            - enabled
            - redirected
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
    environment_variables:
        description: environment_variables
        type: dict
        required: false
    min_scale:
        description: min_scale
        type: int
        required: false
    max_scale:
        description: max_scale
        type: int
        required: false
    memory_limit:
        description: memory_limit
        type: int
        required: false
    timeout:
        description: timeout
        type: str
        required: false
    description:
        description: description
        type: str
        required: false
    registry_image:
        description: registry_image
        type: str
        required: false
    max_concurrency:
        description: max_concurrency
        type: int
        required: false
    port:
        description: port
        type: int
        required: false
    secret_environment_variables:
        description: secret_environment_variables
        type: list
        elements: str
        required: false
"""

EXAMPLES = r"""
- name: Create a container
  quantumsheep.scaleway.scaleway_container:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    namespace_id: "aaaaaa"
    privacy: "aaaaaa"
    protocol: "aaaaaa"
    http_option: "aaaaaa"
"""

RETURN = r"""
---
container:
    description: The container information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        name: "aaaaaa"
        namespace_id: 00000000-0000-0000-0000-000000000000
        status: ready
        environment_variables:
            aaaaaa: bbbbbb
            cccccc: dddddd
        min_scale: 3
        max_scale: 3
        memory_limit: 3
        cpu_limit: 3
        timeout: "aaaaaa"
        error_message: "aaaaaa"
        privacy: public
        description: "aaaaaa"
        registry_image: "aaaaaa"
        max_concurrency: 3
        domain_name: "aaaaaa"
        protocol: http1
        port: 3
        secret_environment_variables:
            - aaaaaa
            - bbbbbb
        http_option: enabled
        region: fr-par
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
    from scaleway.container.v1beta1 import ContainerV1Beta1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = ContainerV1Beta1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_container(container_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_container(**not_none_params)
    resource = api.wait_for_container(
        container_id=resource.id, region=module.params["region"]
    )

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = ContainerV1Beta1API(client)

    id = module.params.pop("id", None)
    name = module.params.pop("name", None)

    if id is not None:
        resource = api.get_container(container_id=id, region=module.params["region"])
    elif name is not None:
        resources = api.list_containers_all(name=name, region=module.params["region"])
        if len(resources) == 0:
            module.exit_json(msg="No container found with name {name}")
        elif len(resources) > 1:
            module.exit_json(msg="More than one container found with name {name}")
        else:
            resource = resources[0]
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_container(container_id=resource.id, region=module.params["region"])

    try:
        api.wait_for_container(container_id=resource.id, region=module.params["region"])
    except ScalewayException as e:
        if e.status_code != 404:
            raise e

    module.exit_json(
        changed=True,
        msg=f"container's container {resource.name} ({resource.id}) deleted",
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
        container_id=dict(type="str"),
        namespace_id=dict(
            type="str",
            required=True,
        ),
        privacy=dict(
            type="str",
            required=True,
            choices=["unknown_privacy", "public", "private"],
        ),
        protocol=dict(
            type="str",
            required=True,
            choices=["unknown_protocol", "http1", "h2c"],
        ),
        http_option=dict(
            type="str",
            required=True,
            choices=["unknown_http_option", "enabled", "redirected"],
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
        environment_variables=dict(
            type="dict",
            required=False,
        ),
        min_scale=dict(
            type="int",
            required=False,
        ),
        max_scale=dict(
            type="int",
            required=False,
        ),
        memory_limit=dict(
            type="int",
            required=False,
        ),
        timeout=dict(
            type="str",
            required=False,
        ),
        description=dict(
            type="str",
            required=False,
        ),
        registry_image=dict(
            type="str",
            required=False,
        ),
        max_concurrency=dict(
            type="int",
            required=False,
        ),
        port=dict(
            type="int",
            required=False,
        ),
        secret_environment_variables=dict(
            type="list",
            required=False,
            elements="str",
            no_log=True,
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=(["container_id", "name"],),
        supports_check_mode=True,
    )

    if not HAS_SCALEWAY_SDK:
        module.fail_json(msg=missing_required_lib("scaleway"))

    core(module)


if __name__ == "__main__":
    main()
