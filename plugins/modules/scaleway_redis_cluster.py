#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_redis_cluster
short_description: Manage Scaleway redis's cluster
description:
    - This module can be used to manage Scaleway redis's cluster.
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
    cluster_id:
        description: cluster_id
        type: str
        required: false
    version:
        description: version
        type: str
        required: true
    node_type:
        description: node_type
        type: str
        required: true
    user_name:
        description: user_name
        type: str
        required: true
    password:
        description: password
        type: str
        required: true
    tls_enabled:
        description: tls_enabled
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
    name:
        description: name
        type: str
        required: false
    tags:
        description: tags
        type: list
        elements: str
        required: false
    cluster_size:
        description: cluster_size
        type: int
        required: false
    acl_rules:
        description: acl_rules
        type: list
        elements: str
        required: false
    endpoints:
        description: endpoints
        type: list
        elements: str
        required: false
    cluster_settings:
        description: cluster_settings
        type: list
        elements: str
        required: false
"""

EXAMPLES = r"""
- name: Create a cluster
  quantumsheep.scaleway.scaleway_redis_cluster:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    version: "aaaaaa"
    node_type: "aaaaaa"
    user_name: "aaaaaa"
    password: "aaaaaa"
    tls_enabled: true
"""

RETURN = r"""
---
cluster:
    description: The cluster information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        name: "aaaaaa"
        project_id: 00000000-0000-0000-0000-000000000000
        status: ready
        version: "aaaaaa"
        endpoints:
            - aaaaaa
            - bbbbbb
        tags:
            - aaaaaa
            - bbbbbb
        node_type: "aaaaaa"
        created_at: "aaaaaa"
        updated_at: "aaaaaa"
        tls_enabled: true
        cluster_settings:
            - aaaaaa
            - bbbbbb
        acl_rules:
            - aaaaaa
            - bbbbbb
        cluster_size: 3
        zone: "aaaaaa"
        user_name: "aaaaaa"
        upgradable_versions:
            - aaaaaa
            - bbbbbb
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
    from scaleway.redis.v1 import RedisV1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = RedisV1API(client)

    id = module.params.pop("id", None)
    if id is not None:
        resource = api.get_cluster(cluster_id=id)

        if module.check_mode:
            module.exit_json(changed=False)

        module.exit_json(changed=False, data=resource)

    if module.check_mode:
        module.exit_json(changed=True)

    not_none_params = {
        key: value for key, value in module.params.items() if value is not None
    }
    resource = api.create_cluster(**not_none_params)
    resource = api.wait_for_cluster(
        cluster_id=resource.id, region=module.params["region"]
    )

    module.exit_json(changed=True, data=resource.__dict__)


def delete(module: AnsibleModule, client: "Client") -> None:
    api = RedisV1API(client)

    id = module.params.pop("id", None)
    name = module.params.pop("name", None)

    if id is not None:
        resource = api.get_cluster(cluster_id=id, region=module.params["region"])
    elif name is not None:
        resources = api.list_clusters_all(name=name, region=module.params["region"])
        if len(resources) == 0:
            module.exit_json(msg="No cluster found with name {name}")
        elif len(resources) > 1:
            module.exit_json(msg="More than one cluster found with name {name}")
        else:
            resource = resources[0]
    else:
        module.fail_json(msg="id is required")

    if module.check_mode:
        module.exit_json(changed=True)

    api.delete_cluster(cluster_id=resource.id, region=module.params["region"])

    try:
        api.wait_for_cluster(cluster_id=resource.id, region=module.params["region"])
    except ScalewayException as e:
        if e.status_code != 404:
            raise e

    module.exit_json(
        changed=True,
        msg=f"redis's cluster {resource.name} ({resource.id}) deleted",
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
        cluster_id=dict(type="str"),
        version=dict(
            type="str",
            required=True,
        ),
        node_type=dict(
            type="str",
            required=True,
        ),
        user_name=dict(
            type="str",
            required=True,
        ),
        password=dict(
            type="str",
            required=True,
            no_log=True,
        ),
        tls_enabled=dict(
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
        name=dict(
            type="str",
            required=False,
        ),
        tags=dict(
            type="list",
            required=False,
            elements="str",
        ),
        cluster_size=dict(
            type="int",
            required=False,
        ),
        acl_rules=dict(
            type="list",
            required=False,
            elements="str",
        ),
        endpoints=dict(
            type="list",
            required=False,
            elements="str",
        ),
        cluster_settings=dict(
            type="list",
            required=False,
            elements="str",
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=(["cluster_id", "name"],),
        supports_check_mode=True,
    )

    if not HAS_SCALEWAY_SDK:
        module.fail_json(msg=missing_required_lib("scaleway"))

    core(module)


if __name__ == "__main__":
    main()
