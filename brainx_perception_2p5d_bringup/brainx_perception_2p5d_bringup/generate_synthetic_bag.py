from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

import rosbag2_py
from builtin_interfaces.msg import Time
from rclpy.serialization import serialize_message

from brainx_perception_2p5d_bringup.synthetic_scene import (
    CAMERA_INFO_TOPIC,
    DEPTH_TOPIC,
    SyntheticSceneConfig,
    SyntheticSceneRenderer,
)

DEFAULT_BAG_REPEAT_COUNT = 4


def generate_bag(
    output_uri: str | Path | None,
    scenario_name: str,
    config: SyntheticSceneConfig | None = None,
    force: bool = True,
) -> Path:
    scene_config = config or SyntheticSceneConfig()
    renderer = SyntheticSceneRenderer(scene_config)
    if scenario_name not in renderer.available_scenarios():
        raise ValueError(f"unsupported scenario: {scenario_name}")

    if output_uri is None:
        temp_root = Path(tempfile.mkdtemp(prefix=f"brainx_2p5d_{scenario_name}_"))
        bag_path = temp_root / "bag"
    else:
        bag_path = Path(output_uri)

    if bag_path.exists():
        if not force:
            raise FileExistsError(f"bag output already exists: {bag_path}")
        if bag_path.is_dir():
            shutil.rmtree(bag_path)
        else:
            bag_path.unlink()

    bag_path.parent.mkdir(parents=True, exist_ok=True)

    writer = rosbag2_py.SequentialWriter()
    storage_options = rosbag2_py.StorageOptions(uri=str(bag_path), storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions("cdr", "cdr")
    writer.open(storage_options, converter_options)
    writer.create_topic(
        rosbag2_py.TopicMetadata(
            DEPTH_TOPIC,
            "sensor_msgs/msg/Image",
            "cdr",
            "",
        )
    )
    writer.create_topic(
        rosbag2_py.TopicMetadata(
            CAMERA_INFO_TOPIC,
            "sensor_msgs/msg/CameraInfo",
            "cdr",
            "",
        )
    )

    period_ns = max(int(round(1_000_000_000.0 / scene_config.publish_rate_hz)), 1)
    start_ns = 1_000_000_000
    frame_count = renderer.scenario_frame_count(scenario_name)

    output_frame_index = 0
    for _ in range(DEFAULT_BAG_REPEAT_COUNT):
        for frame_index in range(frame_count):
            stamp_ns = start_ns + output_frame_index * period_ns
            stamp = _stamp_from_ns(stamp_ns)
            depth_msg = renderer.make_depth_message(
                stamp, renderer.render_depth_frame(scenario_name, frame_index)
            )
            camera_info_msg = renderer.make_camera_info_message(stamp)
            writer.write(DEPTH_TOPIC, serialize_message(depth_msg), stamp_ns)
            writer.write(CAMERA_INFO_TOPIC, serialize_message(camera_info_msg), stamp_ns)
            output_frame_index += 1

    return bag_path


def _stamp_from_ns(timestamp_ns: int) -> Time:
    seconds, nanoseconds = divmod(timestamp_ns, 1_000_000_000)
    return Time(sec=int(seconds), nanosec=int(nanoseconds))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a deterministic synthetic rosbag2.")
    parser.add_argument(
        "--scenario",
        default="occupied_static",
        choices=SyntheticSceneRenderer.available_scenarios(),
    )
    parser.add_argument("--output-uri")
    parser.add_argument("--no-force", action="store_true")
    args = parser.parse_args()

    bag_path = generate_bag(
        output_uri=args.output_uri,
        scenario_name=args.scenario,
        force=not args.no_force,
    )
    print(bag_path)


if __name__ == "__main__":
    main()
