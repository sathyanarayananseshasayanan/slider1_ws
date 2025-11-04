from setuptools import find_packages, setup
import os 
from glob import glob 


package_name = 'rl_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),  # or list specific files
        # (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),     # add if you have configs
        # (os.path.join('share', package_name, 'rviz'),   glob('rviz/*.rviz')),       # add if you have rviz files
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='montezuma',
    maintainer_email='nektariostaf@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'policy = rl_controller.policy:main',
            'target_point = rl_controller.target_point:main',
            'action_bounds = rl_controller.action_bounds:main',
            'lissajous_trajectory = rl_controller.lissajous_trajectory:main',

        ],
    },
)
