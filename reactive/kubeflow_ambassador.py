import os

from charms.reactive import set_flag
from charms.reactive import when, when_not

from charms import layer


@when_not('layer.docker-resource.ambassador-image.fetched')
def fetch_image():
    layer.docker_resource.fetch('ambassador-image')


@when('layer.docker-resource.ambassador-image.fetched')
@when_not('charm.kubeflow-ambassador.started')
def start_charm():
    layer.status.maintenance('configuring container')

    image_info = layer.docker_resource.get_info('ambassador-image')

    layer.caas_base.pod_spec_set({
        'containers': [
            {
                'name': 'ambassador',
                'imageDetails': {
                    'imagePath': image_info.registry_path,
                    'username': image_info.username,
                    'password': image_info.password,
                },
                'command': [],
                'ports': [
                    {
                        'name': 'ambassador',
                        'containerPort': 8080,
                    },
                ],
                'config': {
                    'AMBASSADOR_NAMESPACE': os.environ['JUJU_MODEL_NAME'],
                    'AMBASSADOR_SINGLE_NAMESPACE': 'true',
                },
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
    })

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-ambassador.started')
