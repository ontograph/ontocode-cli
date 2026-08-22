cmake_minimum_required(VERSION 3.16)
project(CalculatorExample LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt5 COMPONENTS Core Test REQUIRED)

option(ENABLE_COVERAGE "Enable code coverage" OFF)

# 被测库
add_library(calculator_lib STATIC
    src/calculator.cpp
)
target_include_directories(calculator_lib PUBLIC src)
target_link_libraries(calculator_lib PUBLIC Qt5::Core)

if(ENABLE_COVERAGE)
    target_compile_options(calculator_lib PUBLIC -fprofile-arcs -ftest-coverage)
    target_link_libraries(calculator_lib PUBLIC gcov)
endif()

# 测试
enable_testing()
option(BUILD_TESTING "Build unit tests" ON)
if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
