from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def _create_rosbag_play(context, *_args, **_kwargs):
    topics = [
        LaunchConfiguration("depth_topic").perform(context),
        LaunchConfiguration("camera_info_topic").perform(context),
        LaunchConfiguration("color_topic").perform(context),
        LaunchConfiguration("color_camera_info_topic").perform(context),
    ]
    if LaunchConfiguration("replay_tf_static").perform(context).lower() == "true":
        topics.append("/tf_static")

    command = [
        "ros2",
        "bag",
        "play",
        LaunchConfiguration("bag_path").perform(context),
        "--rate",
        LaunchConfiguration("rate").perform(context),
        "--delay",
        "1.0",
        "--disable-keyboard-controls",
        "--topics",
        *topics,
    ]
    if LaunchConfiguration("loop").perform(context).lower() == "true":
        command.append("-l")

    return [ExecuteProcess(cmd=command, output="screen")]


def generate_launch_description():
    bringup_share = FindPackageShare("brainx_perception_2p5d_bringup")
    config_file = PathJoinSubstitution([bringup_share, "config", "table_2p5d.yaml"])
    rviz_config = PathJoinSubstitution([bringup_share, "rviz", "table_2p5d.rviz"])
    pipeline_launch = PathJoinSubstitution(
        [bringup_share, "launch", "includes", "table_2p5d_pipeline.launch.py"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("bag_path"),
            DeclareLaunchArgument("headless", default_value="false"),
            DeclareLaunchArgument("rate", default_value="1.0"),
            DeclareLaunchArgument("loop", default_value="false"),
            DeclareLaunchArgument("replay_tf_static", default_value="false"),
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
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(pipeline_launch),
                launch_arguments={
                    "config_file": config_file,
                    "rviz_config": rviz_config,
                    "headless": LaunchConfiguration("headless"),
                    "depth_topic": LaunchConfiguration("depth_topic"),
                    "camera_info_topic": LaunchConfiguration("camera_info_topic"),
                    "color_topic": LaunchConfiguration("color_topic"),
                    "color_camera_info_topic": LaunchConfiguration("color_camera_info_topic"),
                    "publish_table_tf": LaunchConfiguration("publish_table_tf"),
                    "camera_frame": LaunchConfiguration("camera_frame"),
                    "camera_x": LaunchConfiguration("camera_x"),
                    "camera_y": LaunchConfiguration("camera_y"),
                    "camera_z": LaunchConfiguration("camera_z"),
                    "camera_roll": LaunchConfiguration("camera_roll"),
                    "camera_pitch": LaunchConfiguration("camera_pitch"),
                    "camera_yaw": LaunchConfiguration("camera_yaw"),
                }.items(),
            ),
            OpaqueFunction(function=_create_rosbag_play),
        ]
    )
