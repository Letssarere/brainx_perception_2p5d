#include "brainx_perception_2p5d_slots/slot_layout.hpp"

#include <gtest/gtest.h>

namespace
{

TEST(SlotLayoutTest, GeneratesTwentyFourRowMajorSlots)
{
  brainx_perception_2p5d_slots::LayoutConfig config;
  config.origin_x = 0.2;
  config.origin_y = -0.1;
  config.width = 1.2;
  config.depth = 0.4;

  const brainx_perception_2p5d_slots::SlotLayout layout(config);

  ASSERT_EQ(layout.slot_count(), 24U);
  EXPECT_EQ(layout.slots().front().id, 0U);
  EXPECT_EQ(layout.slots().front().row, 0U);
  EXPECT_EQ(layout.slots().front().column, 0U);
  EXPECT_EQ(layout.slots()[11].id, 11U);
  EXPECT_EQ(layout.slots()[11].row, 0U);
  EXPECT_EQ(layout.slots()[12].id, 12U);
  EXPECT_EQ(layout.slots()[12].row, 1U);
  EXPECT_EQ(layout.slots().back().id, 23U);
  EXPECT_DOUBLE_EQ(layout.slots().front().min_z, 0.015);
  EXPECT_DOUBLE_EQ(layout.slots().front().max_z, 0.25);
  EXPECT_NEAR(layout.slots()[1].min_x - layout.slots()[0].min_x, 0.1, 1e-9);
  EXPECT_NEAR(layout.slots()[12].min_y - layout.slots()[0].min_y, 0.2, 1e-9);
}

}  // namespace
