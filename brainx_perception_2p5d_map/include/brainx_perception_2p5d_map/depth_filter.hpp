#pragma once

#include <cmath>

namespace brainx_perception_2p5d_map
{

struct DepthFilterConfig
{
  float min_depth_m{0.2F};
  float max_depth_m{2.5F};
};

class DepthFilter
{
public:
  explicit DepthFilter(DepthFilterConfig config);

  [[nodiscard]] bool is_valid(float depth_m) const;

private:
  DepthFilterConfig config_;
};

}  // namespace brainx_perception_2p5d_map
