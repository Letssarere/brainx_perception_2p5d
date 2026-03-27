#include "brainx_perception_2p5d_map/depth_filter.hpp"
#include "brainx_perception_2p5d_map/evidence_grid.hpp"

#include "brainx_perception_2p5d_msgs/msg/evidence_grid.hpp"
#include "geometry_msgs/msg/point_stamped.hpp"
#include "geometry_msgs/msg/pose.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/image_encodings.hpp"
#include "sensor_msgs/msg/camera_info.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"
#include "visualization_msgs/msg/marker.hpp"
#include "visualization_msgs/msg/marker_array.hpp"

#include <algorithm>
#include <cstring>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace brainx_perception_2p5d_map
{

namespace
{

struct CameraIntrinsics
{
  double fx{0.0};
  double fy{0.0};
  double cx{0.0};
  double cy{0.0};
};

std_msgs::msg::ColorRGBA make_color(float r, float g, float b, float a)
{
  std_msgs::msg::ColorRGBA color;
  color.r = r;
  color.g = g;
  color.b = b;
  color.a = a;
  return color;
}

std::optional<float> read_depth_meters(const sensor_msgs::msg::Image & msg, std::size_t index)
{
  if (msg.encoding == sensor_msgs::image_encodings::TYPE_32FC1 ||
    msg.encoding == "32FC1")
  {
    const auto * values = reinterpret_cast<const float *>(msg.data.data());
    return values[index];
  }

  if (msg.encoding == sensor_msgs::image_encodings::TYPE_16UC1 ||
    msg.encoding == "16UC1")
  {
    const auto * values = reinterpret_cast<const uint16_t *>(msg.data.data());
    return static_cast<float>(values[index]) * 0.001F;
  }

  return std::nullopt;
}

}  // namespace

class MapNode : public rclcpp::Node
{
public:
  MapNode()
  : Node("map_node"),
    tf_buffer_(get_clock()),
    tf_listener_(tf_buffer_)
  {
    GridConfig grid_config;
    grid_config.table_frame = declare_parameter<std::string>("geometry.table_frame", "table_frame");
    grid_config.origin_x = declare_parameter<double>("geometry.origin_x", 0.0);
    grid_config.origin_y = declare_parameter<double>("geometry.origin_y", 0.0);
    grid_config.width = declare_parameter<double>("geometry.width", 1.2);
    grid_config.depth = declare_parameter<double>("geometry.depth", 0.4);
    grid_config.resolution = declare_parameter<double>("perception.grid_resolution_m", 0.05);
    grid_config.z_max = declare_parameter<double>("geometry.slot_z_max", 0.25);
    grid_config.occupied_height_threshold_m =
      declare_parameter<double>("perception.occupied_height_threshold_m", 0.05);
    grid_config.occupied_increment =
      declare_parameter<double>("perception.occupied_increment", 0.18);
    grid_config.occupied_decay =
      declare_parameter<double>("perception.occupied_decay", 0.92);
    grid_config.visibility_increment =
      declare_parameter<double>("perception.visibility_increment", 0.25);
    grid_config.visibility_decay =
      declare_parameter<double>("perception.visibility_decay", 0.88);

    DepthFilterConfig filter_config;
    filter_config.min_depth_m = declare_parameter<double>("perception.min_depth_m", 0.2);
    filter_config.max_depth_m = declare_parameter<double>("perception.max_depth_m", 2.5);
    pixel_stride_ = declare_parameter<int>("perception.pixel_stride", 4);

    grid_ = std::make_unique<EvidenceGrid>(grid_config);
    depth_filter_ = std::make_unique<DepthFilter>(filter_config);

    validated_depth_pub_ = create_publisher<sensor_msgs::msg::Image>(
      "/pickup_2p5d/depth_validated", 10);
    visibility_mask_pub_ = create_publisher<sensor_msgs::msg::Image>(
      "/pickup_2p5d/visibility_mask", 10);
    grid_pub_ = create_publisher<brainx_perception_2p5d_msgs::msg::EvidenceGrid>(
      "/pickup_2p5d/grid", 10);
    grid_markers_pub_ = create_publisher<visualization_msgs::msg::MarkerArray>(
      "/pickup_2p5d/grid_markers", 10);

    const auto sensor_data_qos = rclcpp::SensorDataQoS();
    camera_info_sub_ = create_subscription<sensor_msgs::msg::CameraInfo>(
      "/pickup_2p5d/input/camera_info",
      sensor_data_qos,
      std::bind(&MapNode::on_camera_info, this, std::placeholders::_1));
    depth_sub_ = create_subscription<sensor_msgs::msg::Image>(
      "/pickup_2p5d/input/depth",
      sensor_data_qos,
      std::bind(&MapNode::on_depth, this, std::placeholders::_1));
    color_camera_info_sub_ = create_subscription<sensor_msgs::msg::CameraInfo>(
      "/pickup_2p5d/input/color_camera_info",
      sensor_data_qos,
      std::bind(&MapNode::on_color_camera_info, this, std::placeholders::_1));
    color_sub_ = create_subscription<sensor_msgs::msg::Image>(
      "/pickup_2p5d/input/color",
      sensor_data_qos,
      std::bind(&MapNode::on_color, this, std::placeholders::_1));
  }

private:
  void on_camera_info(const sensor_msgs::msg::CameraInfo::SharedPtr msg)
  {
    if (msg->k[0] <= 0.0 || msg->k[4] <= 0.0) {
      RCLCPP_WARN_THROTTLE(
        get_logger(),
        *get_clock(),
        2000,
        "Waiting for valid camera intrinsics");
      return;
    }

    depth_intrinsics_.fx = msg->k[0];
    depth_intrinsics_.fy = msg->k[4];
    depth_intrinsics_.cx = msg->k[2];
    depth_intrinsics_.cy = msg->k[5];
    have_depth_intrinsics_ = true;
  }

  void on_color_camera_info(const sensor_msgs::msg::CameraInfo::SharedPtr msg)
  {
    if (msg->k[0] <= 0.0 || msg->k[4] <= 0.0) {
      return;
    }

    color_intrinsics_.fx = msg->k[0];
    color_intrinsics_.fy = msg->k[4];
    color_intrinsics_.cx = msg->k[2];
    color_intrinsics_.cy = msg->k[5];
    have_color_intrinsics_ = true;
  }

  void on_color(const sensor_msgs::msg::Image::SharedPtr msg)
  {
    latest_color_image_ = msg;
  }

  void on_depth(const sensor_msgs::msg::Image::SharedPtr msg)
  {
    if (!have_depth_intrinsics_) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000, "Waiting for camera info");
      return;
    }

    geometry_msgs::msg::TransformStamped depth_to_table;
    try {
      depth_to_table = tf_buffer_.lookupTransform(
        grid_->config().table_frame,
        msg->header.frame_id,
        msg->header.stamp,
        tf2::durationFromSec(0.05));
    } catch (const tf2::TransformException & ex) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000, "TF lookup failed: %s", ex.what());
      return;
    }

    grid_->begin_frame();

    const std::size_t pixel_count = static_cast<std::size_t>(msg->width) * msg->height;
    std::vector<float> validated_depth(pixel_count, 0.0F);
    std::vector<uint8_t> visibility_mask(pixel_count, 0U);

    for (std::size_t v = 0; v < msg->height;
      v += static_cast<std::size_t>(std::max(pixel_stride_, 1)))
    {
      for (std::size_t u = 0; u < msg->width;
        u += static_cast<std::size_t>(std::max(pixel_stride_, 1)))
      {
        const auto index = v * msg->width + u;
        const auto depth_value = read_depth_meters(*msg, index);
        if (!depth_value.has_value() || !depth_filter_->is_valid(*depth_value)) {
          continue;
        }

        geometry_msgs::msg::PointStamped point_in;
        point_in.header = msg->header;
        point_in.point.x =
          ((static_cast<double>(u) - depth_intrinsics_.cx) / depth_intrinsics_.fx) * *depth_value;
        point_in.point.y =
          ((static_cast<double>(v) - depth_intrinsics_.cy) / depth_intrinsics_.fy) * *depth_value;
        point_in.point.z = *depth_value;

        geometry_msgs::msg::PointStamped point_out;
        tf2::doTransform(point_in, point_out, depth_to_table);
        grid_->integrate_point(point_out.point.x, point_out.point.y, point_out.point.z);
        validated_depth[index] = *depth_value;
        visibility_mask[index] = 255U;
      }
    }

    publish_debug_images(*msg, validated_depth, visibility_mask);
    publish_grid(*msg);
  }

  void publish_debug_images(
    const sensor_msgs::msg::Image & source,
    const std::vector<float> & validated_depth,
    const std::vector<uint8_t> & visibility_mask)
  {
    sensor_msgs::msg::Image validated_msg;
    validated_msg.header = source.header;
    validated_msg.height = source.height;
    validated_msg.width = source.width;
    validated_msg.encoding = sensor_msgs::image_encodings::TYPE_32FC1;
    validated_msg.is_bigendian = false;
    validated_msg.step = source.width * sizeof(float);
    validated_msg.data.resize(validated_depth.size() * sizeof(float));
    std::memcpy(validated_msg.data.data(), validated_depth.data(), validated_msg.data.size());
    validated_depth_pub_->publish(validated_msg);

    sensor_msgs::msg::Image mask_msg;
    mask_msg.header = source.header;
    mask_msg.height = source.height;
    mask_msg.width = source.width;
    mask_msg.encoding = sensor_msgs::image_encodings::MONO8;
    mask_msg.is_bigendian = false;
    mask_msg.step = source.width;
    mask_msg.data = visibility_mask;
    visibility_mask_pub_->publish(mask_msg);
  }

  void publish_grid(const sensor_msgs::msg::Image & source)
  {
    const auto export_data = grid_->export_data();

    brainx_perception_2p5d_msgs::msg::EvidenceGrid msg;
    msg.header = source.header;
    msg.header.frame_id = grid_->config().table_frame;
    msg.width = static_cast<uint32_t>(export_data.width);
    msg.height = static_cast<uint32_t>(export_data.height);
    msg.resolution = static_cast<float>(export_data.resolution);
    msg.origin.position.x = export_data.origin_x;
    msg.origin.position.y = export_data.origin_y;
    msg.origin.position.z = 0.0;
    msg.origin.orientation.w = 1.0;
    msg.height_residual_m = export_data.height_residual_m;
    msg.valid_count = export_data.valid_count;
    msg.occupied_score = export_data.occupied_score;
    msg.variance = export_data.variance;
    msg.visibility_score = export_data.visibility_score;
    grid_pub_->publish(msg);

    visualization_msgs::msg::MarkerArray markers;
    visualization_msgs::msg::Marker clear;
    clear.header = msg.header;
    clear.action = visualization_msgs::msg::Marker::DELETEALL;
    markers.markers.push_back(clear);

    const auto & cells = grid_->cells();
    for (std::size_t y = 0; y < grid_->height(); ++y) {
      for (std::size_t x = 0; x < grid_->width(); ++x) {
        const auto index = y * grid_->width() + x;
        const auto & cell = cells[index];
        if (cell.visibility_score < 0.05F) {
          continue;
        }

        visualization_msgs::msg::Marker marker;
        marker.header = msg.header;
        marker.ns = "grid";
        marker.id = static_cast<int>(index);
        marker.type = visualization_msgs::msg::Marker::CUBE;
        marker.action = visualization_msgs::msg::Marker::ADD;
        marker.pose.position.x = grid_->cell_center_x(x);
        marker.pose.position.y = grid_->cell_center_y(y);
        marker.pose.position.z = std::max(0.01, static_cast<double>(cell.height_residual_m) * 0.5);
        marker.pose.orientation.w = 1.0;
        marker.scale.x = grid_->config().resolution * 0.95;
        marker.scale.y = grid_->config().resolution * 0.95;
        marker.scale.z = std::max(0.02, static_cast<double>(cell.height_residual_m));
        marker.color = make_color(
          cell.occupied_score,
          std::clamp(cell.visibility_score, 0.0F, 1.0F),
          1.0F - cell.occupied_score,
          0.45F);
        marker.lifetime = rclcpp::Duration::from_seconds(0.3);
        markers.markers.push_back(marker);
      }
    }

    grid_markers_pub_->publish(markers);
  }

  std::unique_ptr<EvidenceGrid> grid_;
  std::unique_ptr<DepthFilter> depth_filter_;
  CameraIntrinsics depth_intrinsics_;
  CameraIntrinsics color_intrinsics_;
  bool have_depth_intrinsics_{false};
  bool have_color_intrinsics_{false};
  int pixel_stride_{4};
  tf2_ros::Buffer tf_buffer_;
  tf2_ros::TransformListener tf_listener_;
  rclcpp::Subscription<sensor_msgs::msg::CameraInfo>::SharedPtr camera_info_sub_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr depth_sub_;
  rclcpp::Subscription<sensor_msgs::msg::CameraInfo>::SharedPtr color_camera_info_sub_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr color_sub_;
  sensor_msgs::msg::Image::SharedPtr latest_color_image_;
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr validated_depth_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr visibility_mask_pub_;
  rclcpp::Publisher<brainx_perception_2p5d_msgs::msg::EvidenceGrid>::SharedPtr grid_pub_;
  rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr grid_markers_pub_;
};

}  // namespace brainx_perception_2p5d_map

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<brainx_perception_2p5d_map::MapNode>());
  rclcpp::shutdown();
  return 0;
}
