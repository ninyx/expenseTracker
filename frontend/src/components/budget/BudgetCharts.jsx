// frontend/src/components/budget/BudgetCharts.jsx
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";

export default function BudgetCharts({ categories }) {
  const COLORS = [
    "#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6",
    "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#84cc16"
  ];

  // Flatten categories for charts
  const flattenCategories = (cats, result = []) => {
    cats.forEach((cat) => {
      if (cat.budget > 0) {
        result.push({
          name: cat.name,
          budget: cat.budget,
          used: cat.budget_used || 0,
          remaining: Math.max(0, cat.budget - (cat.budget_used || 0)),
          overBudget: Math.max(0, (cat.budget_used || 0) - cat.budget),
          percentage: cat.budget > 0 ? ((cat.budget_used || 0) / cat.budget) * 100 : 0,
        });
      }
      if (cat.children) {
        flattenCategories(cat.children, result);
      }
    });
    return result;
  };

  const chartData = flattenCategories(categories);

  // Data for pie chart (budget allocation)
  const pieData = chartData.map((cat) => ({
    name: cat.name,
    value: cat.budget,
  }));

  // Data for bar chart (budget vs used)
  const barData = chartData.slice(0, 10); // Top 10 categories

  // Data for spending efficiency (percentage used)
  const efficiencyData = chartData
    .map((cat) => ({
      category: cat.name,
      percentage: Math.min(cat.percentage, 100),
    }))
    .slice(0, 8);

  // Data for over/under budget
  const budgetStatusData = chartData.slice(0, 8).map((cat) => ({
    name: cat.name,
    remaining: cat.remaining,
    overBudget: cat.overBudget,
  }));

  // Custom tooltip for pie chart
  const CustomPieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded shadow-lg">
          <p className="font-semibold">{payload[0].name}</p>
          <p className="text-sm text-gray-600">
            Budget: ₱{payload[0].value.toLocaleString()}
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for bar chart
  const CustomBarTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded shadow-lg">
          <p className="font-semibold mb-2">{payload[0].payload.name}</p>
          <p className="text-sm text-blue-600">
            Budget: ₱{payload[0].value.toLocaleString()}
          </p>
          <p className="text-sm text-red-600">
            Used: ₱{payload[1].value.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            Status: {payload[0].payload.percentage.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom label for pie chart
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return percent > 0.05 ? (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central"
        className="text-xs font-semibold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    ) : null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Summary Statistics */}
      <div className="bg-white rounded-lg shadow-md p-6 border lg:col-span-2">
        <h3 className="text-lg font-semibold mb-4">📋 Budget Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-gray-600 mb-1">Total Categories</p>
            <p className="text-2xl font-bold text-blue-600">{chartData.length}</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <p className="text-sm text-gray-600 mb-1">Under Budget</p>
            <p className="text-2xl font-bold text-green-600">
              {chartData.filter((c) => c.percentage < 100).length}
            </p>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <p className="text-sm text-gray-600 mb-1">Near Limit (80%+)</p>
            <p className="text-2xl font-bold text-yellow-600">
              {chartData.filter((c) => c.percentage >= 80 && c.percentage < 100).length}
            </p>
          </div>
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <p className="text-sm text-gray-600 mb-1">Over Budget</p>
            <p className="text-2xl font-bold text-red-600">
              {chartData.filter((c) => c.percentage >= 100).length}
            </p>
          </div>
        </div>
      </div>

      {/* Budget Allocation Pie Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 border">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold">📊 Budget Allocation</h3>
            <p className="text-sm text-gray-600">Distribution across categories</p>
          </div>
        </div>
        {pieData.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center text-gray-400">
            <div className="text-center">
              <div className="text-4xl mb-2">📊</div>
              <p>No budget data to display</p>
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomLabel}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomPieTooltip />} />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value, entry) => (
                  <span className="text-xs">
                    {value}
                  </span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Budget vs Used Bar Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 border">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold">📈 Budget vs. Actual Spending</h3>
            <p className="text-sm text-gray-600">Top 10 categories comparison</p>
          </div>
        </div>
        {barData.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center text-gray-400">
            <div className="text-center">
              <div className="text-4xl mb-2">📈</div>
              <p>No spending data to display</p>
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="name"
                angle={-45}
                textAnchor="end"
                height={100}
                tick={{ fontSize: 12 }}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip content={<CustomBarTooltip />} />
              <Legend />
              <Bar dataKey="budget" fill="#3b82f6" name="Budget" radius={[8, 8, 0, 0]} />
              <Bar dataKey="used" fill="#ef4444" name="Used" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Spending Efficiency Line Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 border">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold">⚡ Spending Efficiency</h3>
            <p className="text-sm text-gray-600">Percentage of budget used</p>
          </div>
        </div>
        {efficiencyData.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center text-gray-400">
            <div className="text-center">
              <div className="text-4xl mb-2">⚡</div>
              <p>No efficiency data to display</p>
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={efficiencyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="category"
                angle={-45}
                textAnchor="end"
                height={100}
                tick={{ fontSize: 12 }}
              />
              <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} />
              <Tooltip
                formatter={(value) => `${value.toFixed(1)}%`}
                labelStyle={{ color: "#000" }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="percentage"
                stroke="#8b5cf6"
                strokeWidth={3}
                dot={{ fill: "#8b5cf6", r: 5 }}
                name="Usage %"
              />
              {/* Reference line at 100% */}
              <Line
                type="monotone"
                data={efficiencyData.map(d => ({ ...d, limit: 100 }))}
                dataKey="limit"
                stroke="#ef4444"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Budget Limit"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Over/Under Budget Comparison */}
      <div className="bg-white rounded-lg shadow-md p-6 border">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold">💸 Budget Status</h3>
            <p className="text-sm text-gray-600">Remaining vs. over budget</p>
          </div>
        </div>
        {budgetStatusData.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center text-gray-400">
            <div className="text-center">
              <div className="text-4xl mb-2">💸</div>
              <p>No status data to display</p>
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={budgetStatusData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="name"
                angle={-45}
                textAnchor="end"
                height={100}
                tick={{ fontSize: 12 }}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                formatter={(value) => `₱${Math.abs(value).toLocaleString()}`}
                labelStyle={{ color: "#000" }}
              />
              <Legend />
              <Bar
                dataKey="remaining"
                fill="#10b981"
                name="Remaining"
                radius={[8, 8, 0, 0]}
              />
              <Bar
                dataKey="overBudget"
                fill="#ef4444"
                name="Over Budget"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      
    </div>
  );
}