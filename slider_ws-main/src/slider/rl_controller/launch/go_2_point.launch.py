from launch import LaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
import os
from datetime import datetime


high_level_path = os.path.join(os.getcwd(), 'rosbags')
os.makedirs(high_level_path, exist_ok=True)  

bag_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
bag_path = os.path.join(high_level_path, bag_name)

def generate_launch_description():
    return LaunchDescription([
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [FindPackageShare('slider_gazebo'), '/launch/slider_launch.py']
            ),
        ),
        
        DeclareLaunchArgument('policy_file_path',description='policy_file_path'),
        DeclareLaunchArgument('lissa_A', default_value='2.0', description='Amplitude A (float)'),
        DeclareLaunchArgument('lissa_B', default_value='2.0', description='Amplitude B (float)'),
        DeclareLaunchArgument('lissa_a', default_value='1',   description='Frequency a (int)'),
        DeclareLaunchArgument('lissa_b', default_value='2',   description='Frequency b (int)'),
        DeclareLaunchArgument('lissa_delta', default_value='1.0', description='Phase delta (float)'),
        DeclareLaunchArgument('lissa_omega', default_value='0.05', description='Angular frequency (float)'),
        DeclareLaunchArgument('record_bag', default_value='false', description='Set true to record rosbag'),
        DeclareLaunchArgument('bag_name', default_value='test', description='Output bag name'),
        DeclareLaunchArgument('launch_plotjuggler', default_value='false', description='Set true to record rosbag'),

        ExecuteProcess(
            condition=IfCondition(LaunchConfiguration('record_bag')),
            cmd=[
                'ros2', 'bag', 'record',
                '--storage', 'sqlite3',
                '-o', bag_path,
                '/odom',
                '/target_point',
                '/action_bounds',
                '/thrust_cmd',
            ],
            output='screen',
        ),
        
        ExecuteProcess(
            condition=IfCondition(LaunchConfiguration('launch_plotjuggler')),
            cmd=[
                'ros2', 'run', 'plotjuggler', 'plotjuggler',
                '-l', 'configs/plot_juggler_config_rl_target_tracking.xml'
                ],
            output='screen',
        ),

        Node(
            package='slider_thruster_controller',
            executable='pwm_publisher',
            name='pwm_publisher'
        ),
        
        Node(
            package='rl_controller',
            executable='policy',
            name='policy',
            arguments=[LaunchConfiguration('policy_file_path'), 
                    '--ros-args', 
                    '--log-level', 
                    'policy:=DEBUG'],
        ),
        
        Node(
            package='rl_controller',
            executable='action_bounds',
            name='action_bounds',
        ),

        ## Use for going just to a point 
        # Node(
        #     package='rl_controller',  
        #     executable='target_point',
        #     name='target_point',
        #     arguments=[
        #         LaunchConfiguration('target_x'),
        #         LaunchConfiguration('target_y')],
        #     parameters=[{
        #         # 'target_x': 1.7,
        #         # 'target_y': 1.8,
        #         # 'target_z': 0.0,
        #         'frame_id': 'odom',
        #         'publish_rate': 10.0,
        #     }],
        # )
            
            
        Node(
            package='rl_controller',  
            executable='lissajous_trajectory',
            name='lissajous_trajectory',
            arguments=[
                LaunchConfiguration('lissa_A'),
                LaunchConfiguration('lissa_B'),
                LaunchConfiguration('lissa_a'),
                LaunchConfiguration('lissa_b'),
                LaunchConfiguration('lissa_delta'),
                LaunchConfiguration('lissa_omega')
                ],
            parameters=[{
                # 'target_x': 1.7,
                # 'target_y': 1.8,
                # 'target_z': 0.0,
                'frame_id': 'odom',
                'publish_rate': 10.0,
            }],
        ),
        
    ])
