from setuptools import setup

__version__ = '0.3.4'

setup(
    name='kuberender',
    version=__version__,
    packages=['kuberender'],
    description='A tool to render and apply Kubernetes manifests using Jinja2',
    install_requires=[
        'Jinja2==2.9.6',
        'click==6.7',
        'PyYAML==3.13',
        'dpath==1.4.0',
        'libvcs==0.3.0',
        'six==1.12.0',
    ],
    entry_points={
        'console_scripts': [
            'kube-render = kuberender:cli_render',
            'kube-render-file = kuberender:cli_file'
        ]
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'mock']
)
