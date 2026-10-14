import React, { useState } from 'react';
import { Bot, X, Send, Sparkles, User, Minimize2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { recommendationService, RecommendationCriteria } from '@/services/recommendation.service';

interface Message {
  id: string;
  sender: 'bot' | 'user';
  text: string;
  timestamp: string;
  suggestions?: string[];
  recommendations?: Array<{ id: number; title: string; priceText: string; matchPct: number }>;
}

export const ChatbotWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const navigate = useNavigate();

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'bot',
      text: 'Xin chào! Tôi là Trợ lý AI Bất động sản BDS Smart. Tôi có thể hỗ trợ bạn tìm kiếm nhà đất theo khoảng giá, khu vực hoặc giải đáp thắc mắc về đăng tin.',
      timestamp: 'Vừa xong',
      suggestions: [
        'Căn hộ chung cư Hà Nội dưới 4 tỷ',
        'Nhà riêng cho thuê',
        'Cách đăng tin nhanh',
      ],
    },
  ]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');

    const lower = query.toLowerCase();
    const criteria: RecommendationCriteria = {
      transaction_type: lower.includes('thuê') ? 'RENT' : 'SALE',
      top_k: 3,
    };
    if (lower.includes('chung cư') || lower.includes('căn hộ')) criteria.category_id = 1;
    if (lower.includes('nhà riêng') || lower.includes('nhà phố')) criteria.category_id = 2;
    if (lower.includes('hà nội')) criteria.province = 'Hà Nội';
    if (lower.includes('cầu giấy')) criteria.district = 'Cầu Giấy';
    if (lower.includes('nam từ liêm')) criteria.district = 'Nam Từ Liêm';
    if (lower.includes('4 tỷ')) criteria.budget_max = 4000000000;
    if (lower.includes('3 tỷ')) criteria.budget_max = 3500000000;
    if (lower.includes('2 tỷ')) criteria.budget_max = 2500000000;

    try {
      const res = await recommendationService.searchRecommendations(criteria);
      const recs = res.items.slice(0, 3).map((item) => ({
        id: item.id,
        title: item.title,
        priceText:
          item.price >= 1_000_000_000
            ? `${(item.price / 1_000_000_000).toFixed(1)} tỷ`
            : `${(item.price / 1_000_000).toFixed(0)} triệu`,
        matchPct: item.match_percentage,
      }));

      let replyText = `Dựa trên thuật toán gợi ý thông minh, tôi tìm thấy ${recs.length} bất động sản phù hợp nhất:`;
      if (recs.length === 0) {
        replyText = 'Hiện tại chưa có bất động sản nào khớp hoàn toàn tiêu chí này, bạn có thể tham khảo thêm tại trang Tìm kiếm.';
      }

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: replyText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        recommendations: recs,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: 'Tôi đã ghi nhận yêu cầu của bạn. Bạn có thể sử dụng menu Tìm kiếm để lọc bất động sản theo tiêu chí chi tiết.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, botMsg]);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating launcher button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group relative flex items-center space-x-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-full shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-200"
          title="Mở Trợ lý Chatbot AI"
        >
          <div className="relative">
            <Bot className="w-6 h-6 animate-pulse" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-400"></span>
            </span>
          </div>
          <span className="hidden sm:inline text-sm font-semibold">Tư vấn AI</span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="w-[360px] sm:w-[400px] h-[520px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 text-white flex items-center justify-between shadow-xs">
            <div className="flex items-center space-x-2.5">
              <div className="p-1.5 bg-white/20 rounded-lg">
                <Sparkles className="w-5 h-5 text-amber-300" />
              </div>
              <div>
                <h3 className="font-semibold text-sm">Trợ lý AI Bất Động Sản</h3>
                <p className="text-xs text-blue-100 flex items-center space-x-1">
                  <span className="w-2 h-2 rounded-full bg-green-400 inline-block"></span>
                  <span>Sẵn sàng hỗ trợ 24/7</span>
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-1">
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

          {/* Messages body */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-gray-50/50 text-sm">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`flex items-start space-x-2 max-w-[85%] ${
                    msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}
                >
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-xs font-semibold ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-indigo-100 text-indigo-700'
                    }`}
                  >
                    {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  <div
                    className={`p-3 rounded-2xl ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white rounded-tr-xs'
                        : 'bg-white border border-gray-200 text-gray-800 rounded-tl-xs shadow-xs'
                    }`}
                  >
                    <p className="text-xs leading-relaxed">{msg.text}</p>

                    {msg.recommendations && msg.recommendations.length > 0 && (
                      <div className="mt-2 space-y-1.5 pt-1.5 border-t border-gray-100">
                        {msg.recommendations.map((rec) => (
                          <div
                            key={rec.id}
                            onClick={() => {
                              setIsOpen(false);
                              navigate(`/listings/${rec.id}`);
                            }}
                            className="p-2 bg-blue-50/70 hover:bg-blue-100/70 rounded-lg cursor-pointer transition text-[11px] flex items-center justify-between"
                          >
                            <span className="font-semibold text-gray-800 line-clamp-1 mr-2">{rec.title}</span>
                            <span className="font-bold text-blue-600 shrink-0">{rec.priceText}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    <span
                      className={`text-[10px] block mt-1 ${
                        msg.sender === 'user' ? 'text-blue-200 text-right' : 'text-gray-400'
                      }`}
                    >
                      {msg.timestamp}
                    </span>
                  </div>
                </div>

                {/* Suggestions chips */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5 pl-9">
                    {msg.suggestions.map((s, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(s)}
                        className="text-xs px-2.5 py-1 bg-white border border-blue-200 text-blue-700 rounded-full hover:bg-blue-50 transition shadow-2xs"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Input Footer */}
          <div className="p-3 bg-white border-t border-gray-200 flex items-center space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Nhập yêu cầu tìm kiếm hoặc câu hỏi..."
              className="flex-1 text-xs px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim()}
              className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-40 transition shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
