# CMake/CTest 集成模式

## 概述

本文件定义 Stage 4 测试代码生成时的 CMake 配置模板和 Stage 5 的构建验证流程。

## 项目结构

已有项目典型结构:
```
project/
├── CMakeLists.txt          # 主 CMakeLists
├── src/                    # 源码
│   ├── CMakeLists.txt
│   ├── calculator.cpp
│   └── calculator.h
├── tests/                  # 测试 (本 Skill 生成/追加)
│   ├── CMakeLists.txt      # 测试模块 CMake
│   ├── test_calculator.cpp
│   └── test_calculator.h
└── build/                  # 构建目录 (不提交)
```

新项目脚手架结构:
```
project/
├── CMakeLists.txt          # 主 CMakeLists (含 enable_testing())
├── src/
│   ├── CMakeLists.txt
│   └── <源文件>
├── tests/
│   ├── CMakeLists.txt
│   └── <测试文件>
└── README.md
```

## 主 CMakeLists.txt 集成

### 已有项目追加测试

在主 CMakeLists.txt 末尾追加:

```cmake
# 单元测试
enable_testing()
option(BUILD_TESTING "Build unit tests" ON)
if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
```

### 新项目脚手架

```cmake
cmake_minimum_required(VERSION 3.16)
project(<project_name> LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt5 COMPONENTS Core Test REQUIRED)

# 源码库
add_subdirectory(src)

# 测试
enable_testing()
option(BUILD_TESTING "Build unit tests" ON)
if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
```

## 测试模块 CMakeLists.txt 模板

```cmake
# tests/CMakeLists.txt

find_package(Qt5Test REQUIRED)

# --- test_<target_name> ---
add_executable(test_<target_name>
    test_<target_name>.cpp
)

# AUTOMOC: 自动处理 Q_OBJECT
set_target_properties(test_<target_name> PROPERTIES
    AUTOMOC ON
)

# 链接被测库 + Qt Test
target_link_libraries(test_<target_name>
    PRIVATE
    <library_target>        # 被测目标
    Qt5::Test
)

# include 被测头文件目录
target_include_directories(test_<target_name> PRIVATE
    ${CMAKE_SOURCE_DIR}/src
)

# 注册 CTest
add_test(NAME test_<target_name> COMMAND test_<target_name>)

# 覆盖率 (可选)
if(ENABLE_COVERAGE)
    target_compile_options(test_<target_name> PRIVATE
        -fprofile-arcs -ftest-coverage
    )
    target_link_libraries(test_<target_name>
        -fprofile-arcs -ftest-coverage
    )
endif()
```

## 多测试模块集成

当有多个测试类时:

```cmake
# tests/CMakeLists.txt

find_package(Qt5Test REQUIRED)

# 测试列表
set(TEST_TARGETS
    test_calculator
    test_parser
    test_model
)

foreach(test_target ${TEST_TARGETS})
    add_executable(${test_target} ${test_target}.cpp)
    set_target_properties(${test_target} PROPERTIES AUTOMOC ON)
    target_link_libraries(${test_target}
        PRIVATE
        <library_target>
        Qt5::Test
    )
    target_include_directories(${test_target} PRIVATE
        ${CMAKE_SOURCE_DIR}/src
    )
    add_test(NAME ${test_target} COMMAND ${test_target})

    if(ENABLE_COVERAGE)
        target_compile_options(${test_target} PRIVATE
            -fprofile-arcs -ftest-coverage
        )
    endif()
endforeach()
```

## 覆盖率配置

### 编译参数

```cmake
if(ENABLE_COVERAGE)
    # 全局覆盖率编译参数
    add_compile_options(-fprofile-arcs -ftest-coverage)
    add_link_options(-fprofile-arcs -ftest-coverage)
endif()
```

### 构建命令

```bash
# 带覆盖率的构建
cmake .. -DENABLE_COVERAGE=ON
make

# 运行测试 (生成 .gcda 文件)
QT_QPA_PLATFORM=offscreen ctest --output-on-failure

# 生成覆盖率报告
lcov --capture --directory . --output-file coverage.info
lcov --remove coverage.info '/usr/*' --output-file coverage.filtered.info
genhtml coverage.filtered.info --output-directory coverage_report
```

## Qt6 兼容

模板自动适配 Qt5/Qt6:

```cmake
# 检测 Qt 版本
find_package(Qt5 COMPONENTS Core Test QUIET)
if(Qt5_FOUND)
    set(QT_VERSION "Qt5")
    set(QT_TEST_LIB Qt5::Test)
else()
    find_package(Qt6 COMPONENTS Core Test REQUIRED)
    set(QT_VERSION "Qt6")
    set(QT_TEST_LIB Qt6::Test)
endif()

target_link_libraries(test_target PRIVATE <lib> ${QT_TEST_LIB})
```

## 构建验证流程 (Stage 5)

```bash
# 1. 配置
cd build && cmake .. -DBUILD_TESTING=ON -DENABLE_COVERAGE=ON

# 2. 编译
make -j$(nproc)

# 3. 运行测试
QT_QPA_PLATFORM=offscreen ctest --output-on-failure

# 4. 覆盖率
lcov --capture --directory . --output-file coverage.info
lcov --remove coverage.info '/usr/*' '*/tests/*' --output-file coverage.filtered.info
genhtml coverage.filtered.info --output-directory coverage_report

# 5. 解析覆盖率 (脚本完成)
python3 scripts/validate_coverage.py --build-dir . --state state.json
```
