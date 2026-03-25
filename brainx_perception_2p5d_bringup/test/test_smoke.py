from brainx_perception_2p5d_bringup.test_support import (
    collect_slot_transition_sequence,
    collect_stable_pattern,
)
from brainx_perception_2p5d_msgs.msg import SlotState


def test_empty_table_is_all_free():
    pattern = collect_stable_pattern(
        "table_2p5d_synthetic.launch.py",
        ["scenario:=empty_table"],
    )
    assert len(pattern) == 24
    assert all(state == SlotState.FREE for state in pattern)


def test_occupied_static_matches_expected_slots():
    pattern = collect_stable_pattern(
        "table_2p5d_synthetic.launch.py",
        ["scenario:=occupied_static"],
    )
    occupied_slots = {index for index, state in enumerate(pattern) if state == SlotState.OCCUPIED}
    assert occupied_slots == {2, 5, 16}
    assert all(
        state == SlotState.FREE for index, state in enumerate(pattern) if index not in occupied_slots
    )


def test_low_visibility_yields_unknown_not_free():
    pattern = collect_stable_pattern(
        "table_2p5d_synthetic.launch.py",
        ["scenario:=low_visibility"],
    )
    assert pattern[6] == SlotState.UNKNOWN
    assert pattern[18] == SlotState.UNKNOWN
    for index, state in enumerate(pattern):
        if index in {6, 18}:
            continue
        assert state == SlotState.FREE


def test_insert_remove_reaches_free_then_occupied_then_free():
    states = collect_slot_transition_sequence(
        "table_2p5d_synthetic.launch.py",
        ["scenario:=insert_remove"],
        slot_id=8,
        expected_sequence=[SlotState.FREE, SlotState.OCCUPIED, SlotState.FREE],
    )
    assert [SlotState.FREE, SlotState.OCCUPIED, SlotState.FREE] == states[-3:]


if __name__ == "__main__":
    test_empty_table_is_all_free()
    test_occupied_static_matches_expected_slots()
    test_low_visibility_yields_unknown_not_free()
    test_insert_remove_reaches_free_then_occupied_then_free()
