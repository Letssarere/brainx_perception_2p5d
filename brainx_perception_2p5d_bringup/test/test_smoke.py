import os
import signal
import subprocess
import time

import rclpy
from brainx_perception_2p5d_msgs.msg import SlotState, SlotStateArray
from rclpy.node import Node


class SlotStateWatcher(Node):
    def __init__(self) -> None:
        super().__init__("slot_state_watcher")
        self.message = None
        self.subscription = self.create_subscription(
            SlotStateArray,
            "/pickup_2p5d/slot_states",
            self._callback,
            10,
        )

    def _callback(self, msg: SlotStateArray) -> None:
        self.message = msg


def test_synthetic_bringup_smoke():
    env = os.environ.copy()
    proc = subprocess.Popen(
        ["ros2", "launch", "brainx_perception_2p5d_bringup", "table_2p5d_replay.launch.py", "headless:=true"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )

    if not rclpy.ok():
        rclpy.init()

    watcher = SlotStateWatcher()
    deadline = time.time() + 20.0

    try:
        while time.time() < deadline:
            rclpy.spin_once(watcher, timeout_sec=0.5)
            if watcher.message is None:
                continue

            states = [item.state for item in watcher.message.states]
            if SlotState.OCCUPIED in states and SlotState.FREE in states:
                break

        assert watcher.message is not None, (
            proc.stdout.read() if proc.stdout else "slot state message not received"
        )
        assert len(watcher.message.states) == 24
        states = [item.state for item in watcher.message.states]
        assert SlotState.OCCUPIED in states
        assert SlotState.FREE in states
    finally:
        watcher.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5.0)


if __name__ == "__main__":
    test_synthetic_bringup_smoke()
