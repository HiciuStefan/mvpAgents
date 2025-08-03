import styles from "~/app/business-intelligence/styles.module.css";
import type { PriorityType } from "~/hooks/use-filters";

export type Priorities = {
	high: number,
	medium: number,
	low: number,
	new: number
}

type PriorityFilterProps = {
	priorities: Priorities;
	filter: PriorityType | null;
	setFilter: (filter: PriorityType | null) => void;
};

// Priority Filter Component
export function PriorityFilter({ priorities, filter, setFilter }: PriorityFilterProps) {
	const filterItems = [
	  {
		id: 3,
		label: "High",
		count: priorities.high,
		bgColor: "bg-red-100",
		textColor: "text-red-700",
		hoverColor: "hover:bg-[#ffd5d5]",
		activeBgColor: "bg-red-600",
		activeTextColor: "text-white"
	  },
	  {
		id: 2,
		label: "Medium",
		count: priorities.medium,
		bgColor: "bg-yellow-100",
		textColor: "text-yellow-700",
		hoverColor: "hover:bg-[#fff4a3]",
		activeBgColor: "bg-yellow-500",
		activeTextColor: "text-white"
	  },
	  {
		id: 1,
		label: "Low",
		count: priorities.low,
		bgColor: "bg-green-100",
		textColor: "text-green-700",
		hoverColor: "hover:bg-[#cafadb]",
		activeBgColor: "bg-green-600",
		activeTextColor: "text-white"
	  }
	];

	const newItemClasses = `${styles.rounded_rectangle ?? 'px-4 py-2 rounded-lg cursor-pointer transition-colors'} bg-gray-100 text-gray-600 hover:bg-[#ecedf0]`;

	return (
	  <div className={`flex gap-2`}>
		{filterItems.map(item => {
		  const isActive = filter === item.id;
		  return (
			<div
			  key={item.id}
			  className={`${styles.rounded_rectangle ?? 'px-4 py-2 rounded-lg cursor-pointer transition-colors'} ${
				isActive
				  ? `${item.activeBgColor} ${item.activeTextColor}`
				  : `${item.bgColor} ${item.textColor} ${item.hoverColor}`
			  }`}
			  onClick={() => setFilter(isActive ? null : item.id as PriorityType)}
			>
			  {item.label} {item.count}
			</div>
		  );
		})}

		<div className={newItemClasses} onClick={() => setFilter(null)}>
		  New&nbsp;<strong className="text-zinc-950 font-medium">
			{priorities.new}
		  </strong>
		</div>
	  </div>
	);
  };