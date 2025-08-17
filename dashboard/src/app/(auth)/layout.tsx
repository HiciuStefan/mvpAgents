import { Logo } from '~/components/digital_excellence_logo'

export default function AuthLayout({ children }: { children: React.ReactNode }) {
	return (
		<div className="flex w-full justify-center items-center h-screen">
			<div className="flex flex-col items-center justify-center gap-10">
				<Logo />
				{children}
			</div>
		</div>
	)
}