#pragma once

#include <cstddef>
#include <string>
#include <vector>

namespace brainx_perception_2p5d_slots
{

struct LayoutConfig
{
  std::string table_frame{"table_frame"};
  double origin_x{0.0};
  double origin_y{0.0};
  double width{1.2};
  double depth{0.4};
  double slot_z_min{0.015};
  double slot_z_max{0.25};
  std::size_t columns{12};
  std::size_t rows{2};
};

struct SlotPrism
{
  std::size_t id{0};
  std::size_t row{0};
  std::size_t column{0};
  double min_x{0.0};
  double max_x{0.0};
  double min_y{0.0};
  double max_y{0.0};
  double min_z{0.0};
  double max_z{0.0};

  [[nodiscard]] double center_x() const;
  [[nodiscard]] double center_y() const;
  [[nodiscard]] double center_z() const;
  [[nodiscard]] double size_x() const;
  [[nodiscard]] double size_y() const;
  [[nodiscard]] double size_z() const;
};

class SlotLayout
{
public:
  explicit SlotLayout(LayoutConfig config);

  [[nodiscard]] const LayoutConfig & config() const;
  [[nodiscard]] const std::vector<SlotPrism> & slots() const;
  [[nodiscard]] std::size_t slot_count() const;

private:
  LayoutConfig config_;
  std::vector<SlotPrism> slots_;
};

}  // namespace brainx_perception_2p5d_slots
