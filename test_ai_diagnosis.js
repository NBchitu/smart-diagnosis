const fetch = require('node-fetch');

async function testAIDiagnosis() {
  console.log('🔍 测试AI诊断功能...');
  
  const testMessages = [
    { role: 'user', content: '网络连接不稳定，经常断线' }
  ];
  
  try {
    const response = await fetch('http://localhost:3000/api/ai-diagnosis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ messages: testMessages }),
    });
    
    console.log('📊 响应状态:', response.status);
    console.log('📋 响应头:', response.headers.get('content-type'));
    
    if (response.ok) {
      console.log('✅ API调用成功');
      
      // 读取流式响应
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      console.log('🔄 读取响应流...');
      let chunks = '';
      
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          chunks += chunk;
          
          // 显示部分响应
          if (chunk.includes('ping')) {
            console.log('🔧 检测到ping工具调用');
          }
        }
        
        console.log('📤 响应流读取完成');
        console.log('📝 响应内容片段:', chunks.substring(0, 200) + '...');
        
        // 检查是否包含AI诊断相关内容
        if (chunks.includes('网络') || chunks.includes('连接') || chunks.includes('ping')) {
          console.log('✅ AI诊断功能正常工作');
        } else {
          console.log('⚠️ AI诊断功能可能存在问题');
        }
        
      } catch (streamError) {
        console.error('❌ 读取响应流失败:', streamError);
      }
      
    } else {
      console.log('❌ API调用失败:', response.status);
      const errorText = await response.text();
      console.log('错误详情:', errorText);
    }
    
  } catch (error) {
    console.error('❌ 测试失败:', error);
  }
}

async function testBackendPing() {
  console.log('🔍 测试后端ping功能...');
  
  try {
    const response = await fetch('http://localhost:8000/api/network/ping_test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ host: 'baidu.com', count: 3 }),
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('✅ 后端ping测试成功:', result);
    } else {
      console.log('❌ 后端ping测试失败:', response.status);
    }
    
  } catch (error) {
    console.error('❌ 后端ping测试错误:', error);
  }
}

async function main() {
  console.log('🚀 开始测试AI诊断系统...\n');
  
  await testBackendPing();
  console.log('\n' + '='.repeat(50) + '\n');
  await testAIDiagnosis();
  
  console.log('\n✅ 测试完成');
}

main().catch(console.error); 