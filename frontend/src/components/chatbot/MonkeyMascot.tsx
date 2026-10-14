import React, { useState, useEffect, useRef } from 'react';

interface MonkeyMascotProps {
  size?: number;
  isTyping?: boolean;
  className?: string;
  onClick?: () => void;
  showSpeechBubble?: boolean;
}

const MONKEY_QUOTES = [
  'Hỏi em về nhà đất nha! 🐵',
  'Tìm nhà ưng ý, để em lo! 🏠',
  'Cần mua hay thuê nhà nè? ✨',
  'Em biết nhiều căn hộ giá tốt lắm! 🏢',
  'Bấm vào em để chat thử nha! 💬',
  'Đang tìm nhà khu vực nào đó? 📍',
  'Ngân sách bao nhiêu em lọc được hết! 💰',
  'Hôm nay có nhiều căn mới đăng lắm! 🌟',
  'Trợ lý Khỉ AI thông minh nhất xóm! 🍌',
  'Em biết định giá & phân tích pháp lý đó! 📊',
  'Nhắn em một câu, tìm nhà liền tay! 🚀',
];

export const MonkeyMascot: React.FC<MonkeyMascotProps> = ({
  size = 72,
  isTyping: externalIsTyping,
  className = '',
  onClick,
  showSpeechBubble = false,
}) => {
  const [internalIsTyping, setInternalIsTyping] = useState(false);
  const isTyping = externalIsTyping ?? internalIsTyping;

  const [pupilOffset, setPupilOffset] = useState({ x: 0, y: 0 });
  const [headTilt, setHeadTilt] = useState({ rotateX: 0, rotateY: 0 });
  const [isBlinking, setIsBlinking] = useState(false);
  const [quoteIndex, setQuoteIndex] = useState(() => Math.floor(Math.random() * MONKEY_QUOTES.length));
  const [isBubbleVisible, setIsBubbleVisible] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  // Rotate speech bubble quotes every 4.5 seconds with random selection
  useEffect(() => {
    if (!showSpeechBubble) return;

    const interval = setInterval(() => {
      setIsBubbleVisible(false);
      setTimeout(() => {
        setQuoteIndex((prev) => {
          let next = Math.floor(Math.random() * MONKEY_QUOTES.length);
          if (next === prev) {
            next = (prev + 1) % MONKEY_QUOTES.length;
          }
          return next;
        });
        setIsBubbleVisible(true);
      }, 300);
    }, 4500);

    return () => clearInterval(interval);
  }, [showSpeechBubble]);

  // 1. Natural blinking effect every 3-5 seconds
  useEffect(() => {
    let blinkTimer: NodeJS.Timeout;
    const triggerBlink = () => {
      setIsBlinking(true);
      setTimeout(() => {
        setIsBlinking(false);
        blinkTimer = setTimeout(triggerBlink, 3000 + Math.random() * 2500);
      }, 160);
    };

    blinkTimer = setTimeout(triggerBlink, 3500);
    return () => clearTimeout(blinkTimer);
  }, []);

  // 2. Global mouse tracking - eyes & head follow cursor across the whole screen
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isTyping) return; // Freeze tracking while shy/turned away
      if (!containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const mascotCenterX = rect.left + rect.width / 2;
      const mascotCenterY = rect.top + rect.height / 2;

      const deltaX = e.clientX - mascotCenterX;
      const deltaY = e.clientY - mascotCenterY;
      const angle = Math.atan2(deltaY, deltaX);

      // Max eye pupil movement radius: 4.5px
      const eyeRadius = Math.min(4.5, Math.hypot(deltaX, deltaY) / 35);
      const px = Math.cos(angle) * eyeRadius;
      const py = Math.sin(angle) * eyeRadius;

      // Subtle 3D head rotation following cursor (max 14 degrees)
      const maxTilt = 14;
      const tiltY = Math.max(-maxTilt, Math.min(maxTilt, (deltaX / window.innerWidth) * (maxTilt * 2)));
      const tiltX = Math.max(-maxTilt, Math.min(maxTilt, (-deltaY / window.innerHeight) * (maxTilt * 2)));

      setPupilOffset({ x: px, y: py });
      setHeadTilt({ rotateX: tiltX, rotateY: tiltY });
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [isTyping]);

  // 3. Global input focus detection - monkey turns away when user types in any input/textarea
  useEffect(() => {
    if (externalIsTyping !== undefined) return;

    const handleFocusIn = (e: FocusEvent) => {
      const target = e.target as HTMLElement;
      if (
        target &&
        (target.tagName === 'INPUT' ||
          target.tagName === 'TEXTAREA' ||
          target.getAttribute('contenteditable') === 'true')
      ) {
        setInternalIsTyping(true);
      }
    };

    const handleFocusOut = () => {
      setInternalIsTyping(false);
    };

    window.addEventListener('focusin', handleFocusIn);
    window.addEventListener('focusout', handleFocusOut);

    return () => {
      window.removeEventListener('focusin', handleFocusIn);
      window.removeEventListener('focusout', handleFocusOut);
    };
  }, [externalIsTyping]);

  return (
    <div
      ref={containerRef}
      onClick={onClick}
      style={{ width: size, height: size }}
      className={`relative select-none cursor-pointer group ${className}`}
      title="Khỉ Trợ lý AI - Nhìn theo con trỏ chuột"
    >
      {/* Optional Speech Bubble */}
      {showSpeechBubble && !isTyping && (
        <div
          className={`absolute bottom-full right-2 mb-2 bg-white/95 backdrop-blur-xs text-slate-800 text-[11px] font-semibold px-3 py-1.5 rounded-2xl shadow-xl border border-amber-200/90 whitespace-nowrap pointer-events-none z-20 flex items-center gap-1.5 transition-all duration-300 transform ${
            isBubbleVisible ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-90 translate-y-1'
          }`}
        >
          <span>{MONKEY_QUOTES[quoteIndex]}</span>
          <div className="absolute -bottom-1.5 right-6 w-3 h-3 bg-white border-b border-r border-amber-200 rotate-45 transform" />
        </div>
      )}

      {/* Shy "Turning Away" speech indicator when user is typing */}
      {isTyping && (
        <div className="absolute bottom-full right-2 mb-2 bg-amber-500 text-white text-[10px] font-bold px-2.5 py-1 rounded-xl shadow-lg whitespace-nowrap z-20 animate-pulse pointer-events-none flex items-center gap-1">
          <span>Dạ em không nhìn trộm đâu ạ! 🙈</span>
          <div className="absolute -bottom-1.5 right-6 w-3 h-3 bg-amber-500 border-b border-r border-amber-600 rotate-45 transform" />
        </div>
      )}

      {/* 3D Container with Perspective */}
      <div
        className="w-full h-full relative transition-transform duration-300 ease-out"
        style={{
          perspective: '600px',
          transform: isTyping
            ? 'rotateY(42deg) rotateZ(10deg) translateX(-4px) translateY(2px)'
            : `rotateX(${headTilt.rotateX}deg) rotateY(${headTilt.rotateY}deg)`,
        }}
      >
        <svg
          viewBox="0 0 120 120"
          className="w-full h-full drop-shadow-md overflow-visible"
        >
          <defs>
            {/* Monkey Fur Gradient */}
            <radialGradient id="monkeyFur" cx="50%" cy="40%" r="60%">
              <stop offset="0%" stopColor="#9C6B48" />
              <stop offset="70%" stopColor="#7A4B2A" />
              <stop offset="100%" stopColor="#5E381C" />
            </radialGradient>

            {/* Inner Ear Gradient */}
            <radialGradient id="innerEar" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#FFE0B2" />
              <stop offset="100%" stopColor="#FFCC80" />
            </radialGradient>

            {/* Face Mask Gradient */}
            <linearGradient id="monkeyFaceMask" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#FFF3E0" />
              <stop offset="100%" stopColor="#FFE0B2" />
            </linearGradient>

            {/* Eye Highlight Gradient */}
            <radialGradient id="eyeGleam" cx="35%" cy="35%" r="65%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="40%" stopColor="#ECEFF1" />
              <stop offset="100%" stopColor="#CFD8DC" />
            </radialGradient>
          </defs>

          {/* 1. Left Ear */}
          <g>
            <circle cx="20" cy="54" r="17" fill="url(#monkeyFur)" stroke="#4E2B12" strokeWidth="2" />
            <circle cx="20" cy="54" r="10.5" fill="url(#innerEar)" opacity="0.9" />
          </g>

          {/* 2. Right Ear */}
          <g>
            <circle cx="100" cy="54" r="17" fill="url(#monkeyFur)" stroke="#4E2B12" strokeWidth="2" />
            <circle cx="100" cy="54" r="10.5" fill="url(#innerEar)" opacity="0.9" />
          </g>

          {/* 3. Main Head Base */}
          <circle
            cx="60"
            cy="58"
            r="44"
            fill="url(#monkeyFur)"
            stroke="#4E2B12"
            strokeWidth="2"
          />

          {/* 4. Top Hair Tufts */}
          <path
            d="M 53 16 Q 58 8 62 14 Q 67 9 69 17 Z"
            fill="#5E381C"
          />

          {/* 5. Heart-shaped Monkey Face Mask */}
          <g>
            {/* Left Eye Muzzle Area */}
            <ellipse cx="46" cy="50" rx="20" ry="21" fill="url(#monkeyFaceMask)" />
            {/* Right Eye Muzzle Area */}
            <ellipse cx="74" cy="50" rx="20" ry="21" fill="url(#monkeyFaceMask)" />
            {/* Lower Mouth / Cheeks */}
            <ellipse cx="60" cy="71" rx="25" ry="19" fill="url(#monkeyFaceMask)" />
          </g>

          {/* 6. Rosy Cheeks */}
          <ellipse cx="33" cy="67" rx="6" ry="3.5" fill="#FF8A80" opacity="0.45" />
          <ellipse cx="87" cy="67" rx="6" ry="3.5" fill="#FF8A80" opacity="0.45" />

          {/* 7. Eyes Section (Animated / Tracking / Shy) */}
          {isTyping ? (
            /* Shy Closed Eyes when typing / turning away */
            <g>
              <path
                d="M 38 52 Q 46 45 54 52"
                fill="none"
                stroke="#4E2B12"
                strokeWidth="3.2"
                strokeLinecap="round"
              />
              <path
                d="M 66 52 Q 74 45 82 52"
                fill="none"
                stroke="#4E2B12"
                strokeWidth="3.2"
                strokeLinecap="round"
              />
            </g>
          ) : isBlinking ? (
            /* Blinking horizontal slits */
            <g>
              <line x1="37" y1="52" x2="55" y2="52" stroke="#4E2B12" strokeWidth="3" strokeLinecap="round" />
              <line x1="65" y1="52" x2="83" y2="52" stroke="#4E2B12" strokeWidth="3" strokeLinecap="round" />
            </g>
          ) : (
            /* Active Eye Tracking mode */
            <g>
              {/* Left Eye White */}
              <ellipse cx="46" cy="50" rx="9" ry="11" fill="url(#eyeGleam)" stroke="#5D4037" strokeWidth="1.5" />
              {/* Left Pupil (Moves with cursor) */}
              <g transform={`translate(${pupilOffset.x}, ${pupilOffset.y})`}>
                <circle cx="46" cy="50" r="5.2" fill="#1A0C06" />
                {/* Shiny White Highlights */}
                <circle cx="44.2" cy="48" r="1.8" fill="#FFFFFF" />
                <circle cx="47.8" cy="52" r="0.9" fill="#FFFFFF" />
              </g>

              {/* Right Eye White */}
              <ellipse cx="74" cy="50" rx="9" ry="11" fill="url(#eyeGleam)" stroke="#5D4037" strokeWidth="1.5" />
              {/* Right Pupil (Moves with cursor) */}
              <g transform={`translate(${pupilOffset.x}, ${pupilOffset.y})`}>
                <circle cx="74" cy="50" r="5.2" fill="#1A0C06" />
                {/* Shiny White Highlights */}
                <circle cx="72.2" cy="48" r="1.8" fill="#FFFFFF" />
                <circle cx="75.8" cy="52" r="0.9" fill="#FFFFFF" />
              </g>

              {/* Expressive Eyebrows */}
              <path
                d={`M 38 ${40 + pupilOffset.y * 0.4} Q 46 ${36 + pupilOffset.y * 0.4} 54 ${39 + pupilOffset.y * 0.4}`}
                fill="none"
                stroke="#5D4037"
                strokeWidth="2.2"
                strokeLinecap="round"
              />
              <path
                d={`M 66 ${39 + pupilOffset.y * 0.4} Q 74 ${36 + pupilOffset.y * 0.4} 82 ${40 + pupilOffset.y * 0.4}`}
                fill="none"
                stroke="#5D4037"
                strokeWidth="2.2"
                strokeLinecap="round"
              />
            </g>
          )}

          {/* 8. Cute Monkey Nose */}
          <ellipse cx="57" cy="65" rx="1.6" ry="2.2" fill="#5D4037" />
          <ellipse cx="63" cy="65" rx="1.6" ry="2.2" fill="#5D4037" />

          {/* 9. Sweet Smile Mouth */}
          {isTyping ? (
            /* Cute shy circle mouth */
            <circle cx="60" cy="74" r="3" fill="#D84315" />
          ) : (
            /* Open happy smile */
            <g>
              <path
                d="M 50 72 Q 60 82 70 72"
                fill="none"
                stroke="#5D4037"
                strokeWidth="2.8"
                strokeLinecap="round"
              />
              {/* Tongue peak */}
              <path
                d="M 56 76 Q 60 80 64 76 Z"
                fill="#FF5252"
                opacity="0.9"
              />
            </g>
          )}

          {/* 10. Little Paws (Hands) */}
          {isTyping && (
            <g className="transition-all duration-300">
              {/* Left Paws covering side */}
              <ellipse cx="28" cy="60" rx="9" ry="12" fill="#7A4B2A" stroke="#4E2B12" strokeWidth="1.5" />
              <ellipse cx="28" cy="60" rx="5.5" ry="7.5" fill="#FFE0B2" />
              {/* Right Paws covering side */}
              <ellipse cx="92" cy="60" rx="9" ry="12" fill="#7A4B2A" stroke="#4E2B12" strokeWidth="1.5" />
              <ellipse cx="92" cy="60" rx="5.5" ry="7.5" fill="#FFE0B2" />
            </g>
          )}
        </svg>
      </div>
    </div>
  );
};
