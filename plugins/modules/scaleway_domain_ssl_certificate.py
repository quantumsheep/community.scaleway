#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_domain_ssl_certificate
short_description: Manage Scaleway domain's ssl_certificate
description:
    - This module can be used to manage Scaleway domain's ssl_certificate.
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
    dns_zone:
        description: dns_zone
        type: str
        required: true
    alternative_dns_zones:
        description: alternative_dns_zones
        type: list
        elements: str
        required: false
"""

EXAMPLES = r"""
- name: Create a ssl_certificate
  quantumsheep.scaleway.scaleway_domain_ssl_certificate:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    dns_zone: "aaaaaa"
"""

RETURN = r"""
---
ssl_certificate:
    description: The ssl_certificate information
    returned: when I(state=present)
    type: dict
    sample:
        dns_zone: "aaaaaa"
        alternative_dns_zones:
            - aaaaaa
            - bbbbbb
        status: new
        private_key: "aaaaaa"
        certificate_chain: "aaaaaa"
        created_at: "aaaaaa"
        expired_at: "aaaaaa"
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
    from scaleway.domain.v2beta1 import DomainV2Beta1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = DomainV2Beta1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_ssl_certificate(dns_zone=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_ssl_certificate(**not_none_params)
    resource = api.wait_for_ssl_certificate(
        dns_zone=resource.dns_zone, region=module.params["region"]
    )

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = DomainV2Beta1API(client)

    dns_zone = module.params.pop("dns_zone", None)

    if dns_zone is not None:
        resource = api.get_ssl_certificate(
            dns_zone=dns_zone, region=module.params["region"]
        )
    else:
        module.fail_json(msg="dns_zone is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_ssl_certificate(
        dns_zone=resource.dns_zone, region=module.params["region"]
    )

    try:
        api.wait_for_ssl_certificate(
            dns_zone=resource.dns_zone, region=module.params["region"]
        )
    except ScalewayException as e:
        if e.status_code != 404:
            raise e

    module.exit_json(
        changed=True,
        msg=f"domain's ssl_certificate {resource.dns_zone} deleted",
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
        dns_zone=dict(
            type="str",
            required=True,
        ),
        alternative_dns_zones=dict(
            type="list",
            required=False,
            elements="str",
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
