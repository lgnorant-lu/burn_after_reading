#!/usr/bin/env python3
"""
端到端测试脚本 - Burn After Reading
测试整个应用的核心功能，包括文本消息、文件上传、密码保护、过期机制等
"""

import requests
import json
import time
import os
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass
import tempfile
import uuid

# 配置
BACKEND_URL = "http://127.0.0.1:8001"
FRONTEND_URL = "http://localhost:3002"

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None

class E2ETestSuite:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        
    def log(self, message: str, level: str = "INFO"):
        """记录测试日志"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def assert_test(self, condition: bool, test_name: str, message: str, details: Dict[str, Any] = None):
        """断言测试结果"""
        result = TestResult(test_name, condition, message, details)
        self.results.append(result)
        
        status = "✅ PASS" if condition else "❌ FAIL"
        self.log(f"{status} - {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                self.log(f"  {key}: {value}", "DEBUG")
                
        return condition
    
    def test_backend_health(self) -> bool:
        """测试后端健康检查"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            return self.assert_test(
                response.status_code == 200 and response.json().get("status") == "healthy",
                "Backend Health Check",
                f"Backend responded with status {response.status_code}",
                {"response": response.json() if response.status_code == 200 else None}
            )
        except Exception as e:
            return self.assert_test(
                False, "Backend Health Check", f"Failed to connect: {str(e)}"
            )
    
    def test_create_text_note_simple(self) -> Optional[str]:
        """测试创建简单文本消息（无密码，阅后即焚）"""
        try:
            payload = {
                "content": "这是一条测试消息 - 阅后即焚",
                "expiration_type": "read_once"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/create",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                note_id = data.get("id")
                
                success = self.assert_test(
                    note_id is not None and data.get("content") == payload["content"],
                    "Create Simple Text Note",
                    f"Successfully created note with ID: {note_id}",
                    {"note_id": note_id, "expiration": data.get("expiration_type")}
                )
                return note_id if success else None
            else:
                self.assert_test(
                    False, "Create Simple Text Note", 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.assert_test(
                False, "Create Simple Text Note", f"Exception: {str(e)}"
            )
            return None
    
    def test_create_text_note_with_password(self) -> Optional[Dict[str, str]]:
        """测试创建有密码保护的文本消息"""
        try:
            payload = {
                "content": "这是一条受密码保护的测试消息",
                "password": "test123",
                "expiration_type": "hours_24"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/create",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                note_id = data.get("id")
                
                success = self.assert_test(
                    note_id is not None and data.get("has_password") is True,
                    "Create Password-Protected Text Note",
                    f"Successfully created protected note with ID: {note_id}",
                    {"note_id": note_id, "has_password": data.get("has_password")}
                )
                return {"note_id": note_id, "password": "test123"} if success else None
            else:
                self.assert_test(
                    False, "Create Password-Protected Text Note", 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.assert_test(
                False, "Create Password-Protected Text Note", f"Exception: {str(e)}"
            )
            return None
    
    def test_upload_file(self) -> Optional[Dict[str, str]]:
        """测试文件上传功能"""
        try:
            # 创建一个临时测试文件
            test_content = "这是一个测试文件的内容\n包含多行\n用于测试文件上传功能"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(test_content)
                temp_file_path = f.name
            
            try:
                with open(temp_file_path, 'rb') as file:
                    files = {'file': ('test_file.txt', file, 'text/plain')}
                    data = {
                        'expiration_type': 'hours_1',
                        'password': 'file123'
                    }
                    
                    response = self.session.post(
                        f"{BACKEND_URL}/upload",
                        files=files,
                        data=data,
                        timeout=15
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    note_id = data.get("id")
                    
                    success = self.assert_test(
                        note_id is not None and data.get("filename") == "test_file.txt",
                        "Upload File with Password",
                        f"Successfully uploaded file with ID: {note_id}",
                        {
                            "note_id": note_id, 
                            "filename": data.get("filename"),
                            "file_size": data.get("file_size"),
                            "content_type": data.get("content_type")
                        }
                    )
                    return {"note_id": note_id, "password": "file123", "content": test_content} if success else None
                else:
                    self.assert_test(
                        False, "Upload File with Password", 
                        f"Failed with status {response.status_code}: {response.text}"
                    )
                    return None
                    
            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.assert_test(
                False, "Upload File with Password", f"Exception: {str(e)}"
            )
            return None
    
    def test_get_note_info(self, note_id: str) -> bool:
        """测试获取笔记信息（非破坏性）"""
        try:
            response = self.session.get(f"{BACKEND_URL}/note/{note_id}/info", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self.assert_test(
                    "has_password" in data and "expiration_type" in data,
                    "Get Note Info",
                    f"Successfully retrieved note info for {note_id}",
                    {"info": data}
                )
            else:
                return self.assert_test(
                    False, "Get Note Info", 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return self.assert_test(
                False, "Get Note Info", f"Exception: {str(e)}"
            )
    
    def test_access_text_note(self, note_id: str, password: Optional[str] = None) -> bool:
        """测试访问文本笔记（破坏性）"""
        try:
            payload = {}
            if password:
                payload["password"] = password
                
            response = self.session.post(
                f"{BACKEND_URL}/note/{note_id}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self.assert_test(
                    "content" in data,
                    "Access Text Note",
                    f"Successfully accessed text note {note_id}",
                    {"content_preview": data.get("content", "")[:50] + "..."}
                )
            else:
                return self.assert_test(
                    False, "Access Text Note", 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return self.assert_test(
                False, "Access Text Note", f"Exception: {str(e)}"
            )
    
    def test_download_file(self, note_id: str, password: Optional[str] = None, expected_content: str = None) -> bool:
        """测试文件下载（破坏性）"""
        try:
            payload = {}
            if password:
                payload["password"] = password
                
            response = self.session.post(
                f"{BACKEND_URL}/note/{note_id}/download",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                # 检查是否是文件下载响应
                content_disposition = response.headers.get('Content-Disposition', '')
                downloaded_content = response.content.decode('utf-8')
                
                content_matches = True
                if expected_content:
                    # 规范化换行符处理Windows/Unix差异
                    normalized_downloaded = downloaded_content.replace('\r\n', '\n').replace('\r', '\n').strip()
                    normalized_expected = expected_content.replace('\r\n', '\n').replace('\r', '\n').strip()
                    content_matches = normalized_downloaded == normalized_expected
                
                return self.assert_test(
                    'attachment' in content_disposition and content_matches,
                    "Download File",
                    f"Successfully downloaded file {note_id}",
                    {
                        "content_disposition": content_disposition,
                        "file_size": len(response.content),
                        "content_matches": content_matches
                    }
                )
            else:
                return self.assert_test(
                    False, "Download File", 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return self.assert_test(
                False, "Download File", f"Exception: {str(e)}"
            )
    
    def test_note_destroyed_after_access(self, note_id: str) -> bool:
        """测试笔记在访问后是否被销毁"""
        try:
            # 尝试再次访问应该返回404
            response = self.session.get(f"{BACKEND_URL}/note/{note_id}/info", timeout=10)
            
            return self.assert_test(
                response.status_code == 404,
                "Note Destruction Verification",
                f"Note {note_id} correctly destroyed after access",
                {"status_code": response.status_code}
            )
                
        except Exception as e:
            return self.assert_test(
                False, "Note Destruction Verification", f"Exception: {str(e)}"
            )
    
    def test_wrong_password(self, note_id: str) -> bool:
        """测试错误密码访问"""
        try:
            payload = {"password": "wrong_password"}
                
            response = self.session.post(
                f"{BACKEND_URL}/note/{note_id}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            return self.assert_test(
                response.status_code in [401, 403, 404],  # 可能返回不同的错误代码
                "Wrong Password Test",
                f"Correctly rejected wrong password for note {note_id}",
                {"status_code": response.status_code}
            )
                
        except Exception as e:
            return self.assert_test(
                False, "Wrong Password Test", f"Exception: {str(e)}"
            )
    
    def test_expiration_types(self) -> bool:
        """测试不同的过期类型"""
        expiration_types = ["read_once", "hours_1", "hours_24", "days_7"]
        success_count = 0
        
        for exp_type in expiration_types:
            try:
                payload = {
                    "content": f"测试消息 - 过期类型: {exp_type}",
                    "expiration_type": exp_type
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/create",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("expiration_type") == exp_type:
                        success_count += 1
                        self.log(f"✅ Expiration type {exp_type} works correctly")
                    else:
                        self.log(f"❌ Expiration type {exp_type} failed - wrong type returned")
                else:
                    self.log(f"❌ Expiration type {exp_type} failed - status {response.status_code}")
                    
            except Exception as e:
                self.log(f"❌ Expiration type {exp_type} failed - exception: {str(e)}")
        
        return self.assert_test(
            success_count == len(expiration_types),
            "Expiration Types Test",
            f"Successfully tested {success_count}/{len(expiration_types)} expiration types",
            {"successful_types": success_count, "total_types": len(expiration_types)}
        )
    
    def run_full_test_suite(self):
        """运行完整的测试套件"""
        self.log("🚀 开始端到端测试", "INFO")
        self.log("=" * 60)
        
        # 1. 基础连接测试
        self.log("📡 测试后端连接...")
        if not self.test_backend_health():
            self.log("❌ 后端连接失败，终止测试", "ERROR")
            return False
        
        # 2. 创建简单文本消息并测试访问
        self.log("📝 测试简单文本消息...")
        simple_note_id = self.test_create_text_note_simple()
        if simple_note_id:
            self.test_get_note_info(simple_note_id)
            self.test_access_text_note(simple_note_id)
            self.test_note_destroyed_after_access(simple_note_id)
        
        # 3. 创建受密码保护的文本消息
        self.log("🔒 测试密码保护的文本消息...")
        protected_note = self.test_create_text_note_with_password()
        if protected_note:
            # 测试错误密码
            self.test_wrong_password(protected_note["note_id"])
            # 测试正确密码
            self.test_access_text_note(protected_note["note_id"], protected_note["password"])
            self.test_note_destroyed_after_access(protected_note["note_id"])
        
        # 4. 测试文件上传
        self.log("📎 测试文件上传功能...")
        file_note = self.test_upload_file()
        if file_note:
            self.test_get_note_info(file_note["note_id"])
            self.test_download_file(file_note["note_id"], file_note["password"], file_note["content"])
            self.test_note_destroyed_after_access(file_note["note_id"])
        
        # 5. 测试不同过期类型
        self.log("⏰ 测试过期类型...")
        self.test_expiration_types()
        
        # 6. 生成测试报告
        self.generate_test_report()
        
        return True
    
    def generate_test_report(self):
        """生成测试报告"""
        self.log("=" * 60)
        self.log("📊 测试报告", "INFO")
        self.log("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"总测试数: {total_tests}")
        self.log(f"通过: {passed_tests} ✅")
        self.log(f"失败: {failed_tests} ❌")
        self.log(f"成功率: {success_rate:.1f}%")
        
        if failed_tests > 0:
            self.log("\n失败的测试:")
            for result in self.results:
                if not result.passed:
                    self.log(f"❌ {result.name}: {result.message}", "ERROR")
        
        self.log("=" * 60)
        
        if success_rate >= 90:
            self.log("🎉 测试结果：优秀！应用程序运行良好。", "INFO")
        elif success_rate >= 75:
            self.log("✅ 测试结果：良好，有一些需要改进的地方。", "INFO")
        else:
            self.log("⚠️ 测试结果：需要关注，存在多个问题。", "ERROR")

def main():
    """主函数"""
    print("🔥 Burn After Reading - 端到端测试")
    print("=" * 60)
    
    # 检查依赖
    try:
        import requests
    except ImportError:
        print("❌ 缺少 requests 库，请运行: pip install requests")
        sys.exit(1)
    
    # 运行测试
    test_suite = E2ETestSuite()
    test_suite.run_full_test_suite()

if __name__ == "__main__":
    main() 