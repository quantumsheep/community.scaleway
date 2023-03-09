#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_instance_image
short_description: Manage Scaleway instance's image
description:
    - This module can be used to manage Scaleway instance's image.
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
    image_id:
        description: image_id
        type: str
        required: false
    root_volume:
        description: root_volume
        type: str
        required: true
    zone:
        description: zone
        type: str
        required: false
    name:
        description: name
        type: str
        required: false
    arch:
        description: arch
        type: str
        required: true
        choices:
            - x86_64
            - arm
    default_bootscript:
        description: default_bootscript
        type: str
        required: false
    extra_volumes:
        description: extra_volumes
        type: dict
        required: false
    organization:
        description: organization
        type: str
        required: false
    project:
        description: project
        type: str
        required: false
    tags:
        description: tags
        type: list
        elements: str
        required: false
    public:
        description: public
        type: bool
        required: false
"""

EXAMPLES = r"""
- name: Create a image
  quantumsheep.scaleway.scaleway_instance_image:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    root_volume: "aaaaaa"
    arch: "aaaaaa"
"""

RETURN = r"""
---
image:
    description: The image information
    returned: when I(state=present)
    type: dict
    sample:
        image:
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
        resource = api.get_image(image_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_image(**not_none_params)

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = InstanceV1APIUtils(client)

    image = module.params.pop("image", None)

    if image is not None:
        resource = api.get_image(image_id=image, region=module.params["region"])
    else:
        module.fail_json(msg="image is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_image(image_id=resource.image, region=module.params["region"])

    module.exit_json(
        changed=True,
        msg=f"instance's image {resource.image} deleted",
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
        image_id=dict(type="str"),
        root_volume=dict(
            type="str",
            required=True,
        ),
        zone=dict(
            type="str",
            required=False,
        ),
        name=dict(
            type="str",
            required=False,
        ),
        arch=dict(
            type="str",
            required=True,
            choices=["x86_64", "arm"],
        ),
        default_bootscript=dict(
            type="str",
            required=False,
        ),
        extra_volumes=dict(
            type="dict",
            required=False,
        ),
        organization=dict(
            type="str",
            required=False,
        ),
        project=dict(
            type="str",
            required=False,
        ),
        tags=dict(
            type="list",
            required=False,
            elements="str",
        ),
        public=dict(
            type="bool",
            required=False,
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=(["image_id", "name"],),
        supports_check_mode=True,
    )

    if not HAS_SCALEWAY_SDK:
        module.fail_json(msg=missing_required_lib("scaleway"))

    core(module)


if __name__ == "__main__":
    main()
