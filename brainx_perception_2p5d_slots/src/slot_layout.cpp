#include "brainx_perception_2p5d_slots/slot_layout.hpp"

#include <stdexcept>

namespace brainx_perception_2p5d_slots
{

double SlotPrism::center_x() const
{
  return (min_x + max_x) * 0.5;
}

double SlotPrism::center_y() const
{
  return (min_y + max_y) * 0.5;
}

double SlotPrism::center_z() const
{
  return (min_z + max_z) * 0.5;
}

double SlotPrism::size_x() const
{
  return max_x - min_x;
}

double SlotPrism::size_y() const
{
  return max_y - min_y;
}

double SlotPrism::size_z() const
{
  return max_z - min_z;
}

SlotLayout::SlotLayout(LayoutConfig config)
: config_(std::move(config))
{
  if (config_.columns == 0 || config_.rows == 0) {
    throw std::invalid_argument("slot layout requires at least one row and one column");
  }
  if (config_.width <= 0.0 || config_.depth <= 0.0) {
    throw std::invalid_argument("slot layout requires positive width and depth");
  }
  if (config_.slot_z_max <= config_.slot_z_min) {
    throw std::invalid_argument("slot z max must be greater than slot z min");
  }

  const double cell_width = config_.width / static_cast<double>(config_.columns);
  const double cell_depth = config_.depth / static_cast<double>(config_.rows);
  slots_.reserve(config_.columns * config_.rows);

  for (std::size_t column = 0; column < config_.columns; ++column) {
    for (std::size_t row = 0; row < config_.rows; ++row) {
      SlotPrism prism;
      prism.id = column * config_.rows + row;
      prism.row = row;
      prism.column = column;
      prism.min_x = config_.origin_x + static_cast<double>(column) * cell_width;
      prism.max_x = prism.min_x + cell_width;
      prism.min_y = config_.origin_y + static_cast<double>(row) * cell_depth;
      prism.max_y = prism.min_y + cell_depth;
      prism.min_z = config_.slot_z_min;
      prism.max_z = config_.slot_z_max;
      slots_.push_back(prism);
    }
  }
}

const LayoutConfig & SlotLayout::config() const
{
  return config_;
}

const std::vector<SlotPrism> & SlotLayout::slots() const
{
  return slots_;
}

std::size_t SlotLayout::slot_count() const
{
  return slots_.size();
}

}  // namespace brainx_perception_2p5d_slots
