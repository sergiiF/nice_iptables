import setuptools

setuptools.setup(name='nice_iptables',
                 version='0.1',
                 author='skashaba',
                 scripts=['bin/nice_iptables'],
                 packages=setuptools.find_packages(exclude=['bin']))

