#include "brainx_perception_2p5d_slots/tri_state_fsm.hpp"

#include <gtest/gtest.h>

namespace
{

brainx_perception_2p5d_slots::SlotEvidenceSample make_evidence(
  float support,
  float height,
  float visibility)
{
  brainx_perception_2p5d_slots::SlotEvidenceSample evidence;
  evidence.occupied_support_ratio = support;
  evidence.max_height_m = height;
  evidence.visibility_ratio = visibility;
  evidence.confidence = 1.0F;
  return evidence;
}

TEST(TriStateFsmTest, TransitionsToOccupiedThenFreeWithDwell)
{
  brainx_perception_2p5d_slots::FsmConfig config;
  brainx_perception_2p5d_slots::TriStateFsm fsm(config, 1);

  auto states = fsm.update({make_evidence(0.5F, 0.12F, 1.0F)});
  EXPECT_EQ(states[0], brainx_perception_2p5d_slots::SlotStateValue::kUnknown);

  states = fsm.update({make_evidence(0.5F, 0.12F, 1.0F)});
  EXPECT_EQ(states[0], brainx_perception_2p5d_slots::SlotStateValue::kOccupied);

  states = fsm.update({make_evidence(0.0F, 0.01F, 1.0F)});
  EXPECT_EQ(states[0], brainx_perception_2p5d_slots::SlotStateValue::kOccupied);

  states = fsm.update({make_evidence(0.0F, 0.01F, 1.0F)});
  EXPECT_EQ(states[0], brainx_perception_2p5d_slots::SlotStateValue::kFree);
}

TEST(TriStateFsmTest, LowVisibilityYieldsUnknownNotFree)
{
  brainx_perception_2p5d_slots::FsmConfig config;
  brainx_perception_2p5d_slots::TriStateFsm fsm(config, 1);

  auto states = fsm.update({make_evidence(0.0F, 0.0F, 0.1F)});
  EXPECT_EQ(states[0], brainx_perception_2p5d_slots::SlotStateValue::kUnknown);

  states = fsm.update({make_evidence(0.0F, 0.0F, 0.1F)});
  EXPECT_EQ(states[0], brainx_perception_2p5d_slots::SlotStateValue::kUnknown);
}

}  // namespace
