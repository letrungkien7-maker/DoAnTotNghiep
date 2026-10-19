import React, { useState } from 'react';
import { Calculator, DollarSign, Calendar, Percent, ShieldCheck, ArrowRight, Building } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const MortgageCalculator: React.FC = () => {
  const navigate = useNavigate();

  // State
  const [propertyPrice, setPropertyPrice] = useState<number>(3500000000); // 3.5 tỷ
  const [downPaymentPercent, setDownPaymentPercent] = useState<number>(30); // 30% trả trước -> vay 70%
  const [loanTermYears, setLoanTermYears] = useState<number>(20); // 20 năm
  const [annualInterestRate, setAnnualInterestRate] = useState<number>(7.5); // 7.5%

  // Calculations
  const loanPercent = 100 - downPaymentPercent;
  const downPaymentAmount = (propertyPrice * downPaymentPercent) / 100;
  const loanAmount = (propertyPrice * loanPercent) / 100;
  const totalMonths = loanTermYears * 12;

  // Monthly Principal
  const monthlyPrincipal = totalMonths > 0 ? loanAmount / totalMonths : 0;
  // First month interest
  const monthlyInterestFirst = (loanAmount * (annualInterestRate / 100)) / 12;
  // First month total
  const firstMonthTotal = monthlyPrincipal + monthlyInterestFirst;

  const formatVND = (num: number): string => {
    if (num >= 1000000000) {
      return `${(num / 1000000000).toFixed(2)} tỷ đ`;
    }
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)} triệu đ`;
    }
    return `${Math.round(num).toLocaleString('vi-VN')} đ`;
  };

  const handleSearchByBudget = () => {
    navigate(`/search?max_price=${propertyPrice}&transaction_type=SALE`);
  };

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-blue-950 rounded-3xl p-6 sm:p-10 text-white shadow-2xl relative overflow-hidden border border-blue-900/50">
        {/* Ambient background glows */}
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />

        {/* Header */}
        <div className="relative z-10 max-w-2xl mb-8">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30 text-xs font-bold uppercase tracking-wider mb-3">
            <Calculator className="w-3.5 h-3.5 text-amber-300" />
            <span>Công cụ tài chính thông minh</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Ước Tính Khoản Vay & Trả Góp Mua Nhà
          </h2>
          <p className="text-sm text-gray-300 mt-2">
            Mô phỏng kế hoạch tài chính dễ dàng với lãi suất ngân hàng cập nhật, giúp bạn chủ động đưa ra quyết định an cư.
          </p>
        </div>

        {/* Main Grid */}
        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Inputs Column */}
          <div className="lg:col-span-7 space-y-6 bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
            {/* Property Price Slider */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-gray-200 flex items-center space-x-1.5">
                  <Building className="w-4 h-4 text-blue-400" />
                  <span>Giá trị nhà đất dự kiến</span>
                </span>
                <span className="text-lg font-extrabold text-amber-300">
                  {formatVND(propertyPrice)}
                </span>
              </div>
              <input
                type="range"
                min={500000000}
                max={15000000000}
                step={100000000}
                value={propertyPrice}
                onChange={(e) => setPropertyPrice(Number(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              {/* Quick selector chips */}
              <div className="flex flex-wrap gap-2 pt-1">
                {[1500000000, 2500000000, 3500000000, 5000000000, 8000000000].map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => setPropertyPrice(val)}
                    className={`px-2.5 py-1 text-xs rounded-lg border transition font-medium ${
                      propertyPrice === val
                        ? 'bg-blue-600 border-blue-400 text-white shadow-xs'
                        : 'bg-white/5 border-white/10 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    {formatVND(val)}
                  </button>
                ))}
              </div>
            </div>

            {/* Down Payment Percent Slider */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-gray-200 flex items-center space-x-1.5">
                  <DollarSign className="w-4 h-4 text-emerald-400" />
                  <span>Vốn tự có (Trả trước)</span>
                </span>
                <span className="text-sm font-bold text-emerald-300">
                  {downPaymentPercent}% ({formatVND(downPaymentAmount)})
                </span>
              </div>
              <input
                type="range"
                min={20}
                max={70}
                step={5}
                value={downPaymentPercent}
                onChange={(e) => setDownPaymentPercent(Number(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex justify-between text-[11px] text-gray-400">
                <span>Tối thiểu 20%</span>
                <span>Tỷ lệ vay ngân hàng: <strong className="text-blue-300">{loanPercent}%</strong></span>
                <span>Tối đa 70%</span>
              </div>
            </div>

            {/* Loan Term & Interest Rate in 2 Cols */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Loan Term */}
              <div className="space-y-2 bg-white/5 p-4 rounded-xl border border-white/10">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-gray-300 flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Thời hạn vay</span>
                  </span>
                  <span className="font-bold text-white text-sm">{loanTermYears} năm</span>
                </div>
                <input
                  type="range"
                  min={5}
                  max={35}
                  step={5}
                  value={loanTermYears}
                  onChange={(e) => setLoanTermYears(Number(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                />
              </div>

              {/* Interest Rate */}
              <div className="space-y-2 bg-white/5 p-4 rounded-xl border border-white/10">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-gray-300 flex items-center space-x-1">
                    <Percent className="w-3.5 h-3.5 text-amber-400" />
                    <span>Lãi suất ưu đãi</span>
                  </span>
                  <span className="font-bold text-white text-sm">{annualInterestRate}% /năm</span>
                </div>
                <input
                  type="range"
                  min={5.0}
                  max={13.0}
                  step={0.5}
                  value={annualInterestRate}
                  onChange={(e) => setAnnualInterestRate(Number(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
                />
              </div>
            </div>
          </div>

          {/* Result Summary Card Column */}
          <div className="lg:col-span-5 bg-gradient-to-b from-blue-900/60 to-slate-900/80 backdrop-blur-xl p-6 rounded-2xl border border-blue-500/30 shadow-xl flex flex-col justify-between space-y-6">
            <div>
              <div className="text-xs uppercase tracking-wider font-bold text-blue-300 mb-1">
                Thanh toán ước tính tháng đầu
              </div>
              <div className="text-3xl sm:text-4xl font-black text-amber-300 tracking-tight">
                {formatVND(firstMonthTotal)}
                <span className="text-xs font-semibold text-gray-300 ml-1">/ tháng</span>
              </div>
              <p className="text-[11px] text-gray-400 mt-1">
                * Áp dụng phương thức trả góp dư nợ giảm dần (tiền lãi giảm dần theo các tháng sau).
              </p>

              {/* Breakdown details */}
              <div className="mt-6 space-y-3 pt-5 border-t border-white/10 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-300">Vốn tự có (cần chuẩn bị):</span>
                  <span className="font-bold text-emerald-300">{formatVND(downPaymentAmount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Khoản vay ngân hàng:</span>
                  <span className="font-bold text-blue-300">{formatVND(loanAmount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Tiền gốc cố định mỗi tháng:</span>
                  <span className="font-medium text-white">{formatVND(monthlyPrincipal)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Tiền lãi tháng đầu tiên:</span>
                  <span className="font-medium text-amber-300">{formatVND(monthlyInterestFirst)}</span>
                </div>
              </div>

              {/* Ratio bar */}
              <div className="mt-5 space-y-1.5">
                <div className="flex justify-between text-[11px] font-semibold text-gray-300">
                  <span className="text-emerald-400">Tự có: {downPaymentPercent}%</span>
                  <span className="text-blue-400">Vay: {loanPercent}%</span>
                </div>
                <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden flex">
                  <div
                    className="bg-emerald-500 h-full transition-all duration-300"
                    style={{ width: `${downPaymentPercent}%` }}
                  />
                  <div
                    className="bg-blue-500 h-full transition-all duration-300"
                    style={{ width: `${loanPercent}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Action button */}
            <div className="pt-2">
              <button
                type="button"
                onClick={handleSearchByBudget}
                className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-sm rounded-xl transition-all shadow-lg flex items-center justify-center space-x-2 group cursor-pointer"
              >
                <span>Tìm BĐS theo mức tài chính này</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
              <div className="mt-3 flex items-center justify-center space-x-1 text-[11px] text-gray-400">
                <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                <span>Hỗ trợ hồ sơ vay vốn từ các đối tác ngân hàng hàng đầu</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
