from __future__ import annotations

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image

from brainx_perception_2p5d_bringup.synthetic_scene import (
    CAMERA_INFO_TOPIC,
    DEPTH_TOPIC,
    SyntheticSceneConfig,
    SyntheticSceneRenderer,
)


class SyntheticDepthPublisher(Node):
    def __init__(self) -> None:
        super().__init__("synthetic_depth_publisher")
        self.config = SyntheticSceneConfig.from_node(self)
        self.scenario = str(
            self.declare_parameter("synthetic.scenario", "occupied_static").value
        )
        if self.scenario not in SyntheticSceneRenderer.available_scenarios():
            raise ValueError(f"unsupported synthetic scenario: {self.scenario}")

        self.renderer = SyntheticSceneRenderer(self.config)
        self.frame_index = 0
        self.depth_pub = self.create_publisher(Image, DEPTH_TOPIC, 10)
        self.camera_info_pub = self.create_publisher(CameraInfo, CAMERA_INFO_TOPIC, 10)
        self.timer = self.create_timer(1.0 / self.config.publish_rate_hz, self.publish_frame)

        self.get_logger().info(
            f"synthetic scenario={self.scenario} frames={self.renderer.scenario_frame_count(self.scenario)}"
        )

    def publish_frame(self) -> None:
        stamp = self.get_clock().now().to_msg()
        depths = self.renderer.render_depth_frame(self.scenario, self.frame_index)
        self.depth_pub.publish(self.renderer.make_depth_message(stamp, depths))
        self.camera_info_pub.publish(self.renderer.make_camera_info_message(stamp))
        self.frame_index = (self.frame_index + 1) % self.renderer.scenario_frame_count(
            self.scenario
        )


def main() -> None:
    rclpy.init()
    node = SyntheticDepthPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
