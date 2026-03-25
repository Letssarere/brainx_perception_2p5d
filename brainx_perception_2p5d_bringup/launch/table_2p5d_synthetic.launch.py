from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    bringup_share = FindPackageShare("brainx_perception_2p5d_bringup")
    config_file = PathJoinSubstitution([bringup_share, "config", "table_2p5d.yaml"])
    rviz_config = PathJoinSubstitution([bringup_share, "rviz", "table_2p5d.rviz"])
    pipeline_launch = PathJoinSubstitution(
        [bringup_share, "launch", "includes", "table_2p5d_pipeline.launch.py"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("headless", default_value="false"),
            DeclareLaunchArgument("scenario", default_value="occupied_static"),
            DeclareLaunchArgument("camera_frame", default_value="synthetic_camera"),
            DeclareLaunchArgument("camera_x", default_value="0.6"),
            DeclareLaunchArgument("camera_y", default_value="0.2"),
            DeclareLaunchArgument("camera_z", default_value="1.1"),
            Node(
                package="brainx_perception_2p5d_bringup",
                executable="synthetic_depth_publisher.py",
                name="synthetic_depth_publisher",
                output="screen",
                parameters=[
                    config_file,
                    {
                        "synthetic.camera_frame": LaunchConfiguration("camera_frame"),
                        "synthetic.camera_x": LaunchConfiguration("camera_x"),
                        "synthetic.camera_y": LaunchConfiguration("camera_y"),
                        "synthetic.camera_z": LaunchConfiguration("camera_z"),
                    },
                    {"synthetic.scenario": LaunchConfiguration("scenario")},
                ],
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(pipeline_launch),
                launch_arguments={
                    "config_file": config_file,
                    "rviz_config": rviz_config,
                    "headless": LaunchConfiguration("headless"),
                    "camera_frame": LaunchConfiguration("camera_frame"),
                    "camera_x": LaunchConfiguration("camera_x"),
                    "camera_y": LaunchConfiguration("camera_y"),
                    "camera_z": LaunchConfiguration("camera_z"),
                }.items(),
            ),
        ]
    )
