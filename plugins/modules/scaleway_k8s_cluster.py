#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Scaleway
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: scaleway_k8s_cluster
short_description: Manage Scaleway k8s's cluster
description:
    - This module can be used to manage Scaleway k8s's cluster.
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
    type_:
        description: type_
        type: str
        required: true
    description:
        description: description
        type: str
        required: true
    version:
        description: version
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
    organization_id:
        description: organization_id
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
    cni:
        description: cni
        type: str
        required: true
        choices:
            - unknown_cni
            - cilium
            - calico
            - weave
            - flannel
            - kilo
    enable_dashboard:
        description: enable_dashboard
        type: bool
        required: false
    ingress:
        description: ingress
        type: str
        required: false
        choices:
            - unknown_ingress
            - none
            - nginx
            - traefik
            - traefik2
    pools:
        description: pools
        type: list
        elements: str
        required: false
    autoscaler_config:
        description: autoscaler_config
        type: dict
        required: false
    auto_upgrade:
        description: auto_upgrade
        type: dict
        required: false
    feature_gates:
        description: feature_gates
        type: list
        elements: str
        required: false
    admission_plugins:
        description: admission_plugins
        type: list
        elements: str
        required: false
    open_id_connect_config:
        description: open_id_connect_config
        type: dict
        required: false
    apiserver_cert_sans:
        description: apiserver_cert_sans
        type: list
        elements: str
        required: false
"""

EXAMPLES = r"""
- name: Create a cluster
  quantumsheep.scaleway.scaleway_k8s_cluster:
    access_key: "{{ scw_access_key }}"
    secret_key: "{{ scw_secret_key }}"
    type_: "aaaaaa"
    description: "aaaaaa"
    version: "aaaaaa"
    cni: "aaaaaa"
"""

RETURN = r"""
---
cluster:
    description: The cluster information
    returned: when I(state=present)
    type: dict
    sample:
        id: 00000000-0000-0000-0000-000000000000
        type_: "aaaaaa"
        name: "aaaaaa"
        status: creating
        version: "aaaaaa"
        region: fr-par
        organization_id: 00000000-0000-0000-0000-000000000000
        project_id: 00000000-0000-0000-0000-000000000000
        tags:
            - aaaaaa
            - bbbbbb
        cni: cilium
        description: "aaaaaa"
        cluster_url: "aaaaaa"
        dns_wildcard: "aaaaaa"
        created_at: "aaaaaa"
        updated_at: "aaaaaa"
        autoscaler_config:
            aaaaaa: bbbbbb
            cccccc: dddddd
        dashboard_enabled: true
        ingress: none
        auto_upgrade:
            aaaaaa: bbbbbb
            cccccc: dddddd
        upgrade_available: true
        feature_gates:
            - aaaaaa
            - bbbbbb
        admission_plugins:
            - aaaaaa
            - bbbbbb
        open_id_connect_config: 00000000-0000-0000-0000-000000000000
        apiserver_cert_sans:
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
    from scaleway.k8s.v1 import K8SV1API

    HAS_SCALEWAY_SDK = True
except ImportError:
    HAS_SCALEWAY_SDK = False


def create(module: AnsibleModule, client: "Client") -> None:
    api = K8SV1API(client)

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
    api = K8SV1API(client)

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
        msg=f"k8s's cluster {resource.name} ({resource.id}) deleted",
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
        type_=dict(
            type="str",
            required=True,
        ),
        description=dict(
            type="str",
            required=True,
        ),
        version=dict(
            type="str",
            required=True,
        ),
        region=dict(
            type="str",
            required=False,
            choices=["fr-par", "nl-ams", "pl-waw"],
        ),
        organization_id=dict(
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
        cni=dict(
            type="str",
            required=True,
            choices=["unknown_cni", "cilium", "calico", "weave", "flannel", "kilo"],
        ),
        enable_dashboard=dict(
            type="bool",
            required=False,
        ),
        ingress=dict(
            type="str",
            required=False,
            choices=["unknown_ingress", "none", "nginx", "traefik", "traefik2"],
        ),
        pools=dict(
            type="list",
            required=False,
            elements="str",
        ),
        autoscaler_config=dict(
            type="dict",
            required=False,
        ),
        auto_upgrade=dict(
            type="dict",
            required=False,
        ),
        feature_gates=dict(
            type="list",
            required=False,
            elements="str",
        ),
        admission_plugins=dict(
            type="list",
            required=False,
            elements="str",
        ),
        open_id_connect_config=dict(
            type="dict",
            required=False,
        ),
        apiserver_cert_sans=dict(
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
