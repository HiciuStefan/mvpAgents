'use client';

import { useState } from 'react';

import { api } from '~/trpc/react';

export function LatestPost()
{
	const [latestPost] = api.twitter.getLatest.useSuspenseQuery({
		limit: 1
	});

	const utils = api.useUtils();
	const [name, setName] = useState('');
	const createPost = api.twitter.create.useMutation({
		onSuccess: async () => {
			await utils.twitter.invalidate();
			setName('');
		}
	});


	if (latestPost === null) {
		return null;
	}

	const formattedText = '';

	// let formattedText = '';
	// if (latestPost.data?.text) {
	// 	formattedText = latestPost.data.text.replace(/\\n/g, '\n');
	// }



	return (
		<div className="w-full max-w-xs">
			{formattedText ? (
				<p className="whitespace-pre-line">
					{/* <p className="truncate"> */}
					Your most recent post: {formattedText}</p>
			) : (
				<p>You have no posts yet.</p>
			)}
			<form className="flex flex-col gap-2" onSubmit={(e) => {
				e.preventDefault();
				// createPost.mutate({ text: name });
			}}>
				<input
					type="text"
					placeholder="Title"
					value={name}
					onChange={(e) => setName(e.target.value)}
					className="w-full rounded-full px-4 py-2"
				/>
				<button type="submit" disabled={createPost.isPending} className="rounded-full bg-white/10 px-10 py-3 font-semibold transition hover:bg-white/20" >
					{createPost.isPending ? "Submitting..." : "Submit"}
				</button>
			</form>
		</div>
	);
}
