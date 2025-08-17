'use client'

import { useEffect, useState } from "react";
import { UserButton } from "@clerk/nextjs";

export default function UserButtonComponent() {
	const [loaded, setLoaded] = useState(false)

	useEffect(() => {
		setLoaded(true)
	}, [])

	if (!loaded) {
		return  <div className="w-[28px] h-[28px] rounded-full bg-gray-200 animate-pulse" />;
	}

	return <UserButton showName />
}