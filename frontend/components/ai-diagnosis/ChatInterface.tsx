'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { Message } from 'ai';
import { Button } from '@/components/ui/button';
import TextareaAutosize from 'react-textarea-autosize';
import { Send, Bot, User, Loader2, Wrench, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';
import { PingResultCard } from './PingResultCard';
import { PacketCaptureResultCard } from './PacketCaptureResultCard';
import { PacketCaptureStatusCard } from './PacketCaptureStatusCard';
import { ToolsPanel } from './ToolsPanel';

interface ChatInterfaceProps {
  messages: Message[];
  input: string;
  handleInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  isLoading: boolean;
  placeholder?: string;
  onPacketCaptureCompleted?: (analysisResult: any) => void;
  onToolSelect?: (toolId: string) => void;
}

// 抓包会话状态接口
interface PacketCaptureSession {
  session_id: string;
  target: string;
  mode: string;
  start_time: string;
  duration: number;
  is_monitoring: boolean;
  status: 'running' | 'completed' | 'stopped' | 'error';
  retry_count?: number; // 添加重试计数器
}

// 解析消息中的特殊内容
const parseMessageContent = (content: string) => {
  const parts: Array<{ 
  type: 'text' | 'ping_result' | 'packet_capture_result' | 'packet_capture_stopped' | 'packet_capture_status' | 'packet_capture_started'; 
  content: string | any 
}> = [];
  
  // 使用正则表达式匹配```json代码块
  const jsonBlockRegex = /```json\s*([\s\S]*?)\s*```/g;
  let lastIndex = 0;
  let match;

  while ((match = jsonBlockRegex.exec(content)) !== null) {
    // 添加代码块前的文本
    if (match.index > lastIndex) {
      const textBefore = content.slice(lastIndex, match.index).trim();
      if (textBefore) {
        parts.push({ type: 'text', content: textBefore });
      }
    }

    // 尝试解析JSON
    try {
      const jsonContent = JSON.parse(match[1]);
      const supportedTypes = [
        'ping_result', 
        'packet_capture_result', 
        'packet_capture_stopped', 
        'packet_capture_status',
        'packet_capture_started'  // 新增启动类型
      ];
      
      if (supportedTypes.includes(jsonContent.type) && jsonContent.data) {
        parts.push({ type: jsonContent.type, content: jsonContent.data });
      } else {
        // 如果不是支持的类型，作为普通文本处理
        parts.push({ type: 'text', content: match[0] });
      }
    } catch (e) {
      // JSON解析失败，作为普通文本处理
      parts.push({ type: 'text', content: match[0] });
    }

    lastIndex = match.index + match[0].length;
  }

  // 添加剩余的文本
  if (lastIndex < content.length) {
    const remainingText = content.slice(lastIndex).trim();
    if (remainingText) {
      parts.push({ type: 'text', content: remainingText });
    }
  }

  // 如果没有找到任何特殊内容，返回原始文本
  if (parts.length === 0) {
    parts.push({ type: 'text', content });
  }

  return parts;
};

export function ChatInterface({
  messages,
  input,
  handleInputChange,
  handleSubmit,
  isLoading,
  placeholder = "请描述您遇到的问题...",
  onPacketCaptureCompleted,
  onToolSelect
}: ChatInterfaceProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  
  // 抓包会话状态管理
  const [activeCaptureSessions, setActiveCaptureSessions] = useState<Map<string, PacketCaptureSession>>(new Map());
  const [captureStatusUpdates, setCaptureStatusUpdates] = useState<Map<string, any>>(new Map());
  const intervalRefs = useRef<Map<string, NodeJS.Timeout>>(new Map());
  const activeSessionsRef = useRef<Map<string, PacketCaptureSession>>(new Map()); // 添加ref来跟踪当前状态

  // 同步状态到ref
  useEffect(() => {
    activeSessionsRef.current = activeCaptureSessions;
  }, [activeCaptureSessions]);

  // 轮询抓包状态的函数
  const pollCaptureStatus = useCallback(async (sessionId: string) => {
    try {
      console.log('🔄 轮询抓包状态:', sessionId);
      
      // 创建兼容的AbortController
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
      
      // 在API调用中传递session_id
      const response = await fetch(`/api/packet-capture-status?session_id=${encodeURIComponent(sessionId)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId); // 清除超时定时器
      
      console.log('📡 API响应状态:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url,
        headers: response.headers ? Array.from(response.headers.entries()) : []
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API错误响应:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
        throw new Error(`获取抓包状态失败: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      const result = await response.json();
      console.log('📊 API响应数据:', result);
      
      if (result.success && result.data) {
        const statusData = result.data;
        console.log('✅ 抓包状态更新:', {
          session_id: statusData.session_id,
          is_capturing: statusData.is_capturing,
          current_packet_count: statusData.current_packet_count,
          elapsed_time: statusData.elapsed_time,
          remaining_time: statusData.remaining_time,
          status: statusData.status
        });
        
        // 验证session_id匹配
        if (statusData.session_id !== sessionId) {
          console.warn('⚠️ Session ID不匹配!', {
            expected: sessionId,
            received: statusData.session_id
          });
        }
        
        // 更新状态
        setCaptureStatusUpdates(prev => new Map(prev.set(sessionId, statusData)));
        
        // 重置重试计数器（成功时）
        setActiveCaptureSessions(prev => {
          const newSessions = new Map(prev);
          const session = newSessions.get(sessionId);
          if (session) {
            session.retry_count = 0; // 重置重试计数
          }
          return newSessions;
        });
        
        // 检查是否完成
        if (statusData.status === 'completed' || !statusData.is_capturing) {
          console.log('✅ 抓包已完成，停止轮询并开始分析...');
          
          // 停止轮询
          const interval = intervalRefs.current.get(sessionId);
          if (interval) {
            clearInterval(interval);
            intervalRefs.current.delete(sessionId);
          }
          
          // 更新会话状态
          setActiveCaptureSessions(prev => {
            const newSessions = new Map(prev);
            const session = newSessions.get(sessionId);
            if (session) {
              session.status = 'completed';
              session.is_monitoring = false;
            }
            return newSessions;
          });
          
          // 自动分析结果
          try {
            console.log('🧠 开始自动分析...');
            
            // 创建分析请求的超时控制
            const analysisController = new AbortController();
            const analysisTimeoutId = setTimeout(() => analysisController.abort(), 30000); // 30秒超时
            
            const analysisResponse = await fetch('/api/packet-capture-analysis', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ session_id: sessionId }),
              signal: analysisController.signal,
            });
            
            clearTimeout(analysisTimeoutId); // 清除超时定时器
            
            if (analysisResponse.ok) {
              const analysisResult = await analysisResponse.json();
              console.log('✅ AI分析完成:', analysisResult);
              
              // 通知父组件分析完成
              if (onPacketCaptureCompleted && analysisResult.success) {
                onPacketCaptureCompleted(analysisResult.data);
              }
            } else {
              const analysisError = await analysisResponse.text();
              console.error('❌ 分析API错误:', {
                status: analysisResponse.status,
                error: analysisError
              });
            }
          } catch (analysisError) {
            console.error('❌ 自动分析失败:', analysisError);
          }
        }
      } else {
        console.warn('⚠️ API返回失败结果:', result);
        throw new Error(`API调用失败: ${result.error || '未知错误'}`);
      }
    } catch (error) {
      console.error('❌ 轮询抓包状态失败:', {
        sessionId,
        error: (error as Error).message,
        name: (error as Error).name,
        stack: (error as Error).stack
      });
      
      // 增加失败计数器，避免无限重试
      setActiveCaptureSessions(prev => {
        const newSessions = new Map(prev);
        const session = newSessions.get(sessionId);
        if (!session) {
          return newSessions; // session不存在，直接返回
        }
        
        // 如果是网络错误或超时，可以重试几次
        const isRetryableError = (error as Error).name === 'TypeError' || 
                                (error as Error).name === 'AbortError' ||
                                (error as Error).message.includes('fetch') ||
                                (error as Error).message.includes('timeout') ||
                                (error as Error).message.includes('network');
        
        if (isRetryableError) {
          // 增加重试计数
          const retryCount = (session.retry_count || 0) + 1;
          const maxRetries = 3; // 最大重试3次
          
          if (retryCount <= maxRetries) {
            console.log(`🔄 网络错误或超时，重试次数: ${retryCount}/${maxRetries}，将在下次轮询时重试...`);
            
            // 更新重试计数，继续轮询
            session.retry_count = retryCount;
            return newSessions;
          } else {
            console.error(`❌ 达到最大重试次数(${maxRetries})，停止轮询`);
          }
        }
        
        // 其他错误或达到最大重试次数，停止轮询
        const interval = intervalRefs.current.get(sessionId);
        if (interval) {
          clearInterval(interval);
          intervalRefs.current.delete(sessionId);
        }
        
        session.status = 'error';
        session.is_monitoring = false;
        return newSessions;
      });
    }
  }, [onPacketCaptureCompleted]);

  // 开始监控抓包会话
  const startMonitoringSession = useCallback((sessionData: any) => {
    const sessionId = sessionData.session_id;
    
    if (!sessionId) {
      console.error('❌ 无效的会话ID');
      return;
    }
    
    // 检查是否已经在监控中（去重）
    const existingSession = activeSessionsRef.current.get(sessionId);
    if (existingSession && existingSession.is_monitoring) {
      console.log('⚠️ 会话已在监控中，跳过重复启动:', sessionId);
      return;
    }
    
    // 如果存在旧的定时器，先清理
    const existingInterval = intervalRefs.current.get(sessionId);
    if (existingInterval) {
      console.log('🧹 清理旧的定时器:', sessionId);
      clearInterval(existingInterval);
      intervalRefs.current.delete(sessionId);
    }
    
    console.log('🎯 开始监控抓包会话:', sessionId);
    
    const session: PacketCaptureSession = {
      session_id: sessionId,
      target: sessionData.target || '未知',
      mode: sessionData.mode || '未知',
      start_time: new Date().toISOString(),
      duration: sessionData.duration || 30,
      is_monitoring: true,
      status: 'running',
      retry_count: 0 // 初始化重试计数器
    };
    
    setActiveCaptureSessions(prev => new Map(prev.set(sessionId, session)));
    
    // 立即获取一次状态
    pollCaptureStatus(sessionId);
    
    // 开始每5秒轮询一次
    const interval = setInterval(() => {
      console.log('⏰ 定时轮询触发:', sessionId, '时间:', new Date().toLocaleTimeString());
      pollCaptureStatus(sessionId);
    }, 5000);
    
    intervalRefs.current.set(sessionId, interval);
    console.log('✅ 定时器已设置:', sessionId, '间隔: 5秒');
  }, [pollCaptureStatus]);

  // 停止监控抓包会话
  const stopMonitoringSession = useCallback(async (sessionId: string) => {
    console.log('⏹️ 停止监控抓包会话:', sessionId);
    
    const interval = intervalRefs.current.get(sessionId);
    if (interval) {
      clearInterval(interval);
      intervalRefs.current.delete(sessionId);
    }
    
    setActiveCaptureSessions(prev => {
      const newSessions = new Map(prev);
      const session = newSessions.get(sessionId);
      if (session) {
        session.is_monitoring = false;
        session.status = 'stopped';
      }
      return newSessions;
    });
    
    // 调用后端API停止抓包
    try {
      console.log('📡 调用API停止抓包...');
      const response = await fetch('/api/packet-capture-status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'stop',
          session_id: sessionId
        })
      });
      
      const result = await response.json();
      console.log('🛑 停止抓包API响应:', result);
      
      if (result.success) {
        console.log('✅ 抓包已成功停止');
      } else {
        console.warn('⚠️ 停止抓包失败:', result.error);
      }
    } catch (error) {
      console.error('❌ 调用停止抓包API失败:', error);
    }
  }, []);

  // 添加已处理消息的ref，避免重复处理
  const processedMessagesRef = useRef<Set<number>>(new Set());

  // 检测新的抓包启动消息
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (!lastMessage) return;
    
    const messageIndex = messages.length - 1;
    
    // 🔧 新增：如果是assistant消息但内容为空，跳过检测（等待流式传输完成）
    if (lastMessage.role === 'assistant' && 
        (!lastMessage.content || lastMessage.content.trim() === '')) {
      console.log('⚠️ Assistant消息内容为空，等待流式传输完成...');
      return;
    }
    
    // 检查是否已经处理过这条消息
    if (processedMessagesRef.current.has(messageIndex)) {
      console.log('⚠️ 消息已处理，跳过:', messageIndex);
      return;
    }
    
    console.log('🔍 检查最新消息:', {
      index: messageIndex,
      role: lastMessage.role,
      content: typeof lastMessage.content === 'string' ? lastMessage.content.substring(0, 200) + '...' : lastMessage.content,
      fullContent: lastMessage.content, // 添加完整内容用于调试
      messageLength: messages.length,
      isProcessed: processedMessagesRef.current.has(messageIndex)
    });
    
    let foundSession = false;
    
    // 检查助手消息中是否包含工具调用结果
    if (lastMessage.role === 'assistant' && typeof lastMessage.content === 'string') {
      try {
        // 尝试解析消息中的JSON块，查找抓包启动信息
        const jsonRegex = /```json\s*([\s\S]*?)\s*```/g;
        let match;
        
        while ((match = jsonRegex.exec(lastMessage.content)) !== null) {
          try {
            const jsonData = JSON.parse(match[1]);
            console.log('📋 解析到JSON数据:', jsonData);
            
            // 检查是否是抓包启动类型（新格式）
            if (jsonData.type === 'packet_capture_started' && jsonData.data && jsonData.data.session_id) {
              console.log('🎯 检测到抓包启动消息(packet_capture_started):', jsonData.data);
              
              // 开始监控这个会话
              startMonitoringSession({
                session_id: jsonData.data.session_id,
                target: jsonData.data.target || '未知',
                mode: jsonData.data.mode || 'auto',
                duration: jsonData.data.duration || 30
              });
              
              foundSession = true;
              break; // 找到了，退出
            }
            
            // 检查是否是抓包启动响应（包含session_id的success结果）
            if (jsonData.session_id && typeof jsonData.session_id === 'string' && 
                jsonData.session_id.startsWith('capture_')) {
              console.log('🎯 检测到抓包启动响应:', jsonData);
              
              // 开始监控这个会话
              startMonitoringSession({
                session_id: jsonData.session_id,
                target: jsonData.target || '未知',
                mode: jsonData.mode || 'auto',
                duration: jsonData.duration || 30
              });
              
              foundSession = true;
              break; // 找到了，退出
            }
            
            // 检查是否是抓包结果类型（最终分析结果，也包含session_id）
            if (jsonData.type === 'packet_capture_result' && jsonData.data && jsonData.data.session_id) {
              console.log('🎯 检测到抓包分析结果:', jsonData.data);
              
              // 如果是完成状态，可能需要启动监控或更新状态
              if (jsonData.data.status === 'completed') {
                console.log('✅ 抓包已完成，跳过监控');
                foundSession = true;
                break;
              }
              
              // 开始监控这个会话
              startMonitoringSession({
                session_id: jsonData.data.session_id,
                target: jsonData.data.target,
                mode: jsonData.data.mode || 'auto',
                duration: jsonData.data.duration || 30
              });
              
              foundSession = true;
              break; // 找到了，退出
            }
            
            // 检查嵌套的data字段中是否包含session_id
            if (jsonData.data && jsonData.data.session_id && 
                typeof jsonData.data.session_id === 'string' && 
                jsonData.data.session_id.startsWith('capture_')) {
              console.log('🎯 检测到嵌套的抓包数据:', jsonData.data);
              
              // 开始监控这个会话
              startMonitoringSession({
                session_id: jsonData.data.session_id,
                target: jsonData.data.target || '未知',
                mode: jsonData.data.mode || 'auto',
                duration: jsonData.data.duration || 30
              });
              
              foundSession = true;
              break; // 找到了，退出
            }
            
            // 🔧 新增：检查PacketCaptureStatusCard相关的抓包启动状态
            if (jsonData.type === 'packet_capture_started' && jsonData.data) {
              console.log('🎯 检测到packet_capture_started类型:', jsonData.data);
              
              // 开始监控这个会话
              startMonitoringSession({
                session_id: jsonData.data.session_id,
                target: jsonData.data.target || '未知',
                mode: jsonData.data.mode || 'auto',
                duration: jsonData.data.duration || 30
              });
              
              foundSession = true;
              break; // 找到了，退出
            }
            
            // 🔧 新增：检查直接包含session_id的数据
            if (jsonData.session_id && typeof jsonData.session_id === 'string' && 
                jsonData.session_id.startsWith('capture_') && 
                (jsonData.target || jsonData.mode || jsonData.duration)) {
              console.log('🎯 检测到直接包含session_id的抓包数据:', jsonData);
              
              // 开始监控这个会话
              startMonitoringSession({
                session_id: jsonData.session_id,
                target: jsonData.target || '未知',
                mode: jsonData.mode || 'auto',
                duration: jsonData.duration || 30
              });
              
              foundSession = true;
              break; // 找到了，退出
            }
            
            // 🔧 新增：检查是否是工具调用结果格式 (针对用户提供的消息格式)
            if (jsonData.toolCallId && jsonData.result && 
                jsonData.result.server === 'packet_capture' && 
                jsonData.result.data && 
                jsonData.result.data.session_id) {
              console.log('🎯 检测到工具调用结果格式(assistant消息中):', jsonData.result.data);
              
              // 开始监控这个会话
              startMonitoringSession({
                session_id: jsonData.result.data.session_id,
                target: jsonData.result.data.target || '未知',
                mode: jsonData.result.data.mode || 'auto',
                duration: jsonData.result.data.duration || 30
              });
              
              foundSession = true;
              break; // 找到了，退出
            }
            
          } catch (jsonError) {
            // 忽略JSON解析错误，继续查找下一个
            console.log('⚠️ JSON解析失败:', jsonError);
          }
        }
        
        // 如果没有找到JSON块，检查消息中是否包含session_id
        if (!foundSession) {
          // 扩展的session_id匹配模式
          const sessionIdPatterns = [
            /session_id["\s:]*["']?(capture_\d+)["']?/i,
            /会话ID[:\s]*["']?(capture_\d+)["']?/i,
            /会话[:\s]*["']?(capture_\d+)["']?/i,
            /(capture_\d+)/g
          ];
          
          let sessionIdMatch = null;
          for (const pattern of sessionIdPatterns) {
            sessionIdMatch = lastMessage.content.match(pattern);
            if (sessionIdMatch) {
              console.log('🔍 使用模式匹配发现session_id:', sessionIdMatch[1] || sessionIdMatch[0]);
              break;
            }
          }
          
          if (sessionIdMatch) {
            const sessionId = sessionIdMatch[1] || sessionIdMatch[0];
            
            // 尝试从消息上下文中提取其他信息
            const targetMatch = lastMessage.content.match(/目标[:\s]*([^\s,，。！]+)/);
            const target = targetMatch ? targetMatch[1] : '未知';
            
            // 尝试提取更多信息
            const modeMatch = lastMessage.content.match(/模式[:\s]*([^\s,，。！]+)/);
            const mode = modeMatch ? modeMatch[1] : 'auto';
            
            const durationMatch = lastMessage.content.match(/(\d+)[秒\s]*$/);
            const duration = durationMatch ? parseInt(durationMatch[1]) : 30;
            
            console.log('🔍 从消息文本中提取的信息:', {
              sessionId,
              target,
              mode,
              duration
            });
            
            startMonitoringSession({
              session_id: sessionId,
              target: target,
              mode: mode,
              duration: duration
            });
            
            foundSession = true;
          }
        }
        
      } catch (error) {
        console.log('⚠️ 消息解析失败:', error);
      }
    }
    
    // 检测工具调用结果消息（data 和 tool 类型）
    if (!foundSession && (lastMessage.role === 'data' || (lastMessage.role as any) === 'tool')) {
      try {
        const messageData = typeof lastMessage.content === 'string' 
          ? JSON.parse(lastMessage.content) 
          : lastMessage.content;
        
        console.log(`📋 检测到${lastMessage.role}消息:`, {
          role: lastMessage.role,
          hasToolCallId: !!messageData.toolCallId,
          hasResult: !!messageData.result,
          server: messageData.result?.server,
          hasData: !!messageData.result?.data,
          hasSessionId: !!messageData.result?.data?.session_id,
          sessionId: messageData.result?.data?.session_id,
          messageData: messageData
        });
        
        // 检查是否是抓包启动的工具调用结果
        if (messageData.toolCallId && messageData.result && 
            messageData.result.server === 'packet_capture' && 
            messageData.result.data && 
            messageData.result.data.session_id) {
          
          const sessionData = messageData.result.data;
          console.log(`🔍 检测到抓包启动(${lastMessage.role}消息):`, sessionData);
          
          // 开始监控这个会话
          startMonitoringSession(sessionData);
          foundSession = true;
        } else {
          console.log(`⚠️ ${lastMessage.role}消息不符合抓包启动条件:`, {
            hasToolCallId: !!messageData.toolCallId,
            hasResult: !!messageData.result,
            server: messageData.result?.server,
            expectedServer: 'packet_capture',
            hasData: !!messageData.result?.data,
            hasSessionId: !!messageData.result?.data?.session_id
          });
        }
      } catch (error) {
        console.log(`⚠️ ${lastMessage.role}消息解析失败:`, error);
      }
    }
    
    // 🔧 新增：检查其他可能的消息类型
    if (!foundSession) {
      console.log('🔍 检查其他消息类型:', {
        role: lastMessage.role,
        contentType: typeof lastMessage.content,
        contentPreview: typeof lastMessage.content === 'string' ? lastMessage.content.substring(0, 100) : 'non-string'
      });
      
      // 如果是对象类型的content，直接检查
      if (typeof lastMessage.content === 'object' && lastMessage.content !== null) {
        const contentObj = lastMessage.content as any;
        
        if (contentObj.toolCallId && contentObj.result && 
            contentObj.result.server === 'packet_capture' && 
            contentObj.result.data && 
            contentObj.result.data.session_id) {
          
          console.log('🎯 检测到对象类型的工具调用结果:', contentObj.result.data);
          
          startMonitoringSession({
            session_id: contentObj.result.data.session_id,
            target: contentObj.result.data.target || '未知',
            mode: contentObj.result.data.mode || 'auto',
            duration: contentObj.result.data.duration || 30
          });
          
          foundSession = true;
        }
      }
    }
    
    // 🔧 新增：如果在最新消息中没有找到会话，检查最近的几条消息
    if (!foundSession && messages.length > 1) {
      console.log('🔍 在最新消息中未找到会话，检查最近的消息...');
      
      // 检查最近的3条消息
      const recentMessages = messages.slice(-3);
      for (let i = recentMessages.length - 1; i >= 0; i--) {
        const msg = recentMessages[i];
        const msgIndex = messages.length - recentMessages.length + i;
        
        // 跳过已处理的消息
        if (processedMessagesRef.current.has(msgIndex)) {
          continue;
        }
        
        console.log(`🔍 检查消息 ${msgIndex}:`, {
          role: msg.role,
          contentType: typeof msg.content,
          hasContent: !!msg.content,
          contentPreview: typeof msg.content === 'string' ? msg.content.substring(0, 100) : 'non-string'
        });
        
        // 检查是否包含capture_开头的ID
        if (typeof msg.content === 'string' && msg.content.includes('capture_')) {
          const captureIds = msg.content.match(/capture_\d+/g);
          if (captureIds && captureIds.length > 0) {
            const sessionId = captureIds[0];
            console.log('🎯 在历史消息中找到会话ID:', sessionId);
            
            // 从消息中尝试提取目标信息
            const targetMatch = msg.content.match(/sina\.com|baidu\.com|qq\.com|[\w\-]+\.[\w\-]+/);
            const target = targetMatch ? targetMatch[0] : '未知';
            
            startMonitoringSession({
              session_id: sessionId,
              target: target,
              mode: 'auto',
              duration: 60
            });
            
            foundSession = true;
            break;
          }
        }
      }
    }
    
    // 标记消息已处理
    processedMessagesRef.current.add(messageIndex);
    
    // 如果没有找到会话，记录详细信息用于调试
    if (!foundSession) {
      console.log('❌ 未找到抓包会话，消息详情:', {
        index: messageIndex,
        role: lastMessage.role,
        contentType: typeof lastMessage.content,
        content: lastMessage.content
      });
      
      // 🔧 最后兜底检测：如果消息中包含capture_开头的ID，强制启动监控
      if (typeof lastMessage.content === 'string' && lastMessage.content.includes('capture_')) {
        const captureIds = lastMessage.content.match(/capture_\d+/g);
        if (captureIds && captureIds.length > 0) {
          const sessionId = captureIds[0];
          console.log('🔧 兜底检测：强制启动监控for session:', sessionId);
          
          // 从消息中尝试提取目标信息
          const targetMatch = lastMessage.content.match(/sina\.com|baidu\.com|qq\.com|[\w\-]+\.[\w\-]+/);
          const target = targetMatch ? targetMatch[0] : '未知';
          
          startMonitoringSession({
            session_id: sessionId,
            target: target,
            mode: 'auto',
            duration: 60
          });
          
          foundSession = true;
        }
      }
    }
    
    // 清理旧的处理记录（保留最近10条）
    if (processedMessagesRef.current.size > 10) {
      const sorted = Array.from(processedMessagesRef.current).sort((a, b) => b - a);
      processedMessagesRef.current = new Set(sorted.slice(0, 10));
    }
    
  }, [messages, startMonitoringSession]); // 添加startMonitoringSession依赖

  // 🔧 新增：定时检查是否有遗漏的抓包会话
  useEffect(() => {
    const checkMissedSessions = () => {
      // 如果已经有活跃的会话，就不再检查
      if (activeCaptureSessions.size > 0) {
        return;
      }
      
      // 检查最近的5条消息
      const recentMessages = messages.slice(-5);
      for (let i = 0; i < recentMessages.length; i++) {
        const msg = recentMessages[i];
        if (typeof msg.content === 'string' && msg.content.includes('capture_')) {
          const captureIds = msg.content.match(/capture_\d+/g);
          if (captureIds && captureIds.length > 0) {
            const sessionId = captureIds[0];
            
            // 检查是否已经在监控中
            if (!activeCaptureSessions.has(sessionId)) {
              console.log('🔍 定时检查发现遗漏的会话:', sessionId);
              
              // 从消息中尝试提取目标信息
              const targetMatch = msg.content.match(/sina\.com|baidu\.com|qq\.com|[\w\-]+\.[\w\-]+/);
              const target = targetMatch ? targetMatch[0] : '未知';
              
              startMonitoringSession({
                session_id: sessionId,
                target: target,
                mode: 'auto',
                duration: 60
              });
              
              break; // 找到一个就够了
            }
          }
        }
      }
    };
    
    // 每10秒检查一次
    const checkInterval = setInterval(checkMissedSessions, 10000);
    
    return () => {
      clearInterval(checkInterval);
    };
  }, [messages, activeCaptureSessions, startMonitoringSession]);

  // 组件卸载时清理所有轮询
  useEffect(() => {
    return () => {
      intervalRefs.current.forEach((interval) => {
        clearInterval(interval);
      });
      intervalRefs.current.clear();
    };
  }, []);

  // 自动滚动到底部
  const scrollToBottom = useCallback(() => {
    if (scrollAreaRef.current) {
      requestAnimationFrame(() => {
        const scrollElement = scrollAreaRef.current;
        if (scrollElement) {
          // 直接滚动到底部
          scrollElement.scrollTo({
            top: scrollElement.scrollHeight,
            behavior: 'smooth'
          });
          
          // 调试信息
          console.log('📜 滚动到底部:', {
            scrollHeight: scrollElement.scrollHeight,
            scrollTop: scrollElement.scrollTop,
            clientHeight: scrollElement.clientHeight
          });
        }
      });
    }
  }, []);

  // 消息变化时滚动
  useEffect(() => {
    const timeoutId = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timeoutId);
  }, [messages, captureStatusUpdates, scrollToBottom]);

  // 加载状态变化时滚动
  useEffect(() => {
    if (!isLoading) {
      const timeoutId = setTimeout(scrollToBottom, 200);
      return () => clearTimeout(timeoutId);
    }
  }, [isLoading, scrollToBottom]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (formRef.current) {
        formRef.current.requestSubmit();
      }
    }
  };

  const renderMessage = (message: Message, index: number) => {
    const isUser = message.role === 'user';
    const isAssistant = message.role === 'assistant';
    // AI SDK v5 支持: 检测工具调用消息的多种角色类型
    // 使用类型断言来兼容新旧版本的消息类型
    const messageRole = message.role as string;
    const isFunction = messageRole === 'data' || 
                      messageRole === 'tool' || 
                      messageRole === 'function';

    return (
      <div
        key={index}
        className={cn(
          "flex gap-3 p-4",
          isUser && "bg-blue-50",
          isAssistant && "bg-gray-50",
          isFunction && "bg-yellow-50"
        )}
      >
        <div className="flex-shrink-0">
          {isUser && (
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
          )}
          {isAssistant && (
            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
          )}
          {isFunction && (
            <div className="w-8 h-8 bg-yellow-600 rounded-full flex items-center justify-center">
              <Wrench className="w-4 h-4 text-white" />
            </div>
          )}
        </div>
        
        <div className="flex-1 space-y-2">
          <div className="text-sm font-medium text-gray-900">
            {isUser && '您'}
            {isAssistant && 'AI 助手'}
            {isFunction && '工具调用'}
          </div>
          
          <div className="prose prose-sm max-w-none">
            {isFunction ? (
              <div className="bg-yellow-100 border border-yellow-200 rounded p-3">
                <div className="font-medium text-yellow-800 mb-2">执行工具</div>
                <pre className="text-sm text-yellow-700 whitespace-pre-wrap">
                  {typeof message.content === 'string' 
                    ? message.content 
                    : JSON.stringify(message.content, null, 2)
                  }
                </pre>
              </div>
            ) : isAssistant ? (
              // 对助手消息进行特殊解析
              <div className="space-y-3">
                {parseMessageContent(message.content).map((part, partIndex) => (
                  <div key={partIndex}>
                    {part.type === 'text' ? (
                      <div className="text-gray-700 whitespace-pre-wrap">
                        {part.content}
                      </div>
                    ) : part.type === 'ping_result' ? (
                      <div className="not-prose">
                        <PingResultCard result={part.content} />
                      </div>
                    ) : part.type === 'packet_capture_result' ? (
                      <div className="not-prose">
                        <PacketCaptureResultCard result={part.content} />
                      </div>
                    ) : (part.type === 'packet_capture_stopped' || part.type === 'packet_capture_status' || part.type === 'packet_capture_started') ? (
                      <div className="not-prose">
                        <PacketCaptureStatusCard 
                          type={part.type as 'packet_capture_stopped' | 'packet_capture_status' | 'packet_capture_started'} 
                          data={part.content} 
                        />
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-700 whitespace-pre-wrap">
                {message.content}
              </div>
            )}
          </div>
          
          {/* 如果是助手消息，显示时间戳 */}
          {(isAssistant || isFunction) && (
            <div className="text-xs text-gray-500">
              {new Date().toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div 
        className="flex-1 p-0 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100" 
        ref={scrollAreaRef}
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium">诊断助手</p>
              <p className="text-sm">描述您的网络问题，我会为您提供专业的诊断和解决方案</p>
            </div>
          </div>
        ) : (
          <div className="space-y-0">
            {messages.map(renderMessage)}
            
            {/* 显示活跃的抓包状态 */}
            {Array.from(activeCaptureSessions.values()).map(session => {
              const statusUpdate = captureStatusUpdates.get(session.session_id);
              
              if (!session.is_monitoring) return null;
              
              return (
                <div key={session.session_id} className="flex gap-3 p-4 bg-blue-50 border-l-4 border-blue-400">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <Activity className="w-4 h-4 text-white animate-pulse" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900 mb-2">
                      🔍 抓包监控中
                    </div>
                    <div className="space-y-2">
                      <div className="text-sm text-gray-700">
                        <span className="font-medium">目标:</span> {session.target} | 
                        <span className="font-medium"> 模式:</span> {session.mode} | 
                        <span className="font-medium"> 会话ID:</span> {session.session_id}
                      </div>
                      
                      {statusUpdate && (
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="font-medium text-gray-600">当前包数:</span>
                            <span className="ml-1 text-blue-600 font-bold">
                              {statusUpdate.current_packet_count || 0}
                            </span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">已用时间:</span>
                            <span className="ml-1 text-blue-600 font-bold">
                              {statusUpdate.elapsed_time || 0}秒
                            </span>
                          </div>
                          {statusUpdate.remaining_time !== undefined && (
                            <div className="col-span-2">
                              <span className="font-medium text-gray-600">剩余时间:</span>
                              <span className="ml-1 text-orange-600 font-bold">
                                {statusUpdate.remaining_time}秒
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                      
                      <div className="flex items-center gap-2 text-blue-600">
                        <Activity className="w-3 h-3 animate-pulse" />
                        <span className="text-xs">
                          每5秒自动更新状态...
                          {session.retry_count && session.retry_count > 0 && (
                            <span className="text-orange-500 ml-1">
                              (重试: {session.retry_count}/3)
                            </span>
                          )}
                        </span>
                      </div>
                      
                      {session.status === 'completed' && (
                        <div className="text-sm text-green-600 font-medium">
                          ✅ 抓包已完成，正在进行AI分析...
                        </div>
                      )}
                      
                      {session.status === 'error' && (
                        <div className="text-sm text-red-600 font-medium">
                          ❌ 监控出错，请检查网络连接或重新启动抓包
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* 停止按钮 */}
                  <div className="flex-shrink-0">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => stopMonitoringSession(session.session_id)}
                      className="text-xs"
                    >
                      停止监控
                    </Button>
                  </div>
                </div>
              );
            })}
            
            {isLoading && (
              <div className="flex gap-3 p-4 bg-gray-50">
                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900 mb-2">AI 助手</div>
                  <div className="flex items-center space-x-2 text-gray-600">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">正在分析...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 输入区域 */}
      <div className="border-t bg-white">
        {/* 工具面板区域 */}
        <div className="px-4 pt-3 pb-2 bg-gradient-to-r from-blue-50/50 via-indigo-50/50 to-purple-50/50 border-b border-blue-100/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">快速诊断工具</span>
          </div>
          <div className="flex space-x-2">
            {onToolSelect && (
              <ToolsPanel
                onToolSelect={onToolSelect}
                disabled={isLoading}
              />
            )}
          </div>
        </div>

        {/* 输入框区域 */}
        <div className="p-4">
          <form ref={formRef} onSubmit={handleSubmit} className="flex gap-2" suppressHydrationWarning={true}>
            <div className="flex-1 relative">
              <TextareaAutosize
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                className="w-full resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                minRows={1}
                maxRows={4}
                disabled={isLoading}
                suppressHydrationWarning={true}
              />
            </div>
            <Button
              type="submit"
              disabled={isLoading || !input.trim()}
              size="sm"
              className="px-3"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
} 