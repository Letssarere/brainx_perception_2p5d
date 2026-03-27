#include "brainx_perception_2p5d_slots/slot_layout.hpp"
#include "brainx_perception_2p5d_slots/slot_query.hpp"

#include <gtest/gtest.h>

#include <cstddef>

namespace
{

void mark_cells(
  brainx_perception_2p5d_slots::GridSnapshot & grid,
  std::size_t column,
  std::size_t row_start,
  std::size_t row_end,
  float occupied_score,
  float height,
  float visibility)
{
  for (std::size_t row = row_start; row < row_end; ++row) {
    const auto index = row * grid.width + column;
    grid.occupied_score[index] = occupied_score;
    grid.height_residual_m[index] = height;
    grid.visibility_score[index] = visibility;
    grid.valid_count[index] = visibility > 0.0F ? 1U : 0U;
  }
}

TEST(SlotQueryTest, AggregatesOccupiedFreeAndUnknownEvidencePerSlot)
{
  brainx_perception_2p5d_slots::LayoutConfig layout_config;
  layout_config.width = 1.2;
  layout_config.depth = 0.4;
  const brainx_perception_2p5d_slots::SlotLayout layout(layout_config);

  brainx_perception_2p5d_slots::GridSnapshot grid;
  grid.width = 12;
  grid.height = 4;
  grid.resolution = 0.1;
  grid.origin_x = 0.0;
  grid.origin_y = 0.0;
  const auto cell_count = grid.width * grid.height;
  grid.height_residual_m.assign(cell_count, 0.0F);
  grid.occupied_score.assign(cell_count, 0.0F);
  grid.valid_count.assign(cell_count, 0U);
  grid.variance.assign(cell_count, 0.0F);
  grid.visibility_score.assign(cell_count, 0.0F);

  mark_cells(grid, 2, 0, 2, 0.8F, 0.10F, 1.0F);
  mark_cells(grid, 3, 0, 2, 0.05F, 0.02F, 1.0F);
  mark_cells(grid, 6, 0, 2, 0.0F, 0.0F, 0.0F);

  brainx_perception_2p5d_slots::QueryConfig query_config;
  const brainx_perception_2p5d_slots::SlotQuery query(query_config);
  const auto evidences = query.evaluate(layout, grid);

  ASSERT_EQ(evidences.size(), layout.slot_count());

  EXPECT_EQ(evidences[4].evidence_category, "occupied");
  EXPECT_FLOAT_EQ(evidences[4].occupied_support_ratio, 1.0F);
  EXPECT_FLOAT_EQ(evidences[4].visibility_ratio, 1.0F);
  EXPECT_FLOAT_EQ(evidences[4].max_height_m, 0.10F);

  EXPECT_EQ(evidences[6].evidence_category, "free");
  EXPECT_FLOAT_EQ(evidences[6].occupied_support_ratio, 0.0F);
  EXPECT_FLOAT_EQ(evidences[6].visibility_ratio, 1.0F);
  EXPECT_FLOAT_EQ(evidences[6].max_height_m, 0.02F);

  EXPECT_EQ(evidences[12].evidence_category, "unknown");
  EXPECT_FLOAT_EQ(evidences[12].occupied_support_ratio, 0.0F);
  EXPECT_FLOAT_EQ(evidences[12].visibility_ratio, 0.0F);
  EXPECT_FLOAT_EQ(evidences[12].max_height_m, 0.0F);
}

}  // namespace
