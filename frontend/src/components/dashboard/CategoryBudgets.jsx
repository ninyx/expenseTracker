// Enhanced Category Budgets

import React, { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Wallet, PiggyBank, CreditCard, Calendar, AlertCircle, CheckCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export function CategoryBudgets({ categories }) {
  const categoriesWithBudgets = categories.filter(cat => cat.budget && cat.budget > 0);

  if (categoriesWithBudgets.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-12 text-center">
        <div className="text-6xl mb-4">💰</div>
        <p className="text-lg font-medium text-gray-700 mb-2">No Budget Tracking Yet</p>
        <p className="text-gray-500">Set up category budgets to track your spending</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <PiggyBank className="w-5 h-5 text-indigo-600" />
          Budget Overview
        </h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {categoriesWithBudgets.map((cat) => {
          const percentage = ((cat.budget_used || 0) / cat.budget) * 100;
          const isOverBudget = percentage >= 100;
          const isWarning = percentage >= 80 && percentage < 100;
          
          return (
            <div key={cat.uid} className="border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{cat.name}</h4>
                  <p className="text-xs text-gray-500 mt-1 capitalize">{cat.frequency}</p>
                </div>
                <div className="flex items-center gap-1">
                  {isOverBudget ? (
                    <AlertCircle className="w-5 h-5 text-red-500" />
                  ) : isWarning ? (
                    <AlertCircle className="w-5 h-5 text-yellow-500" />
                  ) : (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  )}
                </div>
              </div>
              
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>₱{(cat.budget_used || 0).toLocaleString()}</span>
                  <span>₱{cat.budget.toLocaleString()}</span>
                </div>
                <div className="relative h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className={`absolute h-full rounded-full transition-all duration-700 ${
                      isOverBudget ? 'bg-red-500' : isWarning ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  />
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className={`text-sm font-bold ${
                  isOverBudget ? 'text-red-600' : isWarning ? 'text-yellow-600' : 'text-green-600'
                }`}>
                  {percentage.toFixed(1)}%
                </span>
                <span className="text-xs text-gray-500">
                  ₱{(cat.budget - (cat.budget_used || 0)).toLocaleString()} left
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
