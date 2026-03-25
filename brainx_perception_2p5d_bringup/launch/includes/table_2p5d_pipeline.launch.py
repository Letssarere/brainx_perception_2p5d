from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("config_file"),
            DeclareLaunchArgument("rviz_config"),
            DeclareLaunchArgument("headless", default_value="false"),
            DeclareLaunchArgument("camera_frame", default_value="synthetic_camera"),
            DeclareLaunchArgument("camera_x", default_value="0.6"),
            DeclareLaunchArgument("camera_y", default_value="0.2"),
            DeclareLaunchArgument("camera_z", default_value="1.1"),
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                name="table_to_camera_tf",
                arguments=[
                    "--x",
                    LaunchConfiguration("camera_x"),
                    "--y",
                    LaunchConfiguration("camera_y"),
                    "--z",
                    LaunchConfiguration("camera_z"),
                    "--roll",
                    "3.141592653589793",
                    "--pitch",
                    "0.0",
                    "--yaw",
                    "0.0",
                    "--frame-id",
                    "table_frame",
                    "--child-frame-id",
                    LaunchConfiguration("camera_frame"),
                ],
            ),
            Node(
                package="brainx_perception_2p5d_map",
                executable="map_node",
                name="map_node",
                output="screen",
                parameters=[LaunchConfiguration("config_file")],
            ),
            Node(
                package="brainx_perception_2p5d_slots",
                executable="slots_node",
                name="slots_node",
                output="screen",
                parameters=[LaunchConfiguration("config_file")],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                arguments=["-d", LaunchConfiguration("rviz_config")],
                parameters=[LaunchConfiguration("config_file")],
                condition=UnlessCondition(LaunchConfiguration("headless")),
            ),
        ]
    )
