import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  X,
  Send,
  Sparkles,
  User,
  Minimize2,
  RotateCcw,
  ExternalLink,
  MapPin,
  Bed,
  Maximize,
  Filter,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import {
  chatbotService,
  ChatMessageResponse,
  ExtractedCriteria,
} from '@/services/chatbot.service';
import { RecommendedListingItem } from '@/types';

interface DisplayMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
  listings?: RecommendedListingItem[];
  suggestions?: string[];
  criteria?: ExtractedCriteria;
  isClarification?: boolean;
}

const INITIAL_MESSAGE: DisplayMessage = {
  id: 'init-1',
  sender: 'bot',
  text: 'Xin chào! Tôi là Trợ lý AI Bất động sản BDS Smart. Tôi có thể hỗ trợ bạn tìm kiếm bất động sản theo ngân sách, khu vực, số phòng ngủ hoặc giải đáp thắc mắc về mua bán, cho thuê.',
  timestamp: 'Vừa xong',
  suggestions: [
    'Tìm chung cư 2PN Nam Từ Liêm dưới 3.5 tỷ',
    'Thuê căn hộ Cầu Giấy dưới 15 triệu',
    'Nhà riêng Hà Đông từ 8 đến 10 tỷ',
  ],
};

const SESSION_STORAGE_KEY = 'bds_ai_chat_session_id';

export const ChatbotWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(() => {
    return localStorage.getItem(SESSION_STORAGE_KEY);
  });
  const [messages, setMessages] = useState<DisplayMessage[]>([INITIAL_MESSAGE]);
  const [activeCriteria, setActiveCriteria] = useState<ExtractedCriteria | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, messages, isLoading]);

  const handleResetSession = () => {
    localStorage.removeItem(SESSION_STORAGE_KEY);
    setSessionId(null);
    setActiveCriteria(null);
    setMessages([
      {
        ...INITIAL_MESSAGE,
        id: `init-${Date.now()}`,
      },
    ]);
  };

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query || isLoading) return;

    const userMsg: DisplayMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response: ChatMessageResponse = await chatbotService.sendMessage({
        session_id: sessionId,
        message: query,
      });

      if (response.session_id) {
        setSessionId(response.session_id);
        localStorage.setItem(SESSION_STORAGE_KEY, response.session_id);
      }

      if (response.extracted_criteria) {
        setActiveCriteria((prev) => ({
          ...prev,
          ...response.extracted_criteria,
        }));
      }

      const botMsg: DisplayMessage = {
        id: `bot-${response.id || Date.now()}`,
        sender: 'bot',
        text: response.message_text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        listings: response.listings || [],
        suggestions: response.suggestions || [],
        criteria: response.extracted_criteria,
        isClarification: response.is_clarification,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch {
      const errorMsg: DisplayMessage = {
        id: `error-${Date.now()}`,
        sender: 'bot',
        text: 'Xin lỗi, hiện tại tôi gặp gián đoạn khi kết nối với máy chủ AI. Bạn vui lòng thử lại sau giây lát hoặc sử dụng trang Tìm kiếm.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestions: ['Thử lại', 'Đi tới trang Tìm kiếm'],
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (price: number, transactionType?: string) => {
    if (transactionType === 'RENT' || price < 1_000_000_000) {
      return `${(price / 1_000_000).toLocaleString('vi-VN')} tr/tháng`;
    }
    return `${(price / 1_000_000_000).toFixed(2).replace(/\.?0+$/, '')} tỷ`;
  };

  const renderCriteriaPills = (criteria: ExtractedCriteria) => {
    const pills: string[] = [];
    if (criteria.transaction_type === 'RENT') pills.push('Cho thuê');
    if (criteria.transaction_type === 'SALE') pills.push('Mua bán');
    if (criteria.category_name) pills.push(criteria.category_name);
    if (criteria.district) pills.push(criteria.district);
    else if (criteria.province) pills.push(criteria.province);
    if (criteria.budget_max) {
      const maxBillion = (criteria.budget_max / 1_000_000_000).toFixed(1);
      pills.push(`≤ ${maxBillion} tỷ`);
    }
    if (criteria.bedrooms) pills.push(`${criteria.bedrooms} PN`);

    if (pills.length === 0) return null;

    return (
      <div className="flex items-center flex-wrap gap-1 mb-2 px-2 py-1.5 bg-blue-50/70 border border-blue-100 rounded-lg text-[11px] text-blue-700">
        <Filter className="w-3 h-3 text-blue-500 shrink-0 mr-0.5" />
        <span className="font-semibold text-blue-900">Bộ lọc:</span>
        {pills.map((p, idx) => (
          <span key={idx} className="bg-white px-2 py-0.5 rounded-md border border-blue-200 font-medium">
            {p}
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating launcher button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group relative flex items-center space-x-2.5 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-full shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95 transition-all duration-200"
          title="Mở Trợ lý Chatbot AI Bất động sản"
        >
          <div className="relative">
            <Bot className="w-6 h-6 animate-pulse" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-400"></span>
            </span>
          </div>
          <span className="hidden sm:inline text-sm font-semibold tracking-wide">Tư vấn AI</span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="w-[375px] sm:w-[440px] h-[580px] max-h-[85vh] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 px-4 py-3 text-white flex items-center justify-between shadow-xs select-none">
            <div className="flex items-center space-x-2.5">
              <div className="p-1.5 bg-white/20 rounded-xl backdrop-blur-xs">
                <Sparkles className="w-5 h-5 text-amber-300" />
              </div>
              <div>
                <h3 className="font-semibold text-sm leading-tight flex items-center gap-1.5">
                  Trợ lý AI Bất Động Sản
                  <span className="text-[10px] bg-amber-400/90 text-slate-900 font-bold px-1.5 py-0.2 rounded-full">
                    SMART
                  </span>
                </h3>
                <p className="text-xs text-blue-100 flex items-center space-x-1.5 mt-0.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse inline-block"></span>
                  <span>Trực tuyến 24/7 • Dữ liệu thực tế</span>
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-1">
              <button
                onClick={handleResetSession}
                className="p-1.5 hover:bg-white/20 rounded-lg text-white transition"
                title="Làm mới cuộc trò chuyện"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-white/20 rounded-lg text-white transition"
                title="Thu nhỏ"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-white/20 rounded-lg text-white transition"
                title="Đóng"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Context Active Criteria Bar */}
          {activeCriteria && (activeCriteria.district || activeCriteria.budget_max || activeCriteria.bedrooms) && (
            <div className="bg-slate-50 border-b border-gray-200 px-3 py-1.5 flex items-center justify-between text-xs text-slate-600">
              <div className="flex items-center gap-1.5 truncate">
                <Filter className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span className="truncate">
                  Ngữ cảnh: {activeCriteria.category_name || 'BĐS'}{' '}
                  {activeCriteria.district ? `• ${activeCriteria.district}` : ''}{' '}
                  {activeCriteria.budget_max
                    ? `• < ${(activeCriteria.budget_max / 1_000_000_000).toFixed(1)} tỷ`
                    : ''}{' '}
                  {activeCriteria.bedrooms ? `• ${activeCriteria.bedrooms}PN` : ''}
                </span>
              </div>
              <button
                onClick={handleResetSession}
                className="text-[11px] text-blue-600 hover:text-blue-800 underline font-medium shrink-0 ml-2"
              >
                Đặt lại
              </button>
            </div>
          )}

          {/* Messages body */}
          <div className="flex-1 p-3.5 overflow-y-auto space-y-3.5 bg-slate-50/60 text-sm">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`flex items-start space-x-2 max-w-[92%] sm:max-w-[88%] ${
                    msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}
                >
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-xs font-semibold shadow-2xs ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-indigo-600 text-white'
                    }`}
                  >
                    {msg.sender === 'user' ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                  </div>

                  <div
                    className={`p-3 rounded-2xl ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white rounded-tr-xs shadow-xs'
                        : 'bg-white border border-gray-200 text-gray-800 rounded-tl-xs shadow-xs'
                    }`}
                  >
                    {/* Bot Criteria Tagging */}
                    {msg.sender === 'bot' && msg.criteria && renderCriteriaPills(msg.criteria)}

                    {/* Message Text with Paragraphs */}
                    <div className="text-xs leading-relaxed whitespace-pre-line space-y-1">
                      {msg.text}
                    </div>

                    {/* Recommended Listings Cards */}
                    {msg.listings && msg.listings.length > 0 && (
                      <div className="mt-3 space-y-2 pt-2 border-t border-gray-100">
                        <div className="text-[11px] font-bold text-slate-700 flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Gợi ý phù hợp nhất:</span>
                        </div>

                        {msg.listings.map((item) => (
                          <div
                            key={item.id}
                            onClick={() => {
                              setIsOpen(false);
                              navigate(`/listings/${item.id}`);
                            }}
                            className="group p-2.5 bg-white hover:bg-blue-50/50 border border-gray-200 hover:border-blue-300 rounded-xl cursor-pointer transition-all duration-150 shadow-2xs hover:shadow-xs"
                          >
                            <div className="flex items-start justify-between gap-2">
                              <h4 className="font-semibold text-xs text-gray-900 group-hover:text-blue-600 line-clamp-1 transition">
                                {item.title}
                              </h4>
                              <span className="shrink-0 text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                                {item.match_percentage}%
                              </span>
                            </div>

                            <div className="mt-1 flex items-center justify-between text-[11px]">
                              <span className="font-bold text-red-600">
                                {formatPrice(item.price, item.transaction_type)}
                              </span>
                              <div className="flex items-center gap-2 text-gray-500 text-[10px]">
                                {item.area && (
                                  <span className="flex items-center gap-0.5">
                                    <Maximize className="w-2.5 h-2.5" />
                                    {item.area} m²
                                  </span>
                                )}
                                {item.bedrooms && (
                                  <span className="flex items-center gap-0.5">
                                    <Bed className="w-2.5 h-2.5" />
                                    {item.bedrooms} PN
                                  </span>
                                )}
                              </div>
                            </div>

                            <div className="mt-1 flex items-center justify-between text-[10px] text-gray-500 pt-1 border-t border-gray-100">
                              <span className="flex items-center gap-0.5 truncate max-w-[200px]">
                                <MapPin className="w-2.5 h-2.5 text-gray-400 shrink-0" />
                                {item.district}, {item.province}
                              </span>
                              <span className="text-blue-600 font-medium group-hover:underline flex items-center gap-0.5">
                                Xem <ExternalLink className="w-2.5 h-2.5" />
                              </span>
                            </div>

                            {item.match_reasons && item.match_reasons.length > 0 && (
                              <div className="mt-1.5 flex flex-wrap gap-1">
                                {item.match_reasons.slice(0, 2).map((r, rIdx) => (
                                  <span
                                    key={rIdx}
                                    className="text-[9px] px-1.5 py-0.2 bg-blue-50 text-blue-700 rounded-md border border-blue-100"
                                  >
                                    ✓ {r}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    <span
                      className={`text-[10px] block mt-1.5 ${
                        msg.sender === 'user' ? 'text-blue-200 text-right' : 'text-gray-400'
                      }`}
                    >
                      {msg.timestamp}
                    </span>
                  </div>
                </div>

                {/* Quick suggestions chips */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5 pl-9">
                    {msg.suggestions.map((s, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(s)}
                        disabled={isLoading}
                        className="text-xs px-2.5 py-1 bg-white border border-blue-200 hover:border-blue-400 text-blue-700 rounded-full hover:bg-blue-50 transition shadow-2xs active:scale-95 disabled:opacity-50"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex items-start space-x-2">
                <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-2xs">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="p-3 bg-white border border-gray-200 rounded-2xl rounded-tl-xs shadow-xs flex items-center space-x-2 text-xs text-gray-500">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />
                  <span>AI đang phân tích và tìm kiếm bất động sản...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <div className="p-3 bg-white border-t border-gray-200 flex items-center space-x-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="VD: Căn hộ 2PN Nam Từ Liêm dưới 3.5 tỷ..."
              disabled={isLoading}
              className="flex-1 text-xs px-3.5 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              className="p-2.5 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white rounded-xl disabled:opacity-40 transition-all shrink-0 shadow-xs"
              title="Gửi tin nhắn"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
