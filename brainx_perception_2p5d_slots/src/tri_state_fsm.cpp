#include "brainx_perception_2p5d_slots/tri_state_fsm.hpp"

#include <stdexcept>

namespace brainx_perception_2p5d_slots
{

TriStateFsm::TriStateFsm(FsmConfig config, std::size_t slot_count)
: config_(config), histories_(slot_count), states_(slot_count, SlotStateValue::kUnknown)
{
}

const std::vector<SlotStateValue> & TriStateFsm::states() const
{
  return states_;
}

std::vector<SlotStateValue> TriStateFsm::update(const std::vector<SlotEvidenceSample> & evidences)
{
  if (evidences.size() != histories_.size()) {
    throw std::invalid_argument("evidence size must match configured slot count");
  }

  for (std::size_t index = 0; index < evidences.size(); ++index) {
    auto & history = histories_[index];
    const SlotStateValue target = classify(evidences[index], history.state);

    if (target == history.state) {
      history.candidate = target;
      history.candidate_count = 0;
      states_[index] = history.state;
      continue;
    }

    if (history.candidate != target) {
      history.candidate = target;
      history.candidate_count = 1;
    } else {
      ++history.candidate_count;
    }

    if (history.candidate_count >= dwell_for_state(target)) {
      history.state = target;
      history.candidate_count = 0;
      history.candidate = target;
    }

    states_[index] = history.state;
  }

  return states_;
}

SlotStateValue TriStateFsm::classify(
  const SlotEvidenceSample & evidence,
  SlotStateValue current_state) const
{
  if (evidence.visibility_ratio < config_.unknown_visibility_ratio) {
    return SlotStateValue::kUnknown;
  }

  const bool occupied = evidence.max_height_m >= config_.occupied_height_threshold_m ||
    evidence.occupied_support_ratio >= (
    current_state == SlotStateValue::kOccupied ?
    config_.occupied_exit_support_ratio :
    config_.occupied_enter_support_ratio);

  if (occupied) {
    return SlotStateValue::kOccupied;
  }

  const bool free = evidence.visibility_ratio >= config_.free_min_visibility_ratio &&
    evidence.occupied_support_ratio <= config_.free_support_ratio_max &&
    evidence.max_height_m <= config_.free_height_max_m;

  if (free) {
    return SlotStateValue::kFree;
  }

  return SlotStateValue::kUnknown;
}

std::size_t TriStateFsm::dwell_for_state(SlotStateValue state) const
{
  switch (state) {
    case SlotStateValue::kOccupied:
      return config_.occupied_dwell_frames;
    case SlotStateValue::kFree:
      return config_.free_dwell_frames;
    case SlotStateValue::kUnknown:
    default:
      return config_.unknown_dwell_frames;
  }
}

}  // namespace brainx_perception_2p5d_slots
