import yaml

from charms.reactive import set_flag
from charms.reactive import when_not

from charms import layer
from charms.layer.basic import pod_spec_set


@when_not('charm.kubeflow-ambassador.started')
def start_charm():
    layer.status.maintenance('configuring container')

    pod_spec_set(yaml.dump({
        'containers': [
            {
                'name': 'ambassador',
                'image': 'quay.io/datawire/ambassador:0.30.1',
                'command': [],
                'ports': [
                    {
                        'name': 'ambassador',
                        'containerPort': 8080,
                    },
                ],
                'livenessProbe': {
                    'httpGet': {
                        'path': '/ambassador/v0/check_alive',
                        'port': 8877,
                    },
                    'initialDelaySeconds': 30,
                    'periodSeconds': 30,
                },
                'readinessProbe': {
                    'httpGet': {
                      'path': '/ambassador/v0/check_ready',
                      'port': 8877,
                    },
                    'initialDelaySeconds': 30,
                    'periodSeconds': 30,
                },
            },
        ],
    }))

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-ambassador.started')
