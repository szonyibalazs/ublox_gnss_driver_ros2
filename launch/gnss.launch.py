from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ublox_gnss_driver',
            executable='gnss_node',
            name='gnss_node',
            parameters=[
                {'port': '/dev/ttyACM0'},
                {'baudrate': 9600},
            ],
            output='screen',
        ),
    ])
