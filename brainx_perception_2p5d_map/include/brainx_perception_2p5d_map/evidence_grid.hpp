#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace brainx_perception_2p5d_map
{

struct GridConfig
{
  std::string table_frame{"table_frame"};
  double origin_x{0.0};
  double origin_y{0.0};
  double width{1.2};
  double depth{0.4};
  double resolution{0.05};
  double z_max{0.25};
  float occupied_height_threshold_m{0.05F};
  float occupied_increment{0.18F};
  float occupied_decay{0.92F};
  float visibility_increment{0.25F};
  float visibility_decay{0.88F};
};

struct GridCell
{
  float height_residual_m{0.0F};
  uint32_t valid_count{0};
  float occupied_score{0.0F};
  float variance{0.0F};
  float visibility_score{0.0F};
};

struct GridExportData
{
  std::size_t width{0};
  std::size_t height{0};
  double resolution{0.05};
  double origin_x{0.0};
  double origin_y{0.0};
  std::vector<float> height_residual_m;
  std::vector<uint32_t> valid_count;
  std::vector<float> occupied_score;
  std::vector<float> variance;
  std::vector<float> visibility_score;
};

class EvidenceGrid
{
public:
  explicit EvidenceGrid(GridConfig config);

  void begin_frame();
  void integrate_point(double x, double y, double z);

  [[nodiscard]] const GridConfig & config() const;
  [[nodiscard]] std::size_t width() const;
  [[nodiscard]] std::size_t height() const;
  [[nodiscard]] const std::vector<GridCell> & cells() const;
  [[nodiscard]] GridExportData export_data() const;
  [[nodiscard]] double cell_center_x(std::size_t x) const;
  [[nodiscard]] double cell_center_y(std::size_t y) const;

private:
  [[nodiscard]] bool contains(double x, double y) const;
  [[nodiscard]] std::size_t index_of(std::size_t x, std::size_t y) const;

  GridConfig config_;
  std::size_t width_{0};
  std::size_t height_{0};
  std::vector<GridCell> cells_;
};

}  // namespace brainx_perception_2p5d_map
