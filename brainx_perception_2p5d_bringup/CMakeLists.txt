cmake_minimum_required(VERSION 3.8)
project(brainx_perception_2p5d_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)

install(
  DIRECTORY launch config rviz
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
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

  add_test(
    NAME bringup_smoke_test
    COMMAND /bin/bash -lc
            "source ${CMAKE_CURRENT_SOURCE_DIR}/../install/setup.bash && ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test/test_smoke.py"
  )
  set_tests_properties(bringup_smoke_test PROPERTIES TIMEOUT 40)
endif()

ament_package()
