cmake_minimum_required(VERSION 3.8)
project(brainx_perception_2p5d_slots)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_gtest REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(brainx_perception_2p5d_msgs REQUIRED)

add_library(brainx_perception_2p5d_slots_core
  src/slot_layout.cpp
  src/slot_query.cpp
  src/tri_state_fsm.cpp
)
target_compile_features(brainx_perception_2p5d_slots_core PUBLIC cxx_std_17)
target_include_directories(brainx_perception_2p5d_slots_core PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

add_executable(slots_node src/slots_node.cpp)
target_compile_features(slots_node PUBLIC cxx_std_17)
target_link_libraries(slots_node brainx_perception_2p5d_slots_core)
ament_target_dependencies(slots_node
  rclcpp
  geometry_msgs
  visualization_msgs
  brainx_perception_2p5d_msgs
)

install(
  TARGETS brainx_perception_2p5d_slots_core slots_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY include/
  DESTINATION include
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()

  ament_add_gtest(test_slot_layout test/test_slot_layout.cpp)
  if(TARGET test_slot_layout)
    target_link_libraries(test_slot_layout brainx_perception_2p5d_slots_core)
    target_include_directories(test_slot_layout PRIVATE include)
  endif()

  ament_add_gtest(test_tri_state_fsm test/test_tri_state_fsm.cpp)
  if(TARGET test_tri_state_fsm)
    target_link_libraries(test_tri_state_fsm brainx_perception_2p5d_slots_core)
    target_include_directories(test_tri_state_fsm PRIVATE include)
  endif()

  ament_add_gtest(test_slot_query test/test_slot_query.cpp)
  if(TARGET test_slot_query)
    target_link_libraries(test_slot_query brainx_perception_2p5d_slots_core)
    target_include_directories(test_slot_query PRIVATE include)
  endif()
endif()

ament_export_include_directories(include)
ament_export_libraries(brainx_perception_2p5d_slots_core)
ament_package()
