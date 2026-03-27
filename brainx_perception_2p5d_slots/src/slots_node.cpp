#include "brainx_perception_2p5d_slots/slot_layout.hpp"
#include "brainx_perception_2p5d_slots/slot_query.hpp"
#include "brainx_perception_2p5d_slots/tri_state_fsm.hpp"

#include "brainx_perception_2p5d_msgs/msg/evidence_grid.hpp"
#include "brainx_perception_2p5d_msgs/msg/slot_evidence.hpp"
#include "brainx_perception_2p5d_msgs/msg/slot_evidence_array.hpp"
#include "brainx_perception_2p5d_msgs/msg/slot_state.hpp"
#include "brainx_perception_2p5d_msgs/msg/slot_state_array.hpp"
#include "geometry_msgs/msg/pose.hpp"
#include "rclcpp/rclcpp.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "visualization_msgs/msg/marker_array.hpp"

#include <algorithm>
#include <memory>
#include <string>
#include <utility>
#include <vector>

namespace brainx_perception_2p5d_slots
{

namespace
{

std_msgs::msg::ColorRGBA make_color(float r, float g, float b, float a)
{
  std_msgs::msg::ColorRGBA color;
  color.r = r;
  color.g = g;
  color.b = b;
  color.a = a;
  return color;
}

std_msgs::msg::ColorRGBA state_color(SlotStateValue state)
{
  switch (state) {
    case SlotStateValue::kFree:
      return make_color(0.15F, 0.75F, 0.25F, 0.45F);
    case SlotStateValue::kOccupied:
      return make_color(0.85F, 0.2F, 0.15F, 0.55F);
    case SlotStateValue::kUnknown:
    default:
      return make_color(0.9F, 0.7F, 0.1F, 0.45F);
  }
}

uint8_t to_msg_state(SlotStateValue state)
{
  switch (state) {
    case SlotStateValue::kFree:
      return brainx_perception_2p5d_msgs::msg::SlotState::FREE;
    case SlotStateValue::kOccupied:
      return brainx_perception_2p5d_msgs::msg::SlotState::OCCUPIED;
    case SlotStateValue::kUnknown:
    default:
      return brainx_perception_2p5d_msgs::msg::SlotState::UNKNOWN;
  }
}

std::string to_label(SlotStateValue state)
{
  switch (state) {
    case SlotStateValue::kFree:
      return "FREE";
    case SlotStateValue::kOccupied:
      return "OCCUPIED";
    case SlotStateValue::kUnknown:
    default:
      return "UNKNOWN";
  }
}

}  // namespace

class SlotsNode : public rclcpp::Node
{
public:
  SlotsNode()
  : Node("slots_node")
  {
    LayoutConfig layout_config;
    layout_config.table_frame =
      declare_parameter<std::string>("geometry.table_frame", "table_frame");
    layout_config.origin_x = declare_parameter<double>("geometry.origin_x", 0.0);
    layout_config.origin_y = declare_parameter<double>("geometry.origin_y", 0.0);
    layout_config.width = declare_parameter<double>("geometry.width", 1.2);
    layout_config.depth = declare_parameter<double>("geometry.depth", 0.4);
    layout_config.slot_z_min = declare_parameter<double>("geometry.slot_z_min", 0.015);
    layout_config.slot_z_max = declare_parameter<double>("geometry.slot_z_max", 0.25);
    layout_config.columns =
      static_cast<std::size_t>(declare_parameter<int>("geometry.columns", 12));
    layout_config.rows = static_cast<std::size_t>(declare_parameter<int>("geometry.rows", 2));

    QueryConfig query_config;
    query_config.visibility_visible_threshold =
      declare_parameter<double>("perception.visibility_visible_threshold", 0.2);
    query_config.occupied_score_threshold =
      declare_parameter<double>("perception.occupied_score_threshold", 0.45);
    query_config.occupied_height_threshold_m =
      declare_parameter<double>("perception.occupied_height_threshold_m", 0.05);

    FsmConfig fsm_config;
    fsm_config.occupied_enter_support_ratio =
      declare_parameter<double>("fsm.occupied_enter_support_ratio", 0.28);
    fsm_config.occupied_exit_support_ratio =
      declare_parameter<double>("fsm.occupied_exit_support_ratio", 0.18);
    fsm_config.occupied_height_threshold_m =
      declare_parameter<double>("fsm.occupied_height_threshold_m", 0.07);
    fsm_config.free_support_ratio_max =
      declare_parameter<double>("fsm.free_support_ratio_max", 0.10);
    fsm_config.free_height_max_m =
      declare_parameter<double>("fsm.free_height_max_m", 0.04);
    fsm_config.free_min_visibility_ratio =
      declare_parameter<double>("fsm.free_min_visibility_ratio", 0.75);
    fsm_config.unknown_visibility_ratio =
      declare_parameter<double>("fsm.unknown_visibility_ratio", 0.35);
    fsm_config.occupied_dwell_frames =
      static_cast<std::size_t>(declare_parameter<int>("fsm.occupied_dwell_frames", 2));
    fsm_config.free_dwell_frames =
      static_cast<std::size_t>(declare_parameter<int>("fsm.free_dwell_frames", 2));
    fsm_config.unknown_dwell_frames =
      static_cast<std::size_t>(declare_parameter<int>("fsm.unknown_dwell_frames", 1));

    layout_ = std::make_unique<SlotLayout>(layout_config);
    query_ = std::make_unique<SlotQuery>(query_config);
    fsm_ = std::make_unique<TriStateFsm>(fsm_config, layout_->slot_count());

    evidence_pub_ = create_publisher<brainx_perception_2p5d_msgs::msg::SlotEvidenceArray>(
      "/pickup_2p5d/slot_evidence", 10);
    states_pub_ = create_publisher<brainx_perception_2p5d_msgs::msg::SlotStateArray>(
      "/pickup_2p5d/slot_states", 10);
    markers_pub_ = create_publisher<visualization_msgs::msg::MarkerArray>(
      "/pickup_2p5d/slot_markers", 10);

    grid_sub_ = create_subscription<brainx_perception_2p5d_msgs::msg::EvidenceGrid>(
      "/pickup_2p5d/grid",
      10,
      std::bind(&SlotsNode::on_grid, this, std::placeholders::_1));
  }

private:
  void on_grid(const brainx_perception_2p5d_msgs::msg::EvidenceGrid::SharedPtr msg)
  {
    GridSnapshot grid;
    grid.width = msg->width;
    grid.height = msg->height;
    grid.resolution = msg->resolution;
    grid.origin_x = msg->origin.position.x;
    grid.origin_y = msg->origin.position.y;
    grid.height_residual_m = msg->height_residual_m;
    grid.occupied_score = msg->occupied_score;
    grid.valid_count = msg->valid_count;
    grid.variance = msg->variance;
    grid.visibility_score = msg->visibility_score;

    const auto evidences = query_->evaluate(*layout_, grid);
    const auto states = fsm_->update(evidences);

    brainx_perception_2p5d_msgs::msg::SlotEvidenceArray evidence_msg;
    evidence_msg.header = msg->header;
    evidence_msg.table_frame = layout_->config().table_frame;
    evidence_msg.evidences.reserve(evidences.size());

    for (const auto & evidence : evidences) {
      brainx_perception_2p5d_msgs::msg::SlotEvidence evidence_item;
      evidence_item.slot_id = static_cast<uint8_t>(evidence.slot_id);
      evidence_item.evidence_category = evidence.evidence_category;
      evidence_item.occupied_support_ratio = evidence.occupied_support_ratio;
      evidence_item.max_height_m = evidence.max_height_m;
      evidence_item.visibility_ratio = evidence.visibility_ratio;
      evidence_item.confidence = evidence.confidence;
      evidence_msg.evidences.push_back(std::move(evidence_item));
    }
    evidence_pub_->publish(evidence_msg);

    brainx_perception_2p5d_msgs::msg::SlotStateArray states_msg;
    states_msg.header = msg->header;
    states_msg.table_frame = layout_->config().table_frame;
    states_msg.states.reserve(states.size());
    const auto & slots = layout_->slots();

    for (std::size_t index = 0; index < states.size(); ++index) {
      brainx_perception_2p5d_msgs::msg::SlotState state_item;
      state_item.slot_id = static_cast<uint8_t>(slots[index].id);
      state_item.state = to_msg_state(states[index]);
      states_msg.states.push_back(std::move(state_item));
    }
    states_pub_->publish(states_msg);

    publish_markers(msg->header, states);
  }

  void publish_markers(
    const std_msgs::msg::Header & header,
    const std::vector<SlotStateValue> & states)
  {
    visualization_msgs::msg::MarkerArray marker_array;
    const auto & slots = layout_->slots();
    marker_array.markers.reserve(slots.size() * 2);

    for (std::size_t index = 0; index < slots.size(); ++index) {
      const auto & slot = slots[index];

      visualization_msgs::msg::Marker cube;
      cube.header = header;
      cube.header.frame_id = layout_->config().table_frame;
      cube.ns = "slot_state";
      cube.id = static_cast<int>(slot.id);
      cube.type = visualization_msgs::msg::Marker::CUBE;
      cube.action = visualization_msgs::msg::Marker::ADD;
      cube.pose.position.x = slot.center_x();
      cube.pose.position.y = slot.center_y();
      cube.pose.position.z = slot.center_z();
      cube.pose.orientation.w = 1.0;
      cube.scale.x = slot.size_x();
      cube.scale.y = slot.size_y();
      cube.scale.z = slot.size_z();
      cube.color = state_color(states[index]);
      cube.lifetime = rclcpp::Duration::from_seconds(0.3);
      marker_array.markers.push_back(cube);

      visualization_msgs::msg::Marker text;
      text.header = cube.header;
      text.ns = "slot_state_text";
      text.id = static_cast<int>(slot.id + 1000);
      text.type = visualization_msgs::msg::Marker::TEXT_VIEW_FACING;
      text.action = visualization_msgs::msg::Marker::ADD;
      text.pose.position.x = slot.center_x();
      text.pose.position.y = slot.center_y();
      text.pose.position.z = slot.max_z + 0.05;
      text.pose.orientation.w = 1.0;
      text.scale.z = 0.04;
      text.color = make_color(1.0F, 1.0F, 1.0F, 0.95F);
      text.text = std::to_string(slot.id) + ":" + to_label(states[index]);
      text.lifetime = cube.lifetime;
      marker_array.markers.push_back(text);
    }

    markers_pub_->publish(marker_array);
  }

  std::unique_ptr<SlotLayout> layout_;
  std::unique_ptr<SlotQuery> query_;
  std::unique_ptr<TriStateFsm> fsm_;
  rclcpp::Subscription<brainx_perception_2p5d_msgs::msg::EvidenceGrid>::SharedPtr grid_sub_;
  rclcpp::Publisher<brainx_perception_2p5d_msgs::msg::SlotEvidenceArray>::SharedPtr evidence_pub_;
  rclcpp::Publisher<brainx_perception_2p5d_msgs::msg::SlotStateArray>::SharedPtr states_pub_;
  rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr markers_pub_;
};

}  // namespace brainx_perception_2p5d_slots

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<brainx_perception_2p5d_slots::SlotsNode>());
  rclcpp::shutdown();
  return 0;
}
