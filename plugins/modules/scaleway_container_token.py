from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_container_token
short_description: Manage Scaleway container's token
description:
    - This module can be used to manage Scaleway container's token.
version_added: "2.1.0"
author:
    - Nathanael Demacon (@quantumsheep)
extends_documentation_fragment:
    - quantumsheep.scaleway.scaleway
    - quantumsheep.scaleway.scaleway_waitable_resource
requirements:
    - scaleway >= 0.6.0
options:
    state:
        description:
            - Indicate desired state of the target.
            - C(present) will create the resource.
            - C(absent) will delete the resource, if it exists.
        default: present
        choices: ["present", "absent", "]
        type: str
    id:
        type: str
        required: false
    region:
        type: str
        required: false
        choices:
            - fr-par
            - nl-ams
            - pl-waw
    container_id:
        type: str
        required: false
    namespace_id:
        type: str
        required: false
    description:
        type: str
        required: false
    expires_at:
        type: str
        required: false
"""

RETURN = r"""
---
token:
    description: The token information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        token: "aaaaaa"
        container_id: 00000000-0000-0000-0000-000000000000
        namespace_id: 00000000-0000-0000-0000-000000000000
        public_key: "aaaaaa"
        status: ready
        description: "aaaaaa"
        expires_at: "aaaaaa"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.quantumsheep.scaleway.plugins.module_utils.scaleway import (
    scaleway_argument_spec,
    scaleway_waitable_resource_argument_spec,
    scaleway_get_client_from_module,
    scaleway_pop_client_params,
    scaleway_pop_waitable_resource_params,
)

from scaleway import Client, ScalewayException
from scaleway.container.v1beta1 import ContainerV1Beta1API


def create(module: AnsibleModule, client: Client) -> None:
    api = ContainerV1Beta1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_token(token_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    resource = api.create_token(**module.params)
    resource = api.wait_for_token(token_id=resource.id)

    module.exit_json(changed=True, data=resource)


def delete(module: AnsibleModule, client: Client) -> None:
    api = ContainerV1Beta1API(client)

    id = module.params["id"]

    if id is not None:
        resource = api.get_token(token_id=id)
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_token(token_id=resource.id)

    try:
        api.wait_for_token(token_id=resource.id)
    except ScalewayException as e:
        if e.status_code != 404:
            raise e

    module.exit_json(
        changed=True,
        msg=f"container's token {resource.id} deleted",
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
        id=dict(type="str"),
        region=dict(type="str", required=False, choices=["fr-par", "nl-ams", "pl-waw"]),
        container_id=dict(type="str", required=False),
        namespace_id=dict(type="str", required=False),
        description=dict(type="str", required=False),
        expires_at=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == "__main__":
    main()