from setuptools import setup

setup(
    name='svcstats.py',
    version='1.0.1.2',
    py_modules=['svcstats'],
    install_requires=['pywbem'],
    url='https://github.com/mezantrop/svcstats.py',
    license='',
    author='Mikhail Zakharov',
    author_email='zmey20000@yahoo.com',
    description='Report IBM SVC/Storwize storage system performance statistics for nodes, vdisks, mdisks or drives in CLI'
)
