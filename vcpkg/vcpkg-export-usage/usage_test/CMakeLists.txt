cmake_minimum_required (VERSION 3.8)

# Add source to this project's executable.
add_executable (usage_test "usage_test.cpp" "usage_test.h")

#1. 用set指明export_test的config.cmake文件的位置
#2. find_package调用export_test-config.cmake文件，
#export_test-config.cmake文件调用export_testTargets.cmake文件，
#export_testTargets.cmake文件调用export_testTargets-debug.cmake/export_testTargets-release.cmake文件，
#此时，export_test就已经找到了
#3. 将export_test链接到项目的target上
set(export_test_DIR "C:\\Users\\v-liumonica\\source\\repos\\export_test\\out\\install\\x86-Debug\\share")
find_package(export_test CONFIG REQUIRED)
target_link_libraries(usage_test PRIVATE export_test)

# TODO: Add tests and install targets if needed.
install(TARGETS usage_test
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)