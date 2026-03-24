#!/usr/bin/env python3

import array
from dataclasses import dataclass
from typing import Iterable, Optional

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image


@dataclass
class Box:
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float


class SyntheticDepthPublisher(Node):
    def __init__(self) -> None:
        super().__init__("synthetic_depth_publisher")

        self.table_frame = self.declare_parameter("geometry.table_frame", "table_frame").value
        self.origin_x = float(self.declare_parameter("geometry.origin_x", 0.0).value)
        self.origin_y = float(self.declare_parameter("geometry.origin_y", 0.0).value)
        self.table_width = float(self.declare_parameter("geometry.width", 1.2).value)
        self.table_depth = float(self.declare_parameter("geometry.depth", 0.4).value)
        self.columns = int(self.declare_parameter("geometry.columns", 12).value)
        self.rows = int(self.declare_parameter("geometry.rows", 2).value)

        self.width = int(self.declare_parameter("synthetic.width", 160).value)
        self.height = int(self.declare_parameter("synthetic.height", 120).value)
        self.fx = float(self.declare_parameter("synthetic.fx", 180.0).value)
        self.fy = float(self.declare_parameter("synthetic.fy", 180.0).value)
        self.cx = float(self.declare_parameter("synthetic.cx", self.width / 2.0).value)
        self.cy = float(self.declare_parameter("synthetic.cy", self.height / 2.0).value)
        self.camera_frame = self.declare_parameter("synthetic.camera_frame", "synthetic_camera").value
        self.camera_x = float(self.declare_parameter("synthetic.camera_x", 0.6).value)
        self.camera_y = float(self.declare_parameter("synthetic.camera_y", 0.2).value)
        self.camera_z = float(self.declare_parameter("synthetic.camera_z", 1.1).value)
        self.publish_rate_hz = float(self.declare_parameter("synthetic.publish_rate_hz", 5.0).value)
        self.object_height_m = float(self.declare_parameter("synthetic.object_height_m", 0.14).value)
        self.object_width_scale = float(self.declare_parameter("synthetic.object_width_scale", 0.58).value)
        self.object_depth_scale = float(self.declare_parameter("synthetic.object_depth_scale", 0.50).value)
        self.occupied_slots = list(
            self.declare_parameter("synthetic.occupied_slots", [2, 5, 16]).value
        )

        self.depth_pub = self.create_publisher(Image, "/pickup_2p5d/input/depth", 10)
        self.camera_info_pub = self.create_publisher(CameraInfo, "/pickup_2p5d/input/camera_info", 10)

        self.slot_width = self.table_width / self.columns
        self.slot_depth = self.table_depth / self.rows
        self.objects = self._build_boxes(self.occupied_slots)
        self.timer = self.create_timer(1.0 / self.publish_rate_hz, self.publish_frame)

    def _build_boxes(self, slot_ids: Iterable[int]) -> list[Box]:
        boxes: list[Box] = []
        object_half_width = self.slot_width * self.object_width_scale * 0.5
        object_half_depth = self.slot_depth * self.object_depth_scale * 0.5

        for slot_id in slot_ids:
            row = slot_id // self.columns
            column = slot_id % self.columns
            center_x = self.origin_x + (column + 0.5) * self.slot_width
            center_y = self.origin_y + (row + 0.5) * self.slot_depth
            boxes.append(
                Box(
                    min_x=center_x - object_half_width,
                    max_x=center_x + object_half_width,
                    min_y=center_y - object_half_depth,
                    max_y=center_y + object_half_depth,
                    min_z=0.0,
                    max_z=self.object_height_m,
                )
            )
        return boxes

    def _intersect_box(self, ray_origin: tuple[float, float, float], ray_dir: tuple[float, float, float], box: Box) -> Optional[float]:
        tmin = -float("inf")
        tmax = float("inf")
        bounds = (
            (box.min_x, box.max_x),
            (box.min_y, box.max_y),
            (box.min_z, box.max_z),
        )

        for axis, (lower, upper) in enumerate(bounds):
            origin = ray_origin[axis]
            direction = ray_dir[axis]
            if abs(direction) < 1e-6:
                if origin < lower or origin > upper:
                    return None
                continue
            inv = 1.0 / direction
            t1 = (lower - origin) * inv
            t2 = (upper - origin) * inv
            if t1 > t2:
                t1, t2 = t2, t1
            tmin = max(tmin, t1)
            tmax = min(tmax, t2)
            if tmin > tmax:
                return None

        if tmax < 0.0:
            return None
        return tmin if tmin > 0.0 else tmax

    def _ray_table(self, u: int, v: int) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        # Camera is mounted above the table with a 180 degree roll: x -> x, y -> -y, z -> -z.
        camera_ray = (
            (float(u) - self.cx) / self.fx,
            (float(v) - self.cy) / self.fy,
            1.0,
        )
        table_ray = (camera_ray[0], -camera_ray[1], -camera_ray[2])
        table_origin = (self.camera_x, self.camera_y, self.camera_z)
        return table_origin, table_ray

    def _render_depth(self) -> list[float]:
        depths = [0.0] * (self.width * self.height)

        for v in range(self.height):
            for u in range(self.width):
                origin, ray = self._ray_table(u, v)
                best_t: Optional[float] = None

                if ray[2] < -1e-6:
                    t_plane = origin[2] / -ray[2]
                    hit_x = origin[0] + ray[0] * t_plane
                    hit_y = origin[1] + ray[1] * t_plane
                    if (
                        self.origin_x <= hit_x <= self.origin_x + self.table_width
                        and self.origin_y <= hit_y <= self.origin_y + self.table_depth
                    ):
                        best_t = t_plane

                for box in self.objects:
                    t_box = self._intersect_box(origin, ray, box)
                    if t_box is not None and (best_t is None or t_box < best_t):
                        best_t = t_box

                if best_t is None:
                    continue

                camera_depth = best_t
                depths[v * self.width + u] = camera_depth

        return depths

    def publish_frame(self) -> None:
        stamp = self.get_clock().now().to_msg()
        depths = self._render_depth()

        depth_msg = Image()
        depth_msg.header.stamp = stamp
        depth_msg.header.frame_id = self.camera_frame
        depth_msg.height = self.height
        depth_msg.width = self.width
        depth_msg.encoding = "32FC1"
        depth_msg.is_bigendian = False
        depth_msg.step = self.width * 4
        depth_array = array.array("f", depths)
        depth_msg.data = depth_array.tobytes()
        self.depth_pub.publish(depth_msg)

        camera_info = CameraInfo()
        camera_info.header = depth_msg.header
        camera_info.height = self.height
        camera_info.width = self.width
        camera_info.k = [
            self.fx,
            0.0,
            self.cx,
            0.0,
            self.fy,
            self.cy,
            0.0,
            0.0,
            1.0,
        ]
        camera_info.p = [
            self.fx,
            0.0,
            self.cx,
            0.0,
            0.0,
            self.fy,
            self.cy,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
        ]
        camera_info.r = [
            1.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            1.0,
        ]
        camera_info.distortion_model = "plumb_bob"
        camera_info.d = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.camera_info_pub.publish(camera_info)


def main() -> None:
    rclpy.init()
    node = SyntheticDepthPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
