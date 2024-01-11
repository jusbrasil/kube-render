from setuptools import setup

__version__ = '0.3.5'

setup(
    name='kuberender',
    version=__version__,
    packages=['kuberender'],
    description='A tool to render and apply Kubernetes manifests using Jinja2',
    install_requires=[
        'Jinja2==3.1.3',
        'click==6.7',
        'PyYAML==5.4',
        'dpath==1.4.0',
        'libvcs==0.11.1',
        'six==1.12.0',
        'zipp==0.6.0',
        'MarkupSafe==1.1.1'
    ],
    entry_points={
        'console_scripts': [
            'kube-render = kuberender:cli_render',
            'kube-render-file = kuberender:cli_file'
        ]
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.3.1', 'mock==3.0.5']
)
