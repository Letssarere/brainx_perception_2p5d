from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    bringup_share = FindPackageShare("brainx_perception_2p5d_bringup")
    config_file = PathJoinSubstitution([bringup_share, "config", "table_2p5d.yaml"])
    rviz_config = PathJoinSubstitution([bringup_share, "rviz", "table_2p5d.rviz"])

    headless = LaunchConfiguration("headless")

    return LaunchDescription(
        [
            DeclareLaunchArgument("headless", default_value="false"),
            Node(
                package="brainx_perception_2p5d_bringup",
                executable="synthetic_depth_publisher.py",
                name="synthetic_depth_publisher",
                output="screen",
                parameters=[config_file],
            ),
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                name="table_to_camera_tf",
                arguments=[
                    "0.6",
                    "0.2",
                    "1.1",
                    "0.0",
                    "0.0",
                    "3.141592653589793",
                    "table_frame",
                    "synthetic_camera",
                ],
            ),
            Node(
                package="brainx_perception_2p5d_map",
                executable="map_node",
                name="map_node",
                output="screen",
                parameters=[config_file],
            ),
            Node(
                package="brainx_perception_2p5d_slots",
                executable="slots_node",
                name="slots_node",
                output="screen",
                parameters=[config_file],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                arguments=["-d", rviz_config],
                parameters=[config_file],
                condition=UnlessCondition(headless),
            ),
        ]
    )
