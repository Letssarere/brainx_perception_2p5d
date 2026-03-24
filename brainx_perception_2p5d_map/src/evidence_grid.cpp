#include "brainx_perception_2p5d_map/evidence_grid.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace brainx_perception_2p5d_map
{

EvidenceGrid::EvidenceGrid(GridConfig config)
: config_(std::move(config))
{
  if (config_.width <= 0.0 || config_.depth <= 0.0 || config_.resolution <= 0.0) {
    throw std::invalid_argument("grid dimensions and resolution must be positive");
  }
  width_ = static_cast<std::size_t>(std::ceil(config_.width / config_.resolution));
  height_ = static_cast<std::size_t>(std::ceil(config_.depth / config_.resolution));
  cells_.resize(width_ * height_);
}

void EvidenceGrid::begin_frame()
{
  for (auto & cell : cells_) {
    cell.height_residual_m *= config_.occupied_decay;
    cell.occupied_score *= config_.occupied_decay;
    cell.visibility_score *= config_.visibility_decay;
    cell.variance *= 0.98F;
  }
}

void EvidenceGrid::integrate_point(double x, double y, double z)
{
  if (!contains(x, y)) {
    return;
  }

  const auto grid_x = static_cast<std::size_t>((x - config_.origin_x) / config_.resolution);
  const auto grid_y = static_cast<std::size_t>((y - config_.origin_y) / config_.resolution);
  auto & cell = cells_[index_of(grid_x, grid_y)];

  const float clamped_height = static_cast<float>(std::clamp(z, 0.0, config_.z_max));
  const float delta = clamped_height - cell.height_residual_m;
  cell.height_residual_m = std::max(cell.height_residual_m, clamped_height);
  cell.variance = 0.9F * cell.variance + 0.1F * delta * delta;
  cell.visibility_score = std::clamp(
    cell.visibility_score + config_.visibility_increment,
    0.0F,
    1.0F);
  ++cell.valid_count;

  if (clamped_height >= config_.occupied_height_threshold_m) {
    cell.occupied_score = std::clamp(
      cell.occupied_score + config_.occupied_increment,
      0.0F,
      1.0F);
  } else {
    cell.occupied_score = std::max(0.0F, cell.occupied_score - config_.occupied_increment * 0.5F);
  }
}

const GridConfig & EvidenceGrid::config() const
{
  return config_;
}

std::size_t EvidenceGrid::width() const
{
  return width_;
}

std::size_t EvidenceGrid::height() const
{
  return height_;
}

const std::vector<GridCell> & EvidenceGrid::cells() const
{
  return cells_;
}

GridExportData EvidenceGrid::export_data() const
{
  GridExportData data;
  data.width = width_;
  data.height = height_;
  data.resolution = config_.resolution;
  data.origin_x = config_.origin_x;
  data.origin_y = config_.origin_y;
  data.height_residual_m.reserve(cells_.size());
  data.valid_count.reserve(cells_.size());
  data.occupied_score.reserve(cells_.size());
  data.variance.reserve(cells_.size());
  data.visibility_score.reserve(cells_.size());

  for (const auto & cell : cells_) {
    data.height_residual_m.push_back(cell.height_residual_m);
    data.valid_count.push_back(cell.valid_count);
    data.occupied_score.push_back(cell.occupied_score);
    data.variance.push_back(cell.variance);
    data.visibility_score.push_back(cell.visibility_score);
  }

  return data;
}

double EvidenceGrid::cell_center_x(std::size_t x) const
{
  return config_.origin_x + (static_cast<double>(x) + 0.5) * config_.resolution;
}

double EvidenceGrid::cell_center_y(std::size_t y) const
{
  return config_.origin_y + (static_cast<double>(y) + 0.5) * config_.resolution;
}

bool EvidenceGrid::contains(double x, double y) const
{
  return x >= config_.origin_x &&
         y >= config_.origin_y &&
         x < config_.origin_x + config_.width &&
         y < config_.origin_y + config_.depth;
}

std::size_t EvidenceGrid::index_of(std::size_t x, std::size_t y) const
{
  return y * width_ + x;
}

}  // namespace brainx_perception_2p5d_map
