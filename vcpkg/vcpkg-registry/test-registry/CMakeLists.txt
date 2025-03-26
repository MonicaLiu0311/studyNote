cmake_minimum_required(VERSION 3.18)
set(CMAKE_TOOLCHAIN_FILE "E:/vcpkg/scripts/buildsystems/vcpkg.cmake")

project(test CXX)
add_executable(main main.cpp)

find_package(beicode CONFIG REQUIRED)
target_link_libraries(main PRIVATE beicode::beicode)

find_package(beison CONFIG REQUIRED)
target_link_libraries(main PRIVATE beison::beison)

find_package(fmt CONFIG REQUIRED)
target_link_libraries(main PRIVATE fmt::fmt)