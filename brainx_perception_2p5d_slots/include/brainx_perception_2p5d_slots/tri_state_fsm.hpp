#pragma once

#include "brainx_perception_2p5d_slots/slot_query.hpp"

#include <cstddef>
#include <cstdint>
#include <vector>

namespace brainx_perception_2p5d_slots
{

enum class SlotStateValue : uint8_t
{
  kFree = 0,
  kOccupied = 1,
  kUnknown = 2,
};

struct FsmConfig
{
  float occupied_enter_support_ratio{0.28F};
  float occupied_exit_support_ratio{0.18F};
  float occupied_height_threshold_m{0.07F};
  float free_support_ratio_max{0.10F};
  float free_height_max_m{0.04F};
  float free_min_visibility_ratio{0.75F};
  float unknown_visibility_ratio{0.35F};
  std::size_t occupied_dwell_frames{2};
  std::size_t free_dwell_frames{2};
  std::size_t unknown_dwell_frames{1};
};

class TriStateFsm
{
public:
  TriStateFsm(FsmConfig config, std::size_t slot_count);

  [[nodiscard]] const std::vector<SlotStateValue> & states() const;
  [[nodiscard]] std::vector<SlotStateValue> update(
    const std::vector<SlotEvidenceSample> & evidences);

private:
  [[nodiscard]] SlotStateValue classify(
    const SlotEvidenceSample & evidence,
    SlotStateValue current_state) const;
  [[nodiscard]] std::size_t dwell_for_state(SlotStateValue state) const;

  struct SlotHistory
  {
    SlotStateValue state{SlotStateValue::kUnknown};
    SlotStateValue candidate{SlotStateValue::kUnknown};
    std::size_t candidate_count{0};
  };

  FsmConfig config_;
  std::vector<SlotHistory> histories_;
  std::vector<SlotStateValue> states_;
};

}  // namespace brainx_perception_2p5d_slots
