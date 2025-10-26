// frontend/src/components/accounts/AccountSummary.jsx
export default function AccountSummary({ accounts }) {
  const totalBalance = accounts.reduce((sum, acc) => sum + (acc.balance || 0), 0);
  const totalMonthlyInterest = accounts.reduce((sum, acc) => {
    if (acc.interest_rate > 0) {
      return sum + (acc.balance * (acc.interest_rate / 100)) / 12;
    }
    return sum;
  }, 0);
  const accountsWithInterest = accounts.filter(acc => acc.interest_rate > 0).length;

  const stats = [
    {
      label: "Total Balance",
      value: `₱${totalBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: "💰",
      color: "bg-blue-100 text-blue-700 border-blue-200",
    },
    {
      label: "Total Accounts",
      value: accounts.length,
      icon: "💳",
      color: "bg-purple-100 text-purple-700 border-purple-200",
    },
    {
      label: "Monthly Interest",
      value: `₱${totalMonthlyInterest.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: "📈",
      color: "bg-green-100 text-green-700 border-green-200",
    },
    {
      label: "Interest Earning Accounts",
      value: accountsWithInterest,
      icon: "✨",
      color: "bg-yellow-100 text-yellow-700 border-yellow-200",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className={`${stat.color} rounded-xl p-6 border shadow-sm`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-3xl">{stat.icon}</span>
          </div>
          <p className="text-sm font-medium opacity-80 mb-1">{stat.label}</p>
          <p className="text-2xl font-bold">{stat.value}</p>
        </div>
      ))}
    </div>
  );
}