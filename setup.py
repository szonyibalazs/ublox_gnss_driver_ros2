import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'ublox_gnss_driver'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='szonyibalazs',
    maintainer_email='szonyibali@gmail.com',
    description='u-blox GNSS receiver driver for ROS2 that reads position data via USB serial',
    license='MIT',
    entry_points={
        'console_scripts': [
            'gnss_node = ublox_gnss_driver.gnss_node:main',
        ],
    },
)
