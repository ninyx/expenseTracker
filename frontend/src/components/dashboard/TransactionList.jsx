import { useState } from 'react';
import { TrendingUp, TrendingDown, Wallet, PiggyBank, CreditCard, Calendar, AlertCircle, CheckCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react';


// Enhanced Transaction List
export function TransactionsList({ transactions, accounts, categories }) {
  if (!transactions || transactions.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-12 text-center">
        <div className="text-6xl mb-4">📝</div>
        <p className="text-lg font-medium text-gray-700 mb-2">No Recent Transactions</p>
        <p className="text-gray-500">Your recent transactions will appear here</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      <div className="p-6 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <CreditCard className="w-5 h-5 text-blue-600" />
          Recent Transactions
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {transactions.map((tx) => {
              const isIncome = tx.transaction_type === 'income';
              const isExpense = tx.transaction_type === 'expense';
              
              return (
                <tr key={tx.uid} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {new Date(tx.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="flex items-center gap-2">
                      {isIncome && <TrendingUp className="w-4 h-4 text-green-500" />}
                      {isExpense && <TrendingDown className="w-4 h-4 text-red-500" />}
                      <span className="font-medium">{tx.description || 'No description'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {tx.category_name || '—'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {tx.account_name || tx.from_account_name || '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold">
                    <span className={isIncome ? 'text-green-600' : isExpense ? 'text-red-600' : 'text-blue-600'}>
                      {isIncome ? '+' : isExpense ? '-' : ''}₱{tx.amount.toLocaleString()}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}