cmake_minimum_required(VERSION 3.8)
project(brainx_perception_2p5d_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)

ament_python_install_package(${PROJECT_NAME})

install(
  DIRECTORY launch config rviz
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/generate_synthetic_bag.py
    scripts/synthetic_depth_publisher.py
  DESTINATION lib/${PROJECT_NAME}
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
  set(ament_cmake_flake8_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()

  get_filename_component(WORKSPACE_ROOT "${CMAKE_CURRENT_BINARY_DIR}/../.." ABSOLUTE)
  set(WORKSPACE_SETUP "${WORKSPACE_ROOT}/install/setup.bash")

  add_test(
    NAME bringup_synthetic_scenarios_test
    COMMAND /bin/bash -lc
            "source ${WORKSPACE_SETUP} && ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test/test_smoke.py"
  )
  set_tests_properties(bringup_synthetic_scenarios_test PROPERTIES TIMEOUT 70)

  add_test(
    NAME bringup_replay_equivalence_test
    COMMAND /bin/bash -lc
            "source ${WORKSPACE_SETUP} && ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test/test_replay_equivalence.py"
  )
  set_tests_properties(bringup_replay_equivalence_test PROPERTIES TIMEOUT 180)
endif()

ament_package()
