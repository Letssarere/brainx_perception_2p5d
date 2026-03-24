#include "brainx_perception_2p5d_map/depth_filter.hpp"

namespace brainx_perception_2p5d_map
{

DepthFilter::DepthFilter(DepthFilterConfig config)
: config_(config)
{
}

bool DepthFilter::is_valid(float depth_m) const
{
  return std::isfinite(depth_m) &&
         depth_m >= config_.min_depth_m &&
         depth_m <= config_.max_depth_m;
}

}  // namespace brainx_perception_2p5d_map
