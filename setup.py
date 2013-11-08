import setuptools

setuptools.setup(name='nice_iptables',
                 version='0.1.1',
                 author='skashaba',
                 scripts=['bin/nice_iptables'],
                 install_requires=["nose", "flake8", "coverage"],
                 packages=setuptools.find_packages(exclude=['bin']))

