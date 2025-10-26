import React, { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Wallet, PiggyBank, CreditCard, Calendar, AlertCircle, CheckCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react';


// Enhanced Charts Component
export function DashboardCharts({ totals, categories, accounts }) {
  const [chartView, setChartView] = useState('overview');

  // Prepare category spending data
  const categoryData = categories
    .filter(cat => cat.budget_used > 0)
    .sort((a, b) => b.budget_used - a.budget_used)
    .slice(0, 5);

  const maxCategorySpend = Math.max(...categoryData.map(c => c.budget_used), 1);

  // Account distribution
  const totalAccountBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0) || 1;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Income vs Expenses */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-6 flex items-center gap-2">
          <CreditCard className="w-5 h-5 text-blue-600" />
          Income vs Expenses
        </h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Income</span>
              <span className="text-sm font-bold text-green-600">₱{totals.income.toLocaleString()}</span>
            </div>
            <div className="relative h-8 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="absolute h-full bg-gradient-to-r from-green-400 to-green-600 rounded-full transition-all duration-700"
                style={{ width: `${totals.income > 0 ? 100 : 0}%` }}
              />
            </div>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Expenses</span>
              <span className="text-sm font-bold text-red-600">₱{totals.expense.toLocaleString()}</span>
            </div>
            <div className="relative h-8 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="absolute h-full bg-gradient-to-r from-red-400 to-red-600 rounded-full transition-all duration-700"
                style={{ width: `${totals.income > 0 ? (totals.expense / totals.income * 100) : 0}%` }}
              />
            </div>
          </div>

          <div className="pt-4 border-t mt-6">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">Net Balance</span>
              <span className={`text-lg font-bold ${totals.income - totals.expense >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ₱{(totals.income - totals.expense).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Spending Categories */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-6 flex items-center gap-2">
          <TrendingDown className="w-5 h-5 text-purple-600" />
          Top Spending Categories
        </h3>
        <div className="space-y-4">
          {categoryData.length > 0 ? (
            categoryData.map((cat, idx) => {
              const percentage = (cat.budget_used / maxCategorySpend) * 100;
              const colors = ['bg-purple-500', 'bg-blue-500', 'bg-indigo-500', 'bg-pink-500', 'bg-cyan-500'];
              return (
                <div key={cat.uid}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700 truncate">{cat.name}</span>
                    <span className="text-sm font-bold text-gray-900">₱{cat.budget_used.toLocaleString()}</span>
                  </div>
                  <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className={`absolute h-full ${colors[idx % colors.length]} rounded-full transition-all duration-700`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })
          ) : (
            <div className="text-center py-8 text-gray-400">
              <p>No spending data available</p>
            </div>
          )}
        </div>
      </div>

      {/* Account Distribution */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-6 flex items-center gap-2">
          <Wallet className="w-5 h-5 text-teal-600" />
          Account Distribution
        </h3>
        <div className="space-y-4">
          {accounts.length > 0 ? (
            accounts.map((acc) => {
              const percentage = (acc.balance / totalAccountBalance) * 100;
              return (
                <div key={acc.uid}>
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-700 truncate">{acc.name}</span>
                      <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full capitalize">{acc.type}</span>
                    </div>
                    <span className="text-sm font-bold text-gray-900">₱{acc.balance.toLocaleString()}</span>
                  </div>
                  <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="absolute h-full bg-gradient-to-r from-teal-400 to-teal-600 rounded-full transition-all duration-700"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })
          ) : (
            <div className="text-center py-8 text-gray-400">
              <p>No accounts available</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-6 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-orange-600" />
          Quick Stats
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
            <p className="text-xs text-blue-600 font-medium mb-1">Accounts</p>
            <p className="text-2xl font-bold text-blue-700">{accounts.length}</p>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4">
            <p className="text-xs text-purple-600 font-medium mb-1">Categories</p>
            <p className="text-2xl font-bold text-purple-700">{categories.length}</p>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
            <p className="text-xs text-green-600 font-medium mb-1">Savings Rate</p>
            <p className="text-2xl font-bold text-green-700">
              {totals.income > 0 ? (((totals.income - totals.expense) / totals.income) * 100).toFixed(1) : 0}%
            </p>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4">
            <p className="text-xs text-orange-600 font-medium mb-1">Budget Used</p>
            <p className="text-2xl font-bold text-orange-700">
              {categories.reduce((sum, cat) => sum + (cat.budget_used || 0), 0).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
