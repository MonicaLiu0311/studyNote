cmake_minimum_required (VERSION 3.8)

#这个set的作用与CMakeJson.json中的variable设置BUILD_SHARED_LIBS作用一样，二者取其一
#cmake提供
#set(BUILD_SHARED_LIBS "build dynamic lib" ON)

add_library(export_test "export_test.cpp")

if(BUILD_SHARED_LIBS)
    target_compile_definitions(export_test PUBLIC EXPORT_TEST_DLL PRIVATE BUILD_DLL)
endif()

#指明lz4的位置，也可以用TOOLCHAIN
set(lz4_DIR "E:\\src\\Monica\\vcpkg\\installed\\x86-windows\\share\\lz4")
#set(lz4_DIR "E:\\src\\Monica\\vcpkg\\ports\\lz4")
find_package(lz4 CONFIG REQUIRED)

#这个inclue是源码的include文件，BUILD必须用绝对路径，INSTALL必须用相对路径
target_include_directories(export_test PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/include> $<INSTALL_INTERFACE:include>)
#target_include_directories(export_test PUBLIC include)

target_link_libraries(export_test PUBLIC ws2_32.lib lz4::lz4)

#这个include是安装的include文件,相对路径是CMAKE_INSTALL_PREFIX
#VS中默认${CMAKE_INSTALL_PREFIX}="export_test\out\install\x86-Debug"（debug和release放在不同的位置）
#vcpkg中${CMAKE_INSTALL_PREFIX}=${CURRENT_PACKAGES_DIR}\debug（debug和release放在不同的位置）
install(FILES "include/export_test.h" DESTINATION include)
install(TARGETS export_test
    EXPORT export_testTargets
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)

#手动生成export_test-config.cmake文件
#然后export_test-config.cmake调用export_testTargets.cmake文件
#再由export_testTargets.cmake调用export_testTargets-debug.cmake/export_testTargets-release.cmake
#为什么手动生成export_test-config.cmake文件? 为了把target_link_libraries中的第三方依赖库(lz4)替换成对应的.lib文件
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/export_test-config.cmake" 
[[include(CMakeFindDependencyMacro) 
find_dependency(lz4 CONFIG REQUIRED) 
include("${CMAKE_CURRENT_LIST_DIR}/export_testTargets.cmake")]])

#把手动生成的export_test-config.cmake放到vcpkg指定的share位置
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/export_test-config.cmake" DESTINATION share)

#放在${CMAKE_INSTALL_PREFIX}/share下，这个命令会生成两个.cmake文件，分别是export_testTargets.cmake/export_testTargets-debug.cmake
install(EXPORT export_testTargets DESTINATION share)

message("-----------start printing macro info-----------")
message("CMAKE_CURRENT_SOURCE_DIR:${CMAKE_CURRENT_SOURCE_DIR}")
message("CMAKE_CURRENT_LIST_DIR:${CMAKE_CURRENT_LIST_DIR}")
message("CMAKE_INSTALL_PREFIX:${CMAKE_INSTALL_PREFIX}")
message("CMAKE_CURRENT_BINARY_DIR:${CMAKE_CURRENT_BINARY_DIR}")

message("CMAKE_SYSTEM_PROCESSOR:${CMAKE_SYSTEM_PROCESSOR}")
message("CMAKE_DEBUG_POSTFIX:${CMAKE_DEBUG_POSTFIX}")
message("CMAKE_BUILD_TYPE:${CMAKE_BUILD_TYPE}")
message("VCPKG_TARGET_ARCHITECTURE:${VCPKG_TARGET_ARCHITECTURE}")

message("CURRENT_HOST_INSTALLED_DIR:${CURRENT_HOST_INSTALLED_DIR}")
message("CURRENT_PORT_DIR:${CURRENT_PORT_DIR}")
message("CURRENT_INSTALLED_DIR:${CURRENT_INSTALLED_DIR}")
message("DOWNLOADS:${DOWNLOADS}")