// src/components/dashboard/DashboardCharts.jsx
import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from "recharts";

export default function DashboardCharts({ totals, categories, accounts }) {
  const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6", "#a855f7"];

  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold mb-2">Visual Overview</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* INCOME vs EXPENSE BAR */}
        <ChartCard title="Income vs Expense">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={[
              { name: "Income", amount: totals.income },
              { name: "Expense", amount: totals.expense },
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="amount" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* EXPENSE PIE */}
        <ChartCard title="Expense Breakdown by Category">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={categories
                  .filter(c => c.transaction_type === "expense" && c.budget > 0)
                  .map(c => ({ name: c.name, value: c.budget_used || 0 }))}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label
              >
                {categories.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* ACCOUNT BALANCE BAR */}
        <ChartCard title="Account Balances">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={accounts.map(a => ({ name: a.name, balance: a.balance || 0 }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="balance" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="bg-white p-4 rounded shadow-sm border">
      <h3 className="text-sm font-medium mb-2">{title}</h3>
      {children}
    </div>
  );
}
