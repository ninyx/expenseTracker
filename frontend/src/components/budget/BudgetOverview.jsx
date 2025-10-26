// frontend/src/components/budget/BudgetOverview.jsx
export default function BudgetOverview({ totalBudget, totalUsed, frequency }) {
  const remaining = totalBudget - totalUsed;
  const percentageUsed = totalBudget > 0 ? (totalUsed / totalBudget) * 100 : 0;

  const getStatusColor = (percentage) => {
    if (percentage >= 100) return "text-red-600";
    if (percentage >= 80) return "text-yellow-600";
    return "text-green-600";
  };

  const cards = [
    {
      label: "Total Budget",
      value: totalBudget,
      icon: "💼",
      color: "bg-blue-100 text-blue-600",
    },
    {
      label: "Total Used",
      value: totalUsed,
      icon: "💸",
      color: "bg-purple-100 text-purple-600",
    },
    {
      label: "Remaining",
      value: remaining,
      icon: "💰",
      color: remaining < 0 ? "bg-red-100 text-red-600" : "bg-green-100 text-green-600",
    },
  ];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((card) => (
          <div key={card.label} className="bg-white rounded-lg shadow-md p-6 border">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-600 text-sm font-medium">{card.label}</p>
              <span className="text-2xl">{card.icon}</span>
            </div>
            <p className={`text-3xl font-bold ${card.color.split(' ')[1]}`}>
              ₱{card.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
            <p className="text-xs text-gray-500 mt-1 capitalize">
              {frequency} Budget
            </p>
          </div>
        ))}
      </div>

      {/* Overall Progress Bar */}
      <div className="bg-white rounded-lg shadow-md p-6 border">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-semibold text-lg">Overall Budget Usage</h3>
          <span className={`text-2xl font-bold ${getStatusColor(percentageUsed)}`}>
            {percentageUsed.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden">
          <div
            className={`h-6 rounded-full transition-all duration-500 ${
              percentageUsed >= 100
                ? "bg-red-500"
                : percentageUsed >= 80
                ? "bg-yellow-500"
                : "bg-green-500"
            }`}
            style={{ width: `${Math.min(percentageUsed, 100)}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-sm text-gray-600">
          <span>₱{totalUsed.toLocaleString()}</span>
          <span>₱{totalBudget.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}