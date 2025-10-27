// frontend/src/components/accounts/AccountSummary.jsx
export default function AccountSummary({ accounts }) {
  const totalBalance = accounts.reduce((sum, acc) => sum + (acc.balance || 0), 0);
  
  // Calculate total monthly interest across all accounts
  const totalMonthlyInterest = accounts.reduce((sum, acc) => {
    if (!acc.interest_rate || acc.interest_rate === 0) return sum;
    
    const annualRate = acc.interest_rate / 100;
    const frequency = acc.interest_frequency || "monthly";
    
    let interest = 0;
    switch(frequency) {
      case "monthly":
        interest = (acc.balance * annualRate) / 12;
        break;
      case "quarterly":
        interest = (acc.balance * annualRate) / 4;
        break;
      case "annually":
        interest = acc.balance * annualRate;
        break;
      default:
        interest = (acc.balance * annualRate) / 12;
    }
    
    return sum + interest;
  }, 0);

  // Calculate annual interest projection
  const totalAnnualInterest = accounts.reduce((sum, acc) => {
    if (!acc.interest_rate || acc.interest_rate === 0) return sum;
    return sum + (acc.balance * (acc.interest_rate / 100));
  }, 0);

  const accountsWithInterest = accounts.filter(acc => acc.interest_rate && acc.interest_rate > 0).length;
  
  // Calculate average interest rate (weighted by balance)
  const totalInterestBearing = accounts
    .filter(acc => acc.interest_rate && acc.interest_rate > 0)
    .reduce((sum, acc) => sum + acc.balance, 0);
  
  const weightedAverageRate = totalInterestBearing > 0
    ? accounts
        .filter(acc => acc.interest_rate && acc.interest_rate > 0)
        .reduce((sum, acc) => sum + (acc.balance * acc.interest_rate), 0) / totalInterestBearing
    : 0;

  const stats = [
    {
      label: "Total Balance",
      value: `₱${totalBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: "💰",
      color: "bg-blue-100 text-blue-700 border-blue-200",
      subtext: `Across ${accounts.length} accounts`
    },
    {
      label: "Monthly Interest",
      value: `₱${totalMonthlyInterest.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: "📈",
      color: "bg-green-100 text-green-700 border-green-200",
      subtext: accountsWithInterest > 0 ? `From ${accountsWithInterest} earning accounts` : "No earning accounts"
    },
    {
      label: "Annual Projection",
      value: `₱${totalAnnualInterest.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: "✨",
      color: "bg-purple-100 text-purple-700 border-purple-200",
      subtext: "Estimated yearly interest"
    },
    {
      label: "Avg Interest Rate",
      value: `${weightedAverageRate.toFixed(2)}%`,
      icon: "📊",
      color: "bg-yellow-100 text-yellow-700 border-yellow-200",
      subtext: accountsWithInterest > 0 ? "Weighted by balance" : "No rates set"
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className={`${stat.color} rounded-xl p-6 border shadow-sm hover:shadow-md transition-shadow`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-3xl">{stat.icon}</span>
          </div>
          <p className="text-sm font-medium opacity-80 mb-1">{stat.label}</p>
          <p className="text-2xl font-bold mb-1">{stat.value}</p>
          <p className="text-xs opacity-70">{stat.subtext}</p>
        </div>
      ))}
    </div>
  );
}