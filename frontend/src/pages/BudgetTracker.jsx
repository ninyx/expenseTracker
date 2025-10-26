// frontend/src/pages/Budget.jsx
import { useEffect, useState } from "react";
import { getCategoryTree } from "../services/categories";
import toast from "react-hot-toast";
import BudgetOverview from "../components/budget/BudgetOverview";
import BudgetAllocation from "../components/budget/BudgetAllocation";
import BudgetProgress from "../components/budget/BudgetProgress";
import BudgetCharts from "../components/budget/BudgetCharts";

export default function Budget() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFrequency, setSelectedFrequency] = useState("monthly");

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const data = await getCategoryTree();
      setCategories(data);
    } catch (err) {
      console.error("Error fetching categories:", err);
      toast.error("Failed to load budget data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  // Filter categories by frequency
  const filterByFrequency = (cats, freq) => {
    return cats
      .map((cat) => ({
        ...cat,
        children: cat.children ? filterByFrequency(cat.children, freq) : [],
      }))
      .filter((cat) => {
        const hasMatchingFrequency = cat.frequency === freq;
        const hasMatchingChildren = cat.children && cat.children.length > 0;
        return hasMatchingFrequency || hasMatchingChildren;
      });
  };

  const filteredCategories = filterByFrequency(categories, selectedFrequency);

  // Calculate totals
  const calculateTotals = (cats) => {
    let totalBudget = 0;
    let totalUsed = 0;

    const traverse = (cat) => {
      // If cat has a non-zero budget, add its own budget and skip children for totalBudget
      if (cat.budget && cat.budget !== 0) {
        totalBudget += cat.budget;
      } 
      // If cat.budget == 0, sum only its children’s budgets
      else if (cat.children) {
        cat.children.forEach(traverse);
      }

      // totalUsed should always include this category’s value
      totalUsed += cat.budget_used || 0;
    };

    cats.forEach(traverse);
    return { totalBudget, totalUsed };
  };

  const { totalBudget, totalUsed } = calculateTotals(filteredCategories);

  if (loading) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-500">Loading budget data...</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">💰 Budget Tracker</h1>
        
        {/* Frequency Filter */}
        <div className="flex gap-2">
          {["weekly", "monthly", "yearly"].map((freq) => (
            <button
              key={freq}
              onClick={() => setSelectedFrequency(freq)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                selectedFrequency === freq
                  ? "bg-blue-600 text-white shadow-lg"
                  : "bg-white text-gray-700 hover:bg-gray-100 border"
              }`}
            >
              {freq.charAt(0).toUpperCase() + freq.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Cards */}
      <BudgetOverview
        totalBudget={totalBudget}
        totalUsed={totalUsed}
        frequency={selectedFrequency}
      />

      {/* Charts Section */}
      <BudgetCharts categories={filteredCategories} />

      {/* Budget Allocation Table */}
      <BudgetAllocation
        categories={filteredCategories}
        onUpdate={fetchCategories}
      />

      {/* Detailed Progress Bars */}
      <BudgetProgress categories={filteredCategories} />
    </div>
  );
}