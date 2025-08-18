'use client';

import { SignedOut, SignInButton, SignUpButton } from "@clerk/nextjs";
import { Button } from "~/components/ui/button";

export default function Header() {
	return (
		<div className="relative flex flex-end justify-end align-right w-full">
			<div className="absolute top-[-50px] right-[0] flex items-center gap-2">
				<SignedOut>
					<SignUpButton>
						<Button variant="outline" className="cursor-pointer">
							Sign Up
						</Button>
					</SignUpButton>
					<SignInButton>
						<Button className="bg-[#154dbc] hover:bg-[#1b58d3] cursor-pointer">
							Sign In
						</Button>
					</SignInButton>
				</SignedOut>
			</div>
		</div>
	)
}