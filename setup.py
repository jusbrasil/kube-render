from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='kube-render',
    version='0.1',
    py_modules=['kuberender'],
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        kube-render=kuberender:run
    ''',
)
