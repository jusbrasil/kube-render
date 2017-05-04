from setuptools import setup

__version__ = '0.2.0'

setup(
    name='kuberender',
    version=__version__,
    py_modules=['kuberender'],
    install_requires=[
      'Jinja2==2.9.6',
      'click==6.7',
      'PyYAML==3.12',
      'dpath==1.4.0',
      'libvcs==0.2.3',
    ],
    entry_points='''
        [console_scripts]
        kube-render=kuberender:run
    ''',
)
