from __future__ import annotations

from brainx_perception_2p5d_bringup.test_support import (
    cleanup_temp_bag,
    collect_stable_pattern,
    generate_temp_bag,
    wait_for_color_inputs,
)


def test_replay_matches_live_synthetic_for_static_scenarios():
    for scenario_name in ("empty_table", "occupied_static", "low_visibility"):
        live_pattern = collect_stable_pattern(
            "table_2p5d_synthetic.launch.py",
            [f"scenario:={scenario_name}"],
        )
        bag_path = generate_temp_bag(scenario_name)
        try:
            replay_pattern = collect_stable_pattern(
                "table_2p5d_replay.launch.py",
                [f"bag_path:={bag_path}"],
            )
        finally:
            cleanup_temp_bag(bag_path)

        assert replay_pattern == live_pattern, scenario_name


def test_replay_launch_replays_color_inputs():
    bag_path = generate_temp_bag("empty_table")
    try:
        wait_for_color_inputs(
            "table_2p5d_replay.launch.py",
            [f"bag_path:={bag_path}"],
        )
    finally:
        cleanup_temp_bag(bag_path)


if __name__ == "__main__":
    test_replay_matches_live_synthetic_for_static_scenarios()
    test_replay_launch_replays_color_inputs()
