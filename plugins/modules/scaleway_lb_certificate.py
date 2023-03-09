#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_lb_certificate
short_description: Manage Scaleway lb's certificate
description:
    - This module can be used to manage Scaleway lb's certificate.
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
    certificate_id:
        description: certificate_id
        type: str
        required: false
    lb_id:
        description: lb_id
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
    letsencrypt:
        description: letsencrypt
        type: dict
        required: false
    custom_certificate:
        description: custom_certificate
        type: dict
        required: false
"""

EXAMPLES = r"""
- name: Create a certificate
  quantumsheep.scaleway.scaleway_lb_certificate:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    lb_id: "aaaaaa"
"""

RETURN = r"""
---
certificate:
    description: The certificate information
    returned: when I(state=present)
    type: dict
    sample:
        type_: letsencryt
        id: 00000000-0000-0000-0000-000000000000
        common_name: "aaaaaa"
        subject_alternative_name:
            - aaaaaa
            - bbbbbb
        fingerprint: "aaaaaa"
        not_valid_before: 00000000-0000-0000-0000-000000000000
        not_valid_after: 00000000-0000-0000-0000-000000000000
        status: pending
        lb:
            aaaaaa: bbbbbb
            cccccc: dddddd
        name: "aaaaaa"
        created_at: "aaaaaa"
        updated_at: "aaaaaa"
        status_details: "aaaaaa"
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
    from scaleway.lb.v1 import LbV1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = LbV1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_certificate(certificate_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_certificate(**not_none_params)
    resource = api.wait_for_certificate(
        certificate_id=resource.id, region=module.params["region"]
    )

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = LbV1API(client)

    id = module.params.pop("id", None)
    name = module.params.pop("name", None)

    if id is not None:
        resource = api.get_certificate(
            certificate_id=id, region=module.params["region"]
        )
    elif name is not None:
        resources = api.list_certificates_all(name=name, region=module.params["region"])
        if len(resources) == 0:
            module.exit_json(msg="No certificate found with name {name}")
        elif len(resources) > 1:
            module.exit_json(msg="More than one certificate found with name {name}")
        else:
            resource = resources[0]
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_certificate(certificate_id=resource.id, region=module.params["region"])

    try:
        api.wait_for_certificate(
            certificate_id=resource.id, region=module.params["region"]
        )
    except ScalewayException as e:
        if e.status_code != 404:
            raise e

    module.exit_json(
        changed=True,
        msg=f"lb's certificate {resource.name} ({resource.id}) deleted",
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
        certificate_id=dict(type="str"),
        lb_id=dict(
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
        letsencrypt=dict(
            type="dict",
            required=False,
        ),
        custom_certificate=dict(
            type="dict",
            required=False,
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=(["certificate_id", "name"],),
        supports_check_mode=True,
    )

    if not HAS_SCALEWAY_SDK:
        module.fail_json(msg=missing_required_lib("scaleway"))

    core(module)


if __name__ == "__main__":
    main()
