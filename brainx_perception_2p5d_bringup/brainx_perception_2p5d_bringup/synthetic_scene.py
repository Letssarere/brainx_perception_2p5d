from __future__ import annotations

import array
from dataclasses import dataclass
from typing import Iterable

from builtin_interfaces.msg import Time
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image

DEPTH_TOPIC = "/pickup_2p5d/input/depth"
CAMERA_INFO_TOPIC = "/pickup_2p5d/input/camera_info"
COLOR_TOPIC = "/pickup_2p5d/input/color"
COLOR_CAMERA_INFO_TOPIC = "/pickup_2p5d/input/color_camera_info"


@dataclass(frozen=True)
class Box:
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float


@dataclass(frozen=True)
class ScenarioPhase:
    frame_count: int
    occupied_slots: tuple[int, ...] = ()
    hidden_slots: tuple[int, ...] = ()


@dataclass(frozen=True)
class SyntheticSceneConfig:
    origin_x: float = 0.0
    origin_y: float = 0.0
    table_width: float = 1.2
    table_depth: float = 0.4
    columns: int = 12
    rows: int = 2
    width: int = 160
    height: int = 120
    fx: float = 155.0
    fy: float = 180.0
    cx: float = 80.0
    cy: float = 60.0
    camera_frame: str = "synthetic_camera"
    camera_x: float = 0.6
    camera_y: float = 0.2
    camera_z: float = 1.1
    publish_rate_hz: float = 5.0
    object_height_m: float = 0.14
    object_width_scale: float = 0.58
    object_depth_scale: float = 0.50
    occupied_static_slots: tuple[int, ...] = (2, 5, 16)
    low_visibility_slots: tuple[int, ...] = (6, 18)
    insert_remove_slot: int = 8
    static_frame_count: int = 14
    insert_remove_empty_frames: int = 10
    insert_remove_occupied_frames: int = 10

    @classmethod
    def from_node(cls, node: Node) -> "SyntheticSceneConfig":
        return cls(
            origin_x=float(node.declare_parameter("geometry.origin_x", cls.origin_x).value),
            origin_y=float(node.declare_parameter("geometry.origin_y", cls.origin_y).value),
            table_width=float(node.declare_parameter("geometry.width", cls.table_width).value),
            table_depth=float(node.declare_parameter("geometry.depth", cls.table_depth).value),
            columns=int(node.declare_parameter("geometry.columns", cls.columns).value),
            rows=int(node.declare_parameter("geometry.rows", cls.rows).value),
            width=int(node.declare_parameter("synthetic.width", cls.width).value),
            height=int(node.declare_parameter("synthetic.height", cls.height).value),
            fx=float(node.declare_parameter("synthetic.fx", cls.fx).value),
            fy=float(node.declare_parameter("synthetic.fy", cls.fy).value),
            cx=float(node.declare_parameter("synthetic.cx", cls.cx).value),
            cy=float(node.declare_parameter("synthetic.cy", cls.cy).value),
            camera_frame=str(
                node.declare_parameter("synthetic.camera_frame", cls.camera_frame).value
            ),
            camera_x=float(node.declare_parameter("synthetic.camera_x", cls.camera_x).value),
            camera_y=float(node.declare_parameter("synthetic.camera_y", cls.camera_y).value),
            camera_z=float(node.declare_parameter("synthetic.camera_z", cls.camera_z).value),
            publish_rate_hz=float(
                node.declare_parameter("synthetic.publish_rate_hz", cls.publish_rate_hz).value
            ),
            object_height_m=float(
                node.declare_parameter("synthetic.object_height_m", cls.object_height_m).value
            ),
            object_width_scale=float(
                node.declare_parameter(
                    "synthetic.object_width_scale", cls.object_width_scale
                ).value
            ),
            object_depth_scale=float(
                node.declare_parameter(
                    "synthetic.object_depth_scale", cls.object_depth_scale
                ).value
            ),
            occupied_static_slots=tuple(
                int(slot_id)
                for slot_id in node.declare_parameter(
                    "synthetic.occupied_static_slots", list(cls.occupied_static_slots)
                ).value
            ),
            low_visibility_slots=tuple(
                int(slot_id)
                for slot_id in node.declare_parameter(
                    "synthetic.low_visibility_slots", list(cls.low_visibility_slots)
                ).value
            ),
            insert_remove_slot=int(
                node.declare_parameter("synthetic.insert_remove_slot", cls.insert_remove_slot).value
            ),
            static_frame_count=int(
                node.declare_parameter("synthetic.static_frame_count", cls.static_frame_count).value
            ),
            insert_remove_empty_frames=int(
                node.declare_parameter(
                    "synthetic.insert_remove_empty_frames", cls.insert_remove_empty_frames
                ).value
            ),
            insert_remove_occupied_frames=int(
                node.declare_parameter(
                    "synthetic.insert_remove_occupied_frames", cls.insert_remove_occupied_frames
                ).value
            ),
        )


@dataclass(frozen=True)
class ScenarioState:
    occupied_slots: tuple[int, ...]
    hidden_slots: tuple[int, ...]


class SyntheticSceneRenderer:
    def __init__(self, config: SyntheticSceneConfig) -> None:
        self.config = config
        self.slot_width = config.table_width / float(config.columns)
        self.slot_depth = config.table_depth / float(config.rows)
        self._slot_bounds = {
            slot_id: self._slot_bounds_for(slot_id)
            for slot_id in range(config.columns * config.rows)
        }

    @staticmethod
    def available_scenarios() -> tuple[str, ...]:
        return ("empty_table", "occupied_static", "insert_remove", "low_visibility")

    def scenario_frame_count(self, scenario_name: str) -> int:
        static_count = max(self.config.static_frame_count, 1)
        if scenario_name in {"empty_table", "occupied_static", "low_visibility"}:
            return static_count
        if scenario_name == "insert_remove":
            return max(self.config.insert_remove_empty_frames, 1) * 2 + max(
                self.config.insert_remove_occupied_frames, 1
            )
        raise ValueError(f"unsupported scenario: {scenario_name}")

    def render_depth_frame(self, scenario_name: str, frame_index: int) -> list[float]:
        scenario_state = self._scenario_state(scenario_name, frame_index)
        occupied_boxes = self._build_boxes(scenario_state.occupied_slots)
        hidden_slots = set(scenario_state.hidden_slots)
        depths = [0.0] * (self.config.width * self.config.height)

        for v in range(self.config.height):
            for u in range(self.config.width):
                origin, ray = self._ray_in_table_frame(u, v)
                best_t = self._intersect_table(origin, ray)

                for box in occupied_boxes:
                    box_t = self._intersect_box(origin, ray, box)
                    if box_t is not None and (best_t is None or box_t < best_t):
                        best_t = box_t

                if best_t is None:
                    continue

                hit_x = origin[0] + ray[0] * best_t
                hit_y = origin[1] + ray[1] * best_t
                if self._point_is_hidden(hit_x, hit_y, hidden_slots):
                    continue

                depths[v * self.config.width + u] = float(best_t)

        return depths

    def render_color_frame(self, scenario_name: str, frame_index: int) -> bytes:
        scenario_state = self._scenario_state(scenario_name, frame_index)
        occupied_boxes = self._build_boxes(scenario_state.occupied_slots)
        hidden_slots = set(scenario_state.hidden_slots)
        pixels = bytearray(self.config.width * self.config.height * 3)

        for v in range(self.config.height):
            for u in range(self.config.width):
                origin, ray = self._ray_in_table_frame(u, v)
                best_t = self._intersect_table(origin, ray)
                hit_type = "background"

                for box in occupied_boxes:
                    box_t = self._intersect_box(origin, ray, box)
                    if box_t is not None and (best_t is None or box_t < best_t):
                        best_t = box_t
                        hit_type = "occupied"

                color_index = (v * self.config.width + u) * 3
                if best_t is None:
                    pixels[color_index : color_index + 3] = bytes((18, 18, 28))
                    continue

                hit_x = origin[0] + ray[0] * best_t
                hit_y = origin[1] + ray[1] * best_t
                if self._point_is_hidden(hit_x, hit_y, hidden_slots):
                    pixels[color_index : color_index + 3] = bytes((24, 24, 24))
                    continue

                if hit_type == "occupied":
                    pixels[color_index : color_index + 3] = bytes((214, 66, 54))
                    continue

                pixels[color_index : color_index + 3] = bytes(self._table_color(hit_x, hit_y))

        return bytes(pixels)

    def make_depth_message(self, stamp: Time, depths: list[float]) -> Image:
        depth_msg = Image()
        depth_msg.header.stamp = stamp
        depth_msg.header.frame_id = self.config.camera_frame
        depth_msg.height = self.config.height
        depth_msg.width = self.config.width
        depth_msg.encoding = "32FC1"
        depth_msg.is_bigendian = False
        depth_msg.step = self.config.width * 4
        depth_msg.data = array.array("f", depths).tobytes()
        return depth_msg

    def make_color_message(self, stamp: Time, rgb_bytes: bytes) -> Image:
        color_msg = Image()
        color_msg.header.stamp = stamp
        color_msg.header.frame_id = self.config.camera_frame
        color_msg.height = self.config.height
        color_msg.width = self.config.width
        color_msg.encoding = "rgb8"
        color_msg.is_bigendian = False
        color_msg.step = self.config.width * 3
        color_msg.data = rgb_bytes
        return color_msg

    def make_camera_info_message(self, stamp: Time) -> CameraInfo:
        camera_info = CameraInfo()
        camera_info.header.stamp = stamp
        camera_info.header.frame_id = self.config.camera_frame
        camera_info.height = self.config.height
        camera_info.width = self.config.width
        camera_info.k = [
            self.config.fx,
            0.0,
            self.config.cx,
            0.0,
            self.config.fy,
            self.config.cy,
            0.0,
            0.0,
            1.0,
        ]
        camera_info.p = [
            self.config.fx,
            0.0,
            self.config.cx,
            0.0,
            0.0,
            self.config.fy,
            self.config.cy,
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
        return camera_info

    def make_color_camera_info_message(self, stamp: Time) -> CameraInfo:
        return self.make_camera_info_message(stamp)

    def _scenario_state(self, scenario_name: str, frame_index: int) -> ScenarioState:
        if scenario_name == "empty_table":
            return ScenarioState(occupied_slots=(), hidden_slots=())
        if scenario_name == "occupied_static":
            return ScenarioState(
                occupied_slots=self.config.occupied_static_slots,
                hidden_slots=(),
            )
        if scenario_name == "low_visibility":
            return ScenarioState(
                occupied_slots=(),
                hidden_slots=self.config.low_visibility_slots,
            )
        if scenario_name == "insert_remove":
            return self._insert_remove_state(frame_index)
        raise ValueError(f"unsupported scenario: {scenario_name}")

    def _insert_remove_state(self, frame_index: int) -> ScenarioState:
        empty_frames = max(self.config.insert_remove_empty_frames, 1)
        occupied_frames = max(self.config.insert_remove_occupied_frames, 1)
        phase_index = frame_index % self.scenario_frame_count("insert_remove")

        phases = (
            ScenarioPhase(frame_count=empty_frames),
            ScenarioPhase(
                frame_count=occupied_frames,
                occupied_slots=(self.config.insert_remove_slot,),
            ),
            ScenarioPhase(frame_count=empty_frames),
        )

        running = 0
        for phase in phases:
            running += phase.frame_count
            if phase_index < running:
                return ScenarioState(
                    occupied_slots=phase.occupied_slots,
                    hidden_slots=phase.hidden_slots,
                )

        return ScenarioState(occupied_slots=(), hidden_slots=())

    def _slot_bounds_for(self, slot_id: int) -> tuple[float, float, float, float]:
        column = slot_id // self.config.rows
        row = slot_id % self.config.rows
        min_x = self.config.origin_x + column * self.slot_width
        max_x = min_x + self.slot_width
        min_y = self.config.origin_y + row * self.slot_depth
        max_y = min_y + self.slot_depth
        return (min_x, max_x, min_y, max_y)

    def _build_boxes(self, slot_ids: Iterable[int]) -> list[Box]:
        boxes: list[Box] = []
        half_width = self.slot_width * self.config.object_width_scale * 0.5
        half_depth = self.slot_depth * self.config.object_depth_scale * 0.5

        for slot_id in slot_ids:
            min_x, max_x, min_y, max_y = self._slot_bounds[slot_id]
            center_x = 0.5 * (min_x + max_x)
            center_y = 0.5 * (min_y + max_y)
            boxes.append(
                Box(
                    min_x=center_x - half_width,
                    max_x=center_x + half_width,
                    min_y=center_y - half_depth,
                    max_y=center_y + half_depth,
                    min_z=0.0,
                    max_z=self.config.object_height_m,
                )
            )
        return boxes

    def _point_is_hidden(
        self, hit_x: float, hit_y: float, hidden_slots: set[int]
    ) -> bool:
        margin_x = 0.03
        margin_y = 0.03
        for slot_id in hidden_slots:
            min_x, max_x, min_y, max_y = self._slot_bounds[slot_id]
            if (
                min_x - margin_x <= hit_x <= max_x + margin_x
                and min_y - margin_y <= hit_y <= max_y + margin_y
            ):
                return True
        return False

    def _table_color(self, hit_x: float, hit_y: float) -> tuple[int, int, int]:
        normalized_x = (hit_x - self.config.origin_x) / self.config.table_width
        normalized_y = (hit_y - self.config.origin_y) / self.config.table_depth
        normalized_x = max(0.0, min(normalized_x, 1.0))
        normalized_y = max(0.0, min(normalized_y, 1.0))

        if self._is_near_slot_boundary(hit_x, hit_y):
            return (238, 238, 238)

        red = int(34 + 46 * normalized_x)
        green = int(92 + 64 * normalized_y)
        blue = int(128 + 52 * (1.0 - normalized_x * 0.5))
        return (red, green, blue)

    def _is_near_slot_boundary(self, hit_x: float, hit_y: float) -> bool:
        boundary_margin = 0.005
        local_x = hit_x - self.config.origin_x
        local_y = hit_y - self.config.origin_y
        x_offset = local_x % self.slot_width
        y_offset = local_y % self.slot_depth
        return (
            x_offset < boundary_margin
            or self.slot_width - x_offset < boundary_margin
            or y_offset < boundary_margin
            or self.slot_depth - y_offset < boundary_margin
        )

    def _ray_in_table_frame(
        self, u: int, v: int
    ) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        camera_ray = (
            (float(u) - self.config.cx) / self.config.fx,
            (float(v) - self.config.cy) / self.config.fy,
            1.0,
        )
        table_ray = (camera_ray[0], -camera_ray[1], -camera_ray[2])
        table_origin = (
            self.config.camera_x,
            self.config.camera_y,
            self.config.camera_z,
        )
        return table_origin, table_ray

    def _intersect_table(
        self,
        ray_origin: tuple[float, float, float],
        ray_dir: tuple[float, float, float],
    ) -> float | None:
        if ray_dir[2] >= -1e-6:
            return None

        table_t = ray_origin[2] / -ray_dir[2]
        hit_x = ray_origin[0] + ray_dir[0] * table_t
        hit_y = ray_origin[1] + ray_dir[1] * table_t
        if (
            self.config.origin_x <= hit_x <= self.config.origin_x + self.config.table_width
            and self.config.origin_y <= hit_y <= self.config.origin_y + self.config.table_depth
        ):
            return table_t
        return None

    def _intersect_box(
        self,
        ray_origin: tuple[float, float, float],
        ray_dir: tuple[float, float, float],
        box: Box,
    ) -> float | None:
        t_min = -float("inf")
        t_max = float("inf")
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

            inv_direction = 1.0 / direction
            t_first = (lower - origin) * inv_direction
            t_second = (upper - origin) * inv_direction
            if t_first > t_second:
                t_first, t_second = t_second, t_first
            t_min = max(t_min, t_first)
            t_max = min(t_max, t_second)
            if t_min > t_max:
                return None

        if t_max < 0.0:
            return None
        return t_min if t_min > 0.0 else t_max
