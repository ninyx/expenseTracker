// frontend/src/components/budget/BudgetProgress.jsx
export default function BudgetProgress({ categories }) {
  const renderProgress = (cat, depth = 0) => {
    if (!cat.budget || cat.budget === 0) return null;

    const percentage = ((cat.budget_used || 0) / cat.budget) * 100;
    const remaining = cat.budget - (cat.budget_used || 0);

    const getProgressColor = (pct) => {
      if (pct >= 100) return "bg-red-500";
      if (pct >= 80) return "bg-yellow-500";
      if (pct >= 60) return "bg-orange-500";
      return "bg-green-500";
    };

    const getTextColor = (pct) => {
      if (pct >= 100) return "text-red-600";
      if (pct >= 80) return "text-yellow-600";
      if (pct >= 60) return "text-orange-600";
      return "text-green-600";
    };

    const getStatusEmoji = (pct) => {
      if (pct >= 100) return "🚨";
      if (pct >= 80) return "⚠️";
      if (pct >= 60) return "⚡";
      return "✅";
    };

    const getStatusText = (pct) => {
      if (pct >= 100) return "Over Budget!";
      if (pct >= 80) return "Almost There";
      if (pct >= 60) return "On Track";
      return "Looking Good";
    };

    return (
      <div key={cat.uid} className={depth > 0 ? "ml-6" : ""}>
        <div className="bg-white rounded-lg p-5 shadow-md border hover:shadow-lg transition-shadow mb-4">
          <div className="flex justify-between items-start mb-3">
            <div className="flex-1">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                {depth > 0 && <span className="text-gray-400">└─</span>}
                <span>{cat.name}</span>
              </h4>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium capitalize">
                  {cat.transaction_type}
                </span>
                <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full font-medium capitalize">
                  {cat.frequency}
                </span>
              </div>
            </div>
            <div className="text-right">
              <p className={`text-3xl font-bold ${getTextColor(percentage)}`}>
                {percentage.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-600 mt-1 flex items-center gap-1 justify-end">
                <span>{getStatusEmoji(percentage)}</span>
                <span>{getStatusText(percentage)}</span>
              </p>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden shadow-inner">
              <div
                className={`h-4 rounded-full transition-all duration-700 ease-out ${getProgressColor(
                  percentage
                )}`}
                style={{ width: `${Math.min(percentage, 100)}%` }}
              />
            </div>
            <div className="flex justify-between mt-1 text-xs text-gray-500">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-4 text-sm mb-3">
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
              <p className="text-gray-600 text-xs mb-1">Budget</p>
              <p className="font-bold text-blue-700">₱{cat.budget.toLocaleString()}</p>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg border border-purple-100">
              <p className="text-gray-600 text-xs mb-1">Used</p>
              <p className="font-bold text-purple-700">
                ₱{(cat.budget_used || 0).toLocaleString()}
              </p>
            </div>
            <div className={`p-3 rounded-lg border ${
              remaining < 0 
                ? "bg-red-50 border-red-100" 
                : "bg-green-50 border-green-100"
            }`}>
              <p className="text-gray-600 text-xs mb-1">Remaining</p>
              <p
                className={`font-bold ${
                  remaining < 0 ? "text-red-700" : "text-green-700"
                }`}
              >
                ₱{remaining.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Daily Average (for monthly budgets) */}
          {cat.frequency === "monthly" && (
            <div className="text-xs text-gray-600 mb-3 flex items-center gap-2">
              <span>📅</span>
              <span>
                Daily average: ₱{((cat.budget_used || 0) / new Date().getDate()).toFixed(2)} 
                (Target: ₱{(cat.budget / 30).toFixed(2)}/day)
              </span>
            </div>
          )}

          {/* Warning Messages */}
          {percentage >= 100 && (
            <div className="mt-3 p-3 bg-red-50 border-l-4 border-red-500 rounded text-sm text-red-800">
              <p className="font-semibold flex items-center gap-2">
                <span>🚨</span>
                <span>Budget Exceeded!</span>
              </p>
              <p className="mt-1">
                You've gone over budget by <strong>₱{Math.abs(remaining).toLocaleString()}</strong>. 
                Consider reducing spending in this category.
              </p>
            </div>
          )}

          {percentage >= 80 && percentage < 100 && (
            <div className="mt-3 p-3 bg-yellow-50 border-l-4 border-yellow-500 rounded text-sm text-yellow-800">
              <p className="font-semibold flex items-center gap-2">
                <span>⚠️</span>
                <span>Approaching Limit</span>
              </p>
              <p className="mt-1">
                You've used <strong>{percentage.toFixed(1)}%</strong> of your budget. 
                Only <strong>₱{remaining.toLocaleString()}</strong> remaining.
              </p>
            </div>
          )}

          {percentage >= 60 && percentage < 80 && (
            <div className="mt-3 p-3 bg-orange-50 border-l-4 border-orange-500 rounded text-sm text-orange-800">
              <p className="font-semibold flex items-center gap-2">
                <span>⚡</span>
                <span>Keep an Eye Out</span>
              </p>
              <p className="mt-1">
                You're at <strong>{percentage.toFixed(1)}%</strong> of your budget. 
                You have <strong>₱{remaining.toLocaleString()}</strong> left to spend.
              </p>
            </div>
          )}

          {percentage < 60 && (
            <div className="mt-3 p-3 bg-green-50 border-l-4 border-green-500 rounded text-sm text-green-800">
              <p className="font-semibold flex items-center gap-2">
                <span>✅</span>
                <span>On Track</span>
              </p>
              <p className="mt-1">
                Great job! You're managing your budget well. 
                <strong> ₱{remaining.toLocaleString()}</strong> still available.
              </p>
            </div>
          )}
        </div>

        {/* Render Children */}
        {cat.children &&
          cat.children.map((child) => renderProgress(child, depth + 1))}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold text-gray-800">📊 Detailed Budget Progress</h2>
          <p className="text-sm text-gray-600 mt-1">Track spending and monitor budget health</p>
        </div>
      </div>
      
      {categories.length === 0 ? (
        <div className="bg-white rounded-lg p-12 text-center text-gray-500 border shadow-sm">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-lg font-medium mb-2">No Budget Data Available</p>
          <p className="text-sm">No categories with budgets found for this frequency period.</p>
          <p className="text-sm mt-2 text-gray-400">
            Try switching to a different frequency or set up budgets in the Categories section.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {categories.map((cat) => renderProgress(cat))}
        </div>
      )}
    </div>
  );
}