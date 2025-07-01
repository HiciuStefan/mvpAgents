import Link from "next/link";
import { Logo } from "../digital_excellence_logo";
import { Avatar, AvatarFallback, AvatarImage } from "~/components/ui/avatar";
import { User } from "lucide-react";

export default function Header()
{
	return (
		<div className="flex justify-between items-center py-4 w-full">
			{/* <div className="flex items-center pr-4 gap-2">
				<span className="font-medium text-sm text-gray-700">Alex Doe</span>
				<Avatar>
					<AvatarImage src="" alt="User" />
					<AvatarFallback>
						<User className="w-5 h-5" />
					</AvatarFallback>
				</Avatar>
			</div> */}
		</div>
	)
}