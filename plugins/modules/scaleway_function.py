#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_function
short_description: Manage Scaleway function's function
description:
    - This module can be used to manage Scaleway function's function.
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
    function_id:
        description: function_id
        type: str
        required: false
    namespace_id:
        description: namespace_id
        type: str
        required: true
    runtime:
        description: runtime
        type: str
        required: true
        choices:
            - unknown_runtime
            - golang
            - python
            - python3
            - node8
            - node10
            - node14
            - node16
            - node17
            - python37
            - python38
            - python39
            - python310
            - go113
            - go117
            - go118
            - node18
            - rust165
            - go119
            - python311
            - php82
            - node19
            - go120
    privacy:
        description: privacy
        type: str
        required: true
        choices:
            - unknown_privacy
            - public
            - private
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
    handler:
        description: handler
        type: str
        required: false
    description:
        description: description
        type: str
        required: false
    secret_environment_variables:
        description: secret_environment_variables
        type: list
        elements: str
        required: false
"""

EXAMPLES = r"""
- name: Create a function
  quantumsheep.scaleway.scaleway_function:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    namespace_id: "aaaaaa"
    runtime: "aaaaaa"
    privacy: "aaaaaa"
    http_option: "aaaaaa"
"""

RETURN = r"""
---
function:
    description: The function information
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
        runtime: golang
        memory_limit: 3
        cpu_limit: 3
        timeout: "aaaaaa"
        handler: "aaaaaa"
        error_message: "aaaaaa"
        privacy: public
        description: "aaaaaa"
        domain_name: "aaaaaa"
        secret_environment_variables:
            - aaaaaa
            - bbbbbb
        region: fr-par
        http_option: enabled
        runtime_message: "aaaaaa"
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
    from scaleway.function.v1beta1 import FunctionV1Beta1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = FunctionV1Beta1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_function(function_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_function(**not_none_params)
    resource = api.wait_for_function(
        function_id=resource.id, region=module.params["region"]
    )

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = FunctionV1Beta1API(client)

    id = module.params.pop("id", None)
    name = module.params.pop("name", None)

    if id is not None:
        resource = api.get_function(function_id=id, region=module.params["region"])
    elif name is not None:
        resources = api.list_functions_all(name=name, region=module.params["region"])
        if len(resources) == 0:
            module.exit_json(msg="No function found with name {name}")
        elif len(resources) > 1:
            module.exit_json(msg="More than one function found with name {name}")
        else:
            resource = resources[0]
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_function(function_id=resource.id, region=module.params["region"])

    try:
        api.wait_for_function(function_id=resource.id, region=module.params["region"])
    except ScalewayException as e:
        if e.status_code != 404:
            raise e

    module.exit_json(
        changed=True,
        msg=f"function's function {resource.name} ({resource.id}) deleted",
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
        function_id=dict(type="str"),
        namespace_id=dict(
            type="str",
            required=True,
        ),
        runtime=dict(
            type="str",
            required=True,
            choices=[
                "unknown_runtime",
                "golang",
                "python",
                "python3",
                "node8",
                "node10",
                "node14",
                "node16",
                "node17",
                "python37",
                "python38",
                "python39",
                "python310",
                "go113",
                "go117",
                "go118",
                "node18",
                "rust165",
                "go119",
                "python311",
                "php82",
                "node19",
                "go120",
            ],
        ),
        privacy=dict(
            type="str",
            required=True,
            choices=["unknown_privacy", "public", "private"],
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
        handler=dict(
            type="str",
            required=False,
        ),
        description=dict(
            type="str",
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
        required_one_of=(["function_id", "name"],),
        supports_check_mode=True,
    )

    if not HAS_SCALEWAY_SDK:
        module.fail_json(msg=missing_required_lib("scaleway"))

    core(module)


if __name__ == "__main__":
    main()
