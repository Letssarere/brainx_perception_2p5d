#pragma once

#include "brainx_perception_2p5d_slots/slot_layout.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace brainx_perception_2p5d_slots
{

struct GridSnapshot
{
  std::size_t width{0};
  std::size_t height{0};
  double resolution{0.05};
  double origin_x{0.0};
  double origin_y{0.0};
  std::vector<float> height_residual_m;
  std::vector<float> occupied_score;
  std::vector<uint32_t> valid_count;
  std::vector<float> variance;
  std::vector<float> visibility_score;
};

struct QueryConfig
{
  float visibility_visible_threshold{0.2F};
  float occupied_score_threshold{0.45F};
  float occupied_height_threshold_m{0.05F};
};

struct SlotEvidenceSample
{
  std::size_t slot_id{0};
  std::string evidence_category{"unknown"};
  float occupied_support_ratio{0.0F};
  float max_height_m{0.0F};
  float visibility_ratio{0.0F};
  float confidence{0.0F};
};

class SlotQuery
{
public:
  explicit SlotQuery(QueryConfig config);

  [[nodiscard]] std::vector<SlotEvidenceSample> evaluate(
    const SlotLayout & layout,
    const GridSnapshot & grid) const;

private:
  QueryConfig config_;
};

}  // namespace brainx_perception_2p5d_slots
