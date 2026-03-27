from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import rclpy
from brainx_perception_2p5d_bringup.generate_synthetic_bag import generate_bag
from brainx_perception_2p5d_msgs.msg import SlotStateArray
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image


class SlotStateWatcher(Node):
    def __init__(self) -> None:
        super().__init__("slot_state_watcher")
        self._sequence = 0
        self._latest_pattern: tuple[int, ...] | None = None
        self._subscription = self.create_subscription(
            SlotStateArray,
            "/pickup_2p5d/slot_states",
            self._callback,
            10,
        )

    @property
    def sequence(self) -> int:
        return self._sequence

    @property
    def latest_pattern(self) -> tuple[int, ...] | None:
        return self._latest_pattern

    def _callback(self, msg: SlotStateArray) -> None:
        self._latest_pattern = tuple(item.state for item in msg.states)
        self._sequence += 1


class ColorInputWatcher(Node):
    def __init__(self) -> None:
        super().__init__("color_input_watcher")
        self._color_seen = False
        self._color_camera_info_seen = False
        self._color_sub = self.create_subscription(
            Image,
            "/pickup_2p5d/input/color",
            self._on_color,
            10,
        )
        self._color_camera_info_sub = self.create_subscription(
            CameraInfo,
            "/pickup_2p5d/input/color_camera_info",
            self._on_color_camera_info,
            10,
        )

    @property
    def have_color_inputs(self) -> bool:
        return self._color_seen and self._color_camera_info_seen

    def _on_color(self, _msg: Image) -> None:
        self._color_seen = True

    def _on_color_camera_info(self, _msg: CameraInfo) -> None:
        self._color_camera_info_seen = True


def collect_stable_pattern(
    launch_file: str,
    launch_args: list[str] | None = None,
    timeout: float = 12.0,
    stable_count: int = 3,
) -> tuple[int, ...]:
    args = list(launch_args or [])
    if not any(argument.startswith("headless:=") for argument in args):
        args.append("headless:=true")

    proc = _launch_process(launch_file, args)
    watcher, shutdown_after = _create_watcher()

    try:
        deadline = time.monotonic() + timeout
        last_sequence = -1
        last_pattern: tuple[int, ...] | None = None
        stable_pattern: tuple[int, ...] | None = None
        consecutive = 0

        while time.monotonic() < deadline:
            rclpy.spin_once(watcher, timeout_sec=0.25)
            if watcher.sequence == last_sequence or watcher.latest_pattern is None:
                continue

            last_sequence = watcher.sequence
            pattern = watcher.latest_pattern
            if len(pattern) != 24:
                continue

            if pattern == last_pattern:
                consecutive += 1
            else:
                last_pattern = pattern
                consecutive = 1

            if consecutive >= stable_count:
                stable_pattern = pattern

        if stable_pattern is None:
            raise AssertionError(f"stable slot-state pattern not observed for {launch_file}")
        return stable_pattern
    except Exception as exc:
        raise AssertionError(_failure_message(proc, str(exc))) from exc
    finally:
        watcher.destroy_node()
        if shutdown_after and rclpy.ok():
            rclpy.shutdown()
        _terminate_process(proc)


def collect_slot_transition_sequence(
    launch_file: str,
    launch_args: list[str],
    slot_id: int,
    expected_sequence: list[int],
    timeout: float = 30.0,
    stable_count: int = 2,
) -> list[int]:
    args = list(launch_args)
    if not any(argument.startswith("headless:=") for argument in args):
        args.append("headless:=true")

    proc = _launch_process(launch_file, args)
    watcher, shutdown_after = _create_watcher()

    try:
        deadline = time.monotonic() + timeout
        last_sequence = -1
        candidate_state: int | None = None
        candidate_count = 0
        stable_states: list[int] = []

        while time.monotonic() < deadline:
            rclpy.spin_once(watcher, timeout_sec=0.25)
            if watcher.sequence == last_sequence or watcher.latest_pattern is None:
                continue

            last_sequence = watcher.sequence
            pattern = watcher.latest_pattern
            if len(pattern) != 24:
                continue

            slot_state = pattern[slot_id]
            if slot_state == candidate_state:
                candidate_count += 1
            else:
                candidate_state = slot_state
                candidate_count = 1

            if candidate_count < stable_count:
                continue

            if not stable_states or stable_states[-1] != slot_state:
                stable_states.append(slot_state)
                if _contains_subsequence(stable_states, expected_sequence):
                    return stable_states

        raise AssertionError(
            f"expected slot {slot_id} transition {expected_sequence}, got {stable_states}"
        )
    except Exception as exc:
        raise AssertionError(_failure_message(proc, str(exc))) from exc
    finally:
        watcher.destroy_node()
        if shutdown_after and rclpy.ok():
            rclpy.shutdown()
        _terminate_process(proc)


def wait_for_color_inputs(
    launch_file: str,
    launch_args: list[str] | None = None,
    timeout: float = 12.0,
) -> None:
    args = list(launch_args or [])
    if not any(argument.startswith("headless:=") for argument in args):
        args.append("headless:=true")

    proc = _launch_process(launch_file, args)
    watcher, shutdown_after = _create_color_input_watcher()

    try:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            rclpy.spin_once(watcher, timeout_sec=0.25)
            if watcher.have_color_inputs:
                return

        raise AssertionError(f"color inputs not observed for {launch_file}")
    except Exception as exc:
        raise AssertionError(_failure_message(proc, str(exc))) from exc
    finally:
        watcher.destroy_node()
        if shutdown_after and rclpy.ok():
            rclpy.shutdown()
        _terminate_process(proc)


def generate_temp_bag(scenario_name: str) -> Path:
    temp_root = Path(os.environ.get("TMPDIR", "/tmp")) / f"brainx_2p5d_{os.getpid()}_{int(time.time() * 1000)}"
    bag_path = temp_root / "bag"
    return generate_bag(bag_path, scenario_name)


def cleanup_temp_bag(bag_path: Path) -> None:
    if bag_path.exists():
        shutil.rmtree(bag_path)
    parent = bag_path.parent
    if parent.exists() and parent.name.startswith("brainx_2p5d_"):
        shutil.rmtree(parent)


def _create_watcher() -> tuple[SlotStateWatcher, bool]:
    shutdown_after = not rclpy.ok()
    if shutdown_after:
        rclpy.init()
    return SlotStateWatcher(), shutdown_after


def _create_color_input_watcher() -> tuple[ColorInputWatcher, bool]:
    shutdown_after = not rclpy.ok()
    if shutdown_after:
        rclpy.init()
    return ColorInputWatcher(), shutdown_after


def _launch_process(launch_file: str, launch_args: list[str]) -> subprocess.Popen[str]:
    env = os.environ.copy()
    python_bin_dir = str(Path(sys.executable).resolve().parent)
    current_path = env.get("PATH", "")
    if current_path:
        env["PATH"] = f"{python_bin_dir}:{current_path}"
    else:
        env["PATH"] = python_bin_dir
    return subprocess.Popen(
        ["ros2", "launch", "brainx_perception_2p5d_bringup", launch_file, *launch_args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
        start_new_session=True,
    )


def _terminate_process(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=5.0)


def _failure_message(proc: subprocess.Popen[str], message: str) -> str:
    _terminate_process(proc)
    output = ""
    if proc.stdout is not None:
        output = proc.stdout.read()
    return f"{message}\nlaunch output:\n{output}"


def _contains_subsequence(values: list[int], target: list[int]) -> bool:
    if len(values) < len(target):
        return False
    for start in range(len(values) - len(target) + 1):
        if values[start : start + len(target)] == target:
            return True
    return False
