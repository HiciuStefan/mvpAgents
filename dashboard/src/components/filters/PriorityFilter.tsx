import styles from "~/app/business-intelligence/styles.module.css";

type Priorities = {
	high: number,
	medium: number,
	low: number,
	new: number
}

export function PriorityFilter({ priorities }: { priorities: Priorities }) {
	return (
		<>
			<div className={`${styles.rounded_rectangle} bg-red-100 text-red-700 hover:bg-[#ffd5d5]`}>
				High {priorities.high}
			</div>
			<div className={`${styles.rounded_rectangle} bg-yellow-100 text-yellow-700 hover:bg-[#fff4a3]`}>
				Medium {priorities.medium}
			</div>
			<div className={`${styles.rounded_rectangle} bg-green-100 text-green-700 hover:bg-[#cafadb]`}>
				Low {priorities.low}
			</div>
			<div className={`${styles.rounded_rectangle} bg-gray-100 text-gray-600 hover:bg-[#ecedf0]`}>
				New&nbsp;<strong className="text-zinc-950 font-medium"> {priorities.new}</strong>
			</div>
		</>
	);
}