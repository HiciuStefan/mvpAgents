import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import styles from './styles.module.css';

type ActionableDataType = {
  email_count: number;
  task_count: number;
  notes_count: number;
};

export function ActionableItems({ data }: { data: ActionableDataType }) {
  const { email_count, task_count, notes_count } = data;
  const total = email_count + task_count + notes_count;

  return (
    <Card className={styles.card} style={{ width: '360px' }}>
      <CardHeader>
        <CardTitle className={styles.card_title}>Tasks</CardTitle>
      </CardHeader>
      <CardContent className="pr-4">
        <div className="flex items-start gap-5">
          <span className="font-display text-3xl lg:text-4xl font-bold">
            {total}
          </span>
          <ProgressBars data={data} />
        </div>
      </CardContent>
    </Card>
  );
}

export function ActionableItems2({ data }: { data: ActionableDataType }) {
  const { email_count, task_count, notes_count } = data;
  const total = email_count + task_count + notes_count;

  return (
    <Card className={styles.card}>
      <CardHeader>
        <CardTitle className={styles.card_title}>Tasks</CardTitle>
      </CardHeader>
      <CardContent className="pr-4">
        <div className="flex items-start gap-5">
          <span className="font-display text-3xl lg:text-4xl font-bold">
            {total}
          </span>
          <ProgressBars data={data} />
        </div>
      </CardContent>
    </Card>
  );
}

function ProgressBars({ data }: { data: ActionableDataType }) {
  const { /* email_count, */ task_count, notes_count } = data;

  return (
    <div className="flex flex-col mt-[-10px] w-full">
      {/* <div>
				<Link href="#" className={styles.item_link}>
					<div className="flex justify-between">
						<div className="flex gap-2">
							<span className="text-zinc-500">Emails</span>
							<span className="font-medium">({email_count})</span>
						</div>
						<div className="text-zinc-700">
							<ArrowRight width={20} />
						</div>
					</div>
				</Link>
			</div> */}
      <div>
        <Link href="#" className={styles.item_link}>
          <div className="flex justify-between">
            <div className="flex gap-2">
              <span className="text-zinc-500">Tasks</span>
              <span className="font-medium">({task_count})</span>
            </div>
            <div className="text-zinc-700">
              <ArrowRight width={20} />
            </div>
          </div>
        </Link>
      </div>
      <div>
        <Link href="#" className={styles.item_link}>
          <div className="flex justify-between">
            <div className="flex gap-2">
              <span className="text-zinc-500">Notes</span>
              <span className="font-medium">({notes_count})</span>
            </div>
            <div className="text-zinc-700">
              <ArrowRight width={20} />
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
}
