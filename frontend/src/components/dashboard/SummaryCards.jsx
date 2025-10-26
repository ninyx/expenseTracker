import React from 'react';
import { TrendingUp, TrendingDown, Wallet, PiggyBank, CreditCard, Calendar, AlertCircle, CheckCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react';


export function SummaryCards({ totals }) {
  const netIncome = totals.income - totals.expense;
  const savingsRate = totals.income > 0 ? ((netIncome / totals.income) * 100).toFixed(1) : 0;

  const cards = [
    {
      title: "Total Balance",
      value: totals.balance,
      icon: Wallet,
      color: "from-blue-500 to-blue-600",
      bgLight: "bg-blue-50",
      textColor: "text-blue-700",
      trend: null
    },
    {
      title: "Total Income",
      value: totals.income,
      icon: TrendingUp,
      color: "from-green-500 to-green-600",
      bgLight: "bg-green-50",
      textColor: "text-green-700",
      trend: "+12.5%"
    },
    {
      title: "Total Expenses",
      value: totals.expense,
      icon: TrendingDown,
      color: "from-red-500 to-red-600",
      bgLight: "bg-red-50",
      textColor: "text-red-700",
      trend: "-8.3%"
    },
    {
      title: "Net Savings",
      value: netIncome,
      icon: PiggyBank,
      color: netIncome >= 0 ? "from-purple-500 to-purple-600" : "from-orange-500 to-orange-600",
      bgLight: netIncome >= 0 ? "bg-purple-50" : "bg-orange-50",
      textColor: netIncome >= 0 ? "text-purple-700" : "text-orange-700",
      trend: `${savingsRate}% rate`
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <div className={`h-2 bg-gradient-to-r ${card.color}`} />
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl ${card.bgLight}`}>
                  <Icon className={`w-6 h-6 ${card.textColor}`} />
                </div>
                {card.trend && (
                  <span className={`text-xs font-semibold ${card.textColor} flex items-center gap-1`}>
                    {card.trend.startsWith('+') ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {card.trend}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 mb-2">{card.title}</p>
              <p className="text-3xl font-bold text-gray-900">
                ₱{Math.abs(card.value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
