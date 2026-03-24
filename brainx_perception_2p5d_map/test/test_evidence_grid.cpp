#include "brainx_perception_2p5d_map/depth_filter.hpp"
#include "brainx_perception_2p5d_map/evidence_grid.hpp"

#include <gtest/gtest.h>

#include <limits>

namespace
{

TEST(DepthFilterTest, RejectsInvalidDepthValues)
{
  const brainx_perception_2p5d_map::DepthFilter filter(
    brainx_perception_2p5d_map::DepthFilterConfig{0.2F, 2.5F});

  EXPECT_FALSE(filter.is_valid(std::numeric_limits<float>::quiet_NaN()));
  EXPECT_FALSE(filter.is_valid(0.1F));
  EXPECT_FALSE(filter.is_valid(3.0F));
  EXPECT_TRUE(filter.is_valid(0.75F));
}

TEST(EvidenceGridTest, AccumulatesVisibilityAndOccupiedEvidence)
{
  brainx_perception_2p5d_map::GridConfig config;
  config.width = 0.2;
  config.depth = 0.1;
  config.resolution = 0.05;
  config.occupied_height_threshold_m = 0.05F;
  brainx_perception_2p5d_map::EvidenceGrid grid(config);

  grid.begin_frame();
  grid.integrate_point(0.02, 0.02, 0.0);

  auto data = grid.export_data();
  ASSERT_FALSE(data.visibility_score.empty());
  EXPECT_GT(data.visibility_score.front(), 0.0F);
  EXPECT_EQ(data.occupied_score.front(), 0.0F);

  grid.begin_frame();
  grid.integrate_point(0.02, 0.02, 0.12);

  data = grid.export_data();
  EXPECT_GT(data.height_residual_m.front(), 0.1F);
  EXPECT_GT(data.occupied_score.front(), 0.0F);
  EXPECT_EQ(data.valid_count.front(), 2U);

  const auto previous_count = data.valid_count.front();
  grid.begin_frame();
  grid.integrate_point(1.0, 1.0, 0.12);
  data = grid.export_data();
  EXPECT_EQ(data.valid_count.front(), previous_count);
}

}  // namespace
