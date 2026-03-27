from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("config_file"),
            DeclareLaunchArgument("rviz_config"),
            DeclareLaunchArgument("headless", default_value="false"),
            DeclareLaunchArgument("depth_topic", default_value="/pickup_2p5d/input/depth"),
            DeclareLaunchArgument("camera_info_topic", default_value="/pickup_2p5d/input/camera_info"),
            DeclareLaunchArgument("color_topic", default_value="/pickup_2p5d/input/color"),
            DeclareLaunchArgument(
                "color_camera_info_topic",
                default_value="/pickup_2p5d/input/color_camera_info",
            ),
            DeclareLaunchArgument("publish_table_tf", default_value="true"),
            DeclareLaunchArgument("camera_frame", default_value="synthetic_camera"),
            DeclareLaunchArgument("camera_x", default_value="0.6"),
            DeclareLaunchArgument("camera_y", default_value="0.2"),
            DeclareLaunchArgument("camera_z", default_value="1.1"),
            DeclareLaunchArgument("camera_roll", default_value="3.141592653589793"),
            DeclareLaunchArgument("camera_pitch", default_value="0.0"),
            DeclareLaunchArgument("camera_yaw", default_value="0.0"),
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
                    LaunchConfiguration("camera_roll"),
                    "--pitch",
                    LaunchConfiguration("camera_pitch"),
                    "--yaw",
                    LaunchConfiguration("camera_yaw"),
                    "--frame-id",
                    "table_frame",
                    "--child-frame-id",
                    LaunchConfiguration("camera_frame"),
                ],
                condition=IfCondition(LaunchConfiguration("publish_table_tf")),
            ),
            Node(
                package="brainx_perception_2p5d_map",
                executable="map_node",
                name="map_node",
                output="screen",
                parameters=[LaunchConfiguration("config_file")],
                remappings=[
                    ("/pickup_2p5d/input/depth", LaunchConfiguration("depth_topic")),
                    ("/pickup_2p5d/input/camera_info", LaunchConfiguration("camera_info_topic")),
                    ("/pickup_2p5d/input/color", LaunchConfiguration("color_topic")),
                    (
                        "/pickup_2p5d/input/color_camera_info",
                        LaunchConfiguration("color_camera_info_topic"),
                    ),
                ],
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
