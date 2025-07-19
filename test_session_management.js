#!/usr/bin/env node

/**
 * 抓包会话管理修复验证脚本
 */

const fetch = require('node-fetch');

const BASE_URL = 'http://localhost:3000';

async function testSessionManagement() {
  console.log('🧪 开始测试抓包会话管理修复...\n');
  
  try {
    // 1. 模拟AI启动抓包（这通常会生成新的session_id）
    console.log('1️⃣ 模拟抓包启动...');
    
    // 2. 测试不带session_id的状态查询（应该返回最新活跃会话）
    console.log('2️⃣ 测试不带session_id的状态查询...');
    const response1 = await fetch(`${BASE_URL}/api/packet-capture-status`);
    const result1 = await response1.json();
    
    console.log('📊 状态查询结果:', {
      success: result1.success,
      session_id: result1.data?.session_id,
      status: result1.data?.status,
      is_capturing: result1.data?.is_capturing,
      target: result1.data?.target
    });
    
    if (result1.success && result1.data?.session_id) {
      const sessionId = result1.data.session_id;
      
      // 3. 测试带session_id的状态查询
      console.log('\n3️⃣ 测试带session_id的状态查询...');
      const response2 = await fetch(`${BASE_URL}/api/packet-capture-status?session_id=${sessionId}`);
      const result2 = await response2.json();
      
      console.log('📊 指定会话状态查询结果:', {
        success: result2.success,
        session_id: result2.data?.session_id,
        status: result2.data?.status,
        is_capturing: result2.data?.is_capturing,
        session_id_match: result2.data?.session_id === sessionId
      });
      
      // 4. 验证session_id匹配
      if (result2.data?.session_id === sessionId) {
        console.log('✅ Session ID匹配验证通过');
      } else {
        console.log('❌ Session ID匹配验证失败');
      }
    } else {
      console.log('⚠️ 没有找到活跃的抓包会话');
    }
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
  }
  
  console.log('\n🎉 会话管理测试完成！');
}

// 运行测试
testSessionManagement(); 