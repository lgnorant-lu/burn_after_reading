#!/usr/bin/env python
"""
---------------------------------------------------------------
File name:          test_phase2_api.py
Author:             Ignorant-lu
Date created:       2025/06/11
Last modified:      2025/06/11
Python Version:     3.x
Description:        Comprehensive test script for Phase 2 features
                    Tests password protection, expiration, and file uploads
---------------------------------------------------------------
"""

import requests
import json
import io
import time
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8001"
TEST_FILES_DIR = Path("test_files")

def setup_test_files():
    """创建测试文件目录和测试文件"""
    TEST_FILES_DIR.mkdir(exist_ok=True)
    
    # 创建测试文本文件
    test_txt = TEST_FILES_DIR / "test.txt"
    test_txt.write_text("这是一个测试文件\nHello World!\n", encoding='utf-8')
    
    # 创建测试JSON文件
    test_json = TEST_FILES_DIR / "test.json"
    test_json.write_text(json.dumps({"message": "test data", "number": 42}, indent=2))
    
    print(f"✅ 测试文件已创建在 {TEST_FILES_DIR}")

def test_health_check():
    """测试健康检查端点"""
    print("\n🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200
    assert "version" in response.json()
    print("✅ 健康检查通过")

def test_basic_text_note():
    """测试基本文本笔记功能"""
    print("\n📝 测试基本文本笔记...")
    
    # 创建文本笔记
    note_data = {
        "content": "这是一个基本的测试笔记",
        "expiration_type": "read_once"
    }
    
    response = requests.post(f"{BASE_URL}/create", json=note_data)
    print(f"创建状态码: {response.status_code}")
    print(f"创建响应: {response.json()}")
    
    assert response.status_code == 200
    note_id = response.json()["id"]
    assert response.json()["has_password"] == False
    
    # 读取笔记
    access_data = {"password": None}
    read_response = requests.post(f"{BASE_URL}/note/{note_id}", json=access_data)
    print(f"读取状态码: {read_response.status_code}")
    print(f"读取响应: {read_response.json()}")
    
    assert read_response.status_code == 200
    assert read_response.json()["content"] == note_data["content"]
    
    # 再次尝试读取（应该失败）
    second_read = requests.post(f"{BASE_URL}/note/{note_id}", json=access_data)
    print(f"二次读取状态码: {second_read.status_code}")
    assert second_read.status_code == 404
    
    print("✅ 基本文本笔记测试通过")

def test_password_protected_note():
    """测试密码保护笔记"""
    print("\n🔐 测试密码保护笔记...")
    
    # 创建密码保护笔记
    note_data = {
        "content": "这是一个密码保护的测试笔记",
        "password": "test123",
        "expiration_type": "read_once"
    }
    
    response = requests.post(f"{BASE_URL}/create", json=note_data)
    print(f"创建状态码: {response.status_code}")
    assert response.status_code == 200
    
    note_id = response.json()["id"]
    assert response.json()["has_password"] == True
    
    # 尝试无密码访问（应该失败）
    no_password = requests.post(f"{BASE_URL}/note/{note_id}", json={"password": None})
    print(f"无密码访问状态码: {no_password.status_code}")
    assert no_password.status_code == 401
    
    # 尝试错误密码（应该失败）
    wrong_password = requests.post(f"{BASE_URL}/note/{note_id}", json={"password": "wrong"})
    print(f"错误密码状态码: {wrong_password.status_code}")
    assert wrong_password.status_code == 401
    
    # 正确密码访问
    correct_access = requests.post(f"{BASE_URL}/note/{note_id}", json={"password": "test123"})
    print(f"正确密码状态码: {correct_access.status_code}")
    print(f"正确密码响应: {correct_access.json()}")
    assert correct_access.status_code == 200
    assert correct_access.json()["content"] == note_data["content"]
    
    print("✅ 密码保护笔记测试通过")

def test_expiration_types():
    """测试不同过期类型"""
    print("\n⏰ 测试过期类型...")
    
    # 测试1小时过期
    note_data = {
        "content": "1小时后过期的笔记",
        "expiration_type": "hours_1"
    }
    
    response = requests.post(f"{BASE_URL}/create", json=note_data)
    assert response.status_code == 200
    note_info = response.json()
    
    print(f"1小时过期笔记ID: {note_info['id']}")
    print(f"过期时间: {note_info['expires_at']}")
    assert note_info["expiration_type"] == "hours_1"
    assert note_info["expires_at"] is not None
    
    # 测试24小时过期
    note_data_24h = {
        "content": "24小时后过期的笔记",
        "expiration_type": "hours_24"
    }
    
    response_24h = requests.post(f"{BASE_URL}/create", json=note_data_24h)
    assert response_24h.status_code == 200
    note_info_24h = response_24h.json()
    
    print(f"24小时过期笔记ID: {note_info_24h['id']}")
    print(f"过期时间: {note_info_24h['expires_at']}")
    assert note_info_24h["expiration_type"] == "hours_24"
    
    print("✅ 过期类型测试通过")

def test_file_upload():
    """测试文件上传功能"""
    print("\n📁 测试文件上传...")
    
    setup_test_files()
    
    # 上传文本文件
    test_file = TEST_FILES_DIR / "test.txt"
    
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'text/plain')}
        data = {
            'password': 'file123',
            'expiration_type': 'read_once'
        }
        
        response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        print(f"上传状态码: {response.status_code}")
        print(f"上传响应: {response.json()}")
        
        assert response.status_code == 200
        file_note = response.json()
        assert file_note["filename"] == test_file.name
        assert file_note["has_password"] == True
        assert "file_size" in file_note
        
        file_id = file_note["id"]
    
    # 下载文件
    download_data = {"password": "file123"}
    download_response = requests.post(f"{BASE_URL}/note/{file_id}/download", json=download_data)
    
    print(f"下载状态码: {download_response.status_code}")
    assert download_response.status_code == 200
    
    # 验证文件内容
    downloaded_content = download_response.content
    original_content = test_file.read_bytes()
    assert downloaded_content == original_content
    
    print("✅ 文件上传下载测试通过")

def test_note_info_endpoint():
    """测试笔记信息端点"""
    print("\n ℹ️ 测试笔记信息端点...")
    
    # 创建测试笔记
    note_data = {
        "content": "信息查询测试笔记",
        "password": "info123",
        "expiration_type": "hours_1"
    }
    
    response = requests.post(f"{BASE_URL}/create", json=note_data)
    note_id = response.json()["id"]
    
    # 获取笔记信息
    info_response = requests.get(f"{BASE_URL}/note/{note_id}/info")
    print(f"信息查询状态码: {info_response.status_code}")
    
    if info_response.status_code == 200:
        print(f"信息查询响应: {info_response.json()}")
    else:
        print(f"错误详情: {info_response.text}")
        
    assert info_response.status_code == 200
    info = info_response.json()
    assert info["has_password"] == True
    assert info["expiration_type"] == "hours_1"
    assert info["content"] == note_data["content"]  # 信息查询不删除内容
    
    # 验证笔记仍然存在（信息查询不删除）
    access_response = requests.post(f"{BASE_URL}/note/{note_id}", json={"password": "info123"})
    assert access_response.status_code == 200
    
    print("✅ 笔记信息端点测试通过")

def test_legacy_compatibility():
    """测试向后兼容性"""
    print("\n🔄 测试向后兼容性...")
    
    # 创建无密码笔记
    note_data = {
        "content": "向后兼容性测试笔记",
        "expiration_type": "read_once"
    }
    
    response = requests.post(f"{BASE_URL}/create", json=note_data)
    note_id = response.json()["id"]
    
    # 使用旧的GET端点
    legacy_response = requests.get(f"{BASE_URL}/note/{note_id}")
    print(f"旧端点状态码: {legacy_response.status_code}")
    print(f"旧端点响应: {legacy_response.json()}")
    
    assert legacy_response.status_code == 200
    assert legacy_response.json()["content"] == note_data["content"]
    
    print("✅ 向后兼容性测试通过")

def test_error_scenarios():
    """测试错误场景"""
    print("\n❌ 测试错误场景...")
    
    # 测试不存在的笔记
    fake_id = "00000000-0000-0000-0000-000000000000"
    fake_response = requests.post(f"{BASE_URL}/note/{fake_id}", json={"password": None})
    assert fake_response.status_code == 404
    
    # 测试空内容笔记
    empty_note = {"content": "", "expiration_type": "read_once"}
    empty_response = requests.post(f"{BASE_URL}/create", json=empty_note)
    assert empty_response.status_code == 400
    
    # 测试文件大小限制（创建5MB+的测试文件）
    large_file_path = TEST_FILES_DIR / "large_test.bin"
    with open(large_file_path, 'wb') as f:
        f.write(b'x' * (6 * 1024 * 1024))  # 6MB文件
    
    with open(large_file_path, 'rb') as f:
        files = {'file': ('large_test.bin', f, 'application/octet-stream')}
        data = {'expiration_type': 'read_once'}
        
        large_response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        print(f"大文件上传状态码: {large_response.status_code}")
        assert large_response.status_code == 413  # Payload Too Large
    
    # 清理大文件
    large_file_path.unlink()
    
    print("✅ 错误场景测试通过")

def cleanup_test_files():
    """清理测试文件"""
    import shutil
    if TEST_FILES_DIR.exists():
        shutil.rmtree(TEST_FILES_DIR)
        print(f"✅ 已清理测试文件目录 {TEST_FILES_DIR}")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始Phase 2 API全面测试...")
    print("=" * 50)
    
    try:
        test_health_check()
        test_basic_text_note()
        test_password_protected_note()
        test_expiration_types()
        test_file_upload()
        test_note_info_endpoint()
        test_legacy_compatibility()
        test_error_scenarios()
        
        print("\n" + "=" * 50)
        print("🎉 所有Phase 2测试全部通过！")
        print("✅ 密码保护功能正常")
        print("✅ 过期设置功能正常")
        print("✅ 文件上传下载功能正常")
        print("✅ 向后兼容性保持良好")
        print("✅ 错误处理机制正常")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        raise
    finally:
        cleanup_test_files()

if __name__ == "__main__":
    print("Phase 2 API 测试脚本")
    print("确保服务器运行在 http://127.0.0.1:8000")
    print("启动服务器: uv run uvicorn src.main:app --reload")
    print("")
    
    input("按 Enter 键开始测试...")
    run_all_tests() 