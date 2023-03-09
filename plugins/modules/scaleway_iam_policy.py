#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_iam_policy
short_description: Manage Scaleway iam's policy
description:
    - This module can be used to manage Scaleway iam's policy.
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
    policy_id:
        description: policy_id
        type: str
        required: false
    description:
        description: description
        type: str
        required: true
    name:
        description: name
        type: str
        required: false
    organization_id:
        description: organization_id
        type: str
        required: false
    rules:
        description: rules
        type: list
        elements: str
        required: false
    user_id:
        description: user_id
        type: str
        required: false
    group_id:
        description: group_id
        type: str
        required: false
    application_id:
        description: application_id
        type: str
        required: false
    no_principal:
        description: no_principal
        type: bool
        required: false
"""

EXAMPLES = r"""
- name: Create a policy
  quantumsheep.scaleway.scaleway_iam_policy:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    description: "aaaaaa"
"""

RETURN = r"""
---
policy:
    description: The policy information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        name: "aaaaaa"
        description: "aaaaaa"
        organization_id: 00000000-0000-0000-0000-000000000000
        created_at: "aaaaaa"
        updated_at: "aaaaaa"
        editable: true
        nb_rules: 3
        nb_scopes: 3
        nb_permission_sets: 3
        user_id: 00000000-0000-0000-0000-000000000000
        group_id: 00000000-0000-0000-0000-000000000000
        application_id: 00000000-0000-0000-0000-000000000000
        no_principal: true
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
    from scaleway.iam.v1alpha1 import IamV1Alpha1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = IamV1Alpha1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_policy(policy_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_policy(**not_none_params)

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = IamV1Alpha1API(client)

    id = module.params.pop("id", None)
    name = module.params.pop("name", None)

    if id is not None:
        resource = api.get_policy(policy_id=id, region=module.params["region"])
    elif name is not None:
        resources = api.list_policys_all(name=name, region=module.params["region"])
        if len(resources) == 0:
            module.exit_json(msg="No policy found with name {name}")
        elif len(resources) > 1:
            module.exit_json(msg="More than one policy found with name {name}")
        else:
            resource = resources[0]
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_policy(policy_id=resource.id, region=module.params["region"])

    module.exit_json(
        changed=True,
        msg=f"iam's policy {resource.name} ({resource.id}) deleted",
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
        policy_id=dict(type="str"),
        description=dict(
            type="str",
            required=True,
        ),
        name=dict(
            type="str",
            required=False,
        ),
        organization_id=dict(
            type="str",
            required=False,
        ),
        rules=dict(
            type="list",
            required=False,
            elements="str",
        ),
        user_id=dict(
            type="str",
            required=False,
        ),
        group_id=dict(
            type="str",
            required=False,
        ),
        application_id=dict(
            type="str",
            required=False,
        ),
        no_principal=dict(
            type="bool",
            required=False,
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=(["policy_id", "name"],),
        supports_check_mode=True,
    )

    if not HAS_SCALEWAY_SDK:
        module.fail_json(msg=missing_required_lib("scaleway"))

    core(module)


if __name__ == "__main__":
    main()
