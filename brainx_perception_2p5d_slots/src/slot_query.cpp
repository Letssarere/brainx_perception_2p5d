#include "brainx_perception_2p5d_slots/slot_query.hpp"

#include <algorithm>
#include <stdexcept>

namespace brainx_perception_2p5d_slots
{

namespace
{

std::size_t index_of(const GridSnapshot & grid, std::size_t x, std::size_t y)
{
  return y * grid.width + x;
}

}  // namespace

SlotQuery::SlotQuery(QueryConfig config)
: config_(config)
{
}

std::vector<SlotEvidenceSample> SlotQuery::evaluate(
  const SlotLayout & layout,
  const GridSnapshot & grid) const
{
  const std::size_t cell_count = grid.width * grid.height;
  if (grid.height_residual_m.size() != cell_count ||
    grid.occupied_score.size() != cell_count ||
    grid.valid_count.size() != cell_count ||
    grid.variance.size() != cell_count ||
    grid.visibility_score.size() != cell_count)
  {
    throw std::invalid_argument("grid snapshot arrays must match width * height");
  }

  std::vector<SlotEvidenceSample> evidences;
  evidences.reserve(layout.slot_count());

  for (const auto & slot : layout.slots()) {
    std::size_t total_cells = 0;
    std::size_t visible_cells = 0;
    std::size_t occupied_cells = 0;
    float max_height = 0.0F;

    for (std::size_t y = 0; y < grid.height; ++y) {
      for (std::size_t x = 0; x < grid.width; ++x) {
        const double center_x = grid.origin_x + (static_cast<double>(x) + 0.5) * grid.resolution;
        const double center_y = grid.origin_y + (static_cast<double>(y) + 0.5) * grid.resolution;
        if (center_x < slot.min_x || center_x >= slot.max_x ||
          center_y < slot.min_y || center_y >= slot.max_y)
        {
          continue;
        }

        ++total_cells;
        const auto index = index_of(grid, x, y);
        const float visibility = grid.visibility_score[index];
        const float occupied_score = grid.occupied_score[index];
        const float height = grid.height_residual_m[index];
        max_height = std::max(max_height, height);

        if (visibility >= config_.visibility_visible_threshold) {
          ++visible_cells;
        }
        if (occupied_score >= config_.occupied_score_threshold &&
          height >= config_.occupied_height_threshold_m)
        {
          ++occupied_cells;
        }
      }
    }

    SlotEvidenceSample evidence;
    evidence.slot_id = slot.id;
    if (total_cells > 0) {
      evidence.occupied_support_ratio =
        static_cast<float>(occupied_cells) / static_cast<float>(total_cells);
      evidence.visibility_ratio =
        static_cast<float>(visible_cells) / static_cast<float>(total_cells);
    }
    evidence.max_height_m = max_height;
    evidence.confidence = std::clamp(
      0.5F * evidence.visibility_ratio + 0.5F *
      std::max(evidence.occupied_support_ratio, 1.0F - evidence.occupied_support_ratio),
      0.0F, 1.0F);

    if (evidence.visibility_ratio < config_.visibility_visible_threshold) {
      evidence.evidence_category = "unknown";
    } else if (evidence.occupied_support_ratio >= config_.occupied_score_threshold) {
      evidence.evidence_category = "occupied";
    } else {
      evidence.evidence_category = "free";
    }
    evidences.push_back(evidence);
  }

  return evidences;
}

}  // namespace brainx_perception_2p5d_slots
