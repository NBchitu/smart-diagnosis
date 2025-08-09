"""
SSL 检查 API
支持 macOS 和树莓派 5 系统
"""

import ssl
import socket
import time
import datetime
import hashlib
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
import subprocess
import re

router = APIRouter()

class SSLCheckRequest(BaseModel):
    hostname: str
    port: int = 443
    check_chain: bool = True

class SSLCertificate(BaseModel):
    subject: str
    issuer: str
    serial_number: str
    not_before: str
    not_after: str
    signature_algorithm: str
    public_key_algorithm: str
    key_size: int
    fingerprint_sha1: str
    fingerprint_sha256: str
    san_domains: Optional[List[str]] = None

class SSLCheckResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    details: Optional[str] = None

def parse_certificate(cert_der: bytes) -> Dict[str, Any]:
    """解析证书信息"""
    try:
        # 使用 OpenSSL 解析证书（如果可用）
        return parse_certificate_with_openssl(cert_der)
    except:
        # 备用方案：使用 Python ssl 模块
        return parse_certificate_with_ssl(cert_der)

def parse_certificate_with_openssl(cert_der: bytes) -> Dict[str, Any]:
    """使用 OpenSSL 命令解析证书"""
    try:
        # 将 DER 格式转换为 PEM 格式
        import base64
        cert_pem = "-----BEGIN CERTIFICATE-----\n"
        cert_pem += base64.b64encode(cert_der).decode('ascii')
        cert_pem = '\n'.join([cert_pem[i:i+64] for i in range(0, len(cert_pem), 64)])
        cert_pem += "\n-----END CERTIFICATE-----"
        
        # 使用 openssl 命令解析
        process = subprocess.run(
            ['openssl', 'x509', '-text', '-noout'],
            input=cert_pem.encode(),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if process.returncode != 0:
            raise Exception("OpenSSL 解析失败")
        
        output = process.stdout
        
        # 解析输出
        cert_info = {}
        
        # 提取主题
        subject_match = re.search(r'Subject: (.+)', output)
        cert_info['subject'] = subject_match.group(1) if subject_match else "Unknown"
        
        # 提取颁发者
        issuer_match = re.search(r'Issuer: (.+)', output)
        cert_info['issuer'] = issuer_match.group(1) if issuer_match else "Unknown"
        
        # 提取序列号
        serial_match = re.search(r'Serial Number:\s*([a-fA-F0-9:]+)', output)
        cert_info['serial_number'] = serial_match.group(1) if serial_match else "Unknown"
        
        # 提取有效期
        not_before_match = re.search(r'Not Before: (.+)', output)
        not_after_match = re.search(r'Not After : (.+)', output)
        cert_info['not_before'] = not_before_match.group(1) if not_before_match else "Unknown"
        cert_info['not_after'] = not_after_match.group(1) if not_after_match else "Unknown"
        
        # 提取签名算法
        sig_alg_match = re.search(r'Signature Algorithm: (.+)', output)
        cert_info['signature_algorithm'] = sig_alg_match.group(1) if sig_alg_match else "Unknown"
        
        # 提取公钥信息
        pubkey_match = re.search(r'Public Key Algorithm: (.+)', output)
        cert_info['public_key_algorithm'] = pubkey_match.group(1) if pubkey_match else "Unknown"
        
        # 提取密钥长度
        key_size_match = re.search(r'Public-Key: \((\d+) bit\)', output)
        cert_info['key_size'] = int(key_size_match.group(1)) if key_size_match else 0
        
        # 提取 SAN 域名
        san_match = re.search(r'X509v3 Subject Alternative Name:\s*\n\s*(.+)', output)
        if san_match:
            san_text = san_match.group(1)
            san_domains = re.findall(r'DNS:([^,\s]+)', san_text)
            cert_info['san_domains'] = san_domains
        
        # 计算指纹
        cert_info['fingerprint_sha1'] = hashlib.sha1(cert_der).hexdigest().upper()
        cert_info['fingerprint_sha256'] = hashlib.sha256(cert_der).hexdigest().upper()
        
        return cert_info
        
    except Exception as e:
        raise Exception(f"OpenSSL 证书解析失败: {e}")

def parse_certificate_with_ssl(cert_der: bytes) -> Dict[str, Any]:
    """使用 Python ssl 模块解析证书（备用方案）"""
    try:
        print("    使用 Python SSL 模块解析证书")

        # 尝试使用 cryptography 库（如果可用）
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend

            cert = x509.load_der_x509_certificate(cert_der, default_backend())

            # 提取基本信息
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            serial_number = str(cert.serial_number)
            not_before = cert.not_valid_before.strftime('%b %d %H:%M:%S %Y %Z')
            not_after = cert.not_valid_after.strftime('%b %d %H:%M:%S %Y %Z')

            # 提取公钥信息
            public_key = cert.public_key()
            if hasattr(public_key, 'key_size'):
                key_size = public_key.key_size
                public_key_algorithm = type(public_key).__name__
            else:
                key_size = 0
                public_key_algorithm = "Unknown"

            # 提取 SAN 域名
            san_domains = []
            try:
                san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                san_domains = [name.value for name in san_ext.value]
            except:
                pass

            cert_info = {
                'subject': subject,
                'issuer': issuer,
                'serial_number': serial_number,
                'not_before': not_before,
                'not_after': not_after,
                'signature_algorithm': cert.signature_algorithm_oid._name,
                'public_key_algorithm': public_key_algorithm,
                'key_size': key_size,
                'fingerprint_sha1': hashlib.sha1(cert_der).hexdigest().upper(),
                'fingerprint_sha256': hashlib.sha256(cert_der).hexdigest().upper(),
                'san_domains': san_domains
            }

            print("    ✅ 使用 cryptography 库解析成功")
            return cert_info

        except ImportError:
            print("    cryptography 库不可用，使用基础解析")
            pass

        # 基础的证书信息（如果 cryptography 不可用）
        cert_info = {
            'subject': "Certificate Subject (Basic parsing)",
            'issuer': "Certificate Issuer (Basic parsing)",
            'serial_number': "Unknown",
            'not_before': "Unknown",
            'not_after': "Unknown",
            'signature_algorithm': "Unknown",
            'public_key_algorithm': "Unknown",
            'key_size': 2048,  # 假设值
            'fingerprint_sha1': hashlib.sha1(cert_der).hexdigest().upper(),
            'fingerprint_sha256': hashlib.sha256(cert_der).hexdigest().upper(),
            'san_domains': []
        }

        print("    ⚠️ 使用基础证书解析")
        return cert_info

    except Exception as e:
        raise Exception(f"SSL 模块证书解析失败: {e}")

def analyze_ssl_security(cert_info: Dict[str, Any], ssl_version: str, cipher: str) -> Dict[str, Any]:
    """分析 SSL 安全性"""
    analysis = {
        'is_valid': True,
        'is_expired': False,
        'days_until_expiry': 0,
        'is_self_signed': False,
        'has_weak_signature': False,
        'supports_sni': True,
        'vulnerabilities': [],
        'security_grade': 'A'
    }
    
    try:
        # 检查证书有效期
        not_after_str = cert_info.get('not_after', '')
        if not_after_str and not_after_str != "Unknown":
            try:
                # 尝试解析日期
                not_after = datetime.datetime.strptime(not_after_str.strip(), '%b %d %H:%M:%S %Y %Z')
                now = datetime.datetime.now()
                
                if not_after < now:
                    analysis['is_expired'] = True
                    analysis['is_valid'] = False
                    analysis['vulnerabilities'].append('证书已过期')
                    analysis['security_grade'] = 'F'
                else:
                    days_left = (not_after - now).days
                    analysis['days_until_expiry'] = days_left
                    
                    if days_left < 30:
                        analysis['vulnerabilities'].append('证书即将过期（少于30天）')
                        if analysis['security_grade'] == 'A':
                            analysis['security_grade'] = 'B'
                            
            except ValueError:
                analysis['vulnerabilities'].append('无法解析证书有效期')
        
        # 检查自签名
        subject = cert_info.get('subject', '')
        issuer = cert_info.get('issuer', '')
        if subject == issuer and subject != "Unknown":
            analysis['is_self_signed'] = True
            analysis['vulnerabilities'].append('自签名证书')
            if analysis['security_grade'] in ['A', 'B']:
                analysis['security_grade'] = 'C'
        
        # 检查签名算法
        sig_alg = cert_info.get('signature_algorithm', '').lower()
        if 'md5' in sig_alg or 'sha1' in sig_alg:
            analysis['has_weak_signature'] = True
            analysis['vulnerabilities'].append('使用弱签名算法')
            if analysis['security_grade'] in ['A', 'B']:
                analysis['security_grade'] = 'C'
        
        # 检查密钥长度
        key_size = cert_info.get('key_size', 0)
        if key_size < 2048:
            analysis['vulnerabilities'].append('密钥长度过短（小于2048位）')
            if analysis['security_grade'] in ['A', 'B']:
                analysis['security_grade'] = 'C'
        
        # 检查 SSL/TLS 版本
        if ssl_version in ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1']:
            analysis['vulnerabilities'].append(f'使用过时的协议版本: {ssl_version}')
            if analysis['security_grade'] in ['A', 'B']:
                analysis['security_grade'] = 'C'
        
        # 检查加密套件
        if 'RC4' in cipher or 'DES' in cipher or 'NULL' in cipher:
            analysis['vulnerabilities'].append('使用弱加密套件')
            if analysis['security_grade'] in ['A', 'B']:
                analysis['security_grade'] = 'C'
                
    except Exception as e:
        analysis['vulnerabilities'].append(f'安全分析错误: {e}')
    
    return analysis

def check_ssl_certificate(hostname: str, port: int = 443, check_chain: bool = True) -> Dict[str, Any]:
    """检查 SSL 证书"""
    start_time = time.time()

    try:
        # 创建 SSL 上下文
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # 连接到服务器
        connect_start = time.time()
        sock = socket.create_connection((hostname, port), timeout=10)
        connect_time = round((time.time() - connect_start) * 1000, 2)

        # SSL 握手
        handshake_start = time.time()
        ssock = context.wrap_socket(sock, server_hostname=hostname)
        handshake_time = round((time.time() - handshake_start) * 1000, 2)

        # 获取证书信息
        cert_der = ssock.getpeercert(binary_form=True)
        cert_pem = ssock.getpeercert()

        # 获取连接信息
        ssl_version = ssock.version()
        cipher = ssock.cipher()
        cipher_name = cipher[0] if cipher else "Unknown"

        # 解析证书
        cert_info = parse_certificate(cert_der)

        # 获取证书链（如果需要）
        cert_chain = []
        if check_chain:
            try:
                # 尝试获取完整证书链
                cert_chain_der = ssock.getpeercert_chain()
                if cert_chain_der:
                    for chain_cert in cert_chain_der[1:]:  # 跳过第一个（主证书）
                        try:
                            chain_info = parse_certificate(chain_cert)
                            cert_chain.append(chain_info)
                        except:
                            continue
            except:
                pass

        # 关闭连接
        ssock.close()
        sock.close()

        total_time = round((time.time() - start_time) * 1000, 2)

        # 安全分析
        security_analysis = analyze_ssl_security(cert_info, ssl_version, cipher_name)

        # 获取 IP 地址
        ip_address = socket.gethostbyname(hostname)

        return {
            "hostname": hostname,
            "ip_address": ip_address,
            "port": port,
            "ssl_version": ssl_version,
            "cipher_suite": cipher_name,
            "certificate": cert_info,
            "certificate_chain": cert_chain,
            "security_analysis": security_analysis,
            "connection_info": {
                "handshake_time": handshake_time,
                "connect_time": connect_time,
                "total_time": total_time
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    except socket.timeout:
        raise Exception("连接超时")
    except socket.gaierror as e:
        raise Exception(f"域名解析失败: {e}")
    except ssl.SSLError as e:
        raise Exception(f"SSL 错误: {e}")
    except Exception as e:
        raise Exception(f"SSL 检查失败: {e}")

@router.post("/ssl-check")
async def ssl_check(request: SSLCheckRequest) -> SSLCheckResult:
    """执行 SSL 检查"""

    try:
        print(f"🔒 开始SSL检查 - 主机: {request.hostname}:{request.port}")

        data = check_ssl_certificate(request.hostname, request.port, request.check_chain)

        print(f"✅ SSL检查完成: {data['ssl_version']}, 安全等级: {data['security_analysis']['security_grade']}")

        return SSLCheckResult(
            success=True,
            data=data
        )

    except Exception as e:
        error_msg = str(e)
        print(f"❌ SSL检查失败: {error_msg}")

        return SSLCheckResult(
            success=False,
            error="SSL检查失败",
            details=error_msg
        )
