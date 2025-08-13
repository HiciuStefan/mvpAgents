'use client';

import { BadgeCheck, Bell, ChevronsUpDown, LogOut } from 'lucide-react';
// import { BadgeCheck, Bell, ChevronsUpDown, LogOut, Building, Plus, Settings } from 'lucide-react';
// import { useUser, useOrganizationList, useClerk, useOrganization } from '@clerk/nextjs';

import { Avatar, AvatarFallback, AvatarImage } from '~/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
} from '~/components/ui/dropdown-menu';
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem, useSidebar } from '~/components/ui/sidebar';

export function NavUser() {
  // const { user } = useUser();
  // const { userMemberships, setActive } = useOrganizationList({
  //   userMemberships: {
  //     infinite: true,
  //   },
  // });
  // const { organization: currentOrg } = useOrganization();
  // const { openUserProfile, openCreateOrganization, openOrganizationProfile, signOut } = useClerk();
  const { isMobile } = useSidebar();

  // if (!user) return null;

	const user = {
		fullName: 'Johnny Excellence',
		username: 'johnnyexcellence',
		emailAddresses: [{ emailAddress: 'johnny@digitalexcellence.com' }],
		imageUrl: 'https://example.com/avatar.png',
		primaryEmailAddress: { emailAddress: 'johnny@digitalexcellence.com' },
	}

  const userDisplayName =
  user.fullName ??
  user.username ??
  user.emailAddresses[0]?.emailAddress ??
  'User';

  const userEmail = user.primaryEmailAddress?.emailAddress || '';
  const userAvatar = user.imageUrl;
  const userInitials = user.fullName
    ? user.fullName
        .split(' ')
				.slice(0, 2)
        .map(n => n[0])
        .join('')
        .toUpperCase()
    : userDisplayName.slice(0, 2).toUpperCase();


  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <Avatar className="h-8 w-8 rounded-lg">
                <AvatarImage src={userAvatar} alt={userDisplayName} />
                <AvatarFallback className="rounded-lg">{userInitials}</AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">{userDisplayName}</span>
                <span className="truncate text-xs">{userEmail}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
            side={isMobile ? 'bottom' : 'right'}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                <Avatar className="h-8 w-8 rounded-lg">
                  <AvatarImage src={userAvatar} alt={userDisplayName} />
                  <AvatarFallback className="rounded-lg">{userInitials}</AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">{userDisplayName}</span>
                  <span className="truncate text-xs">{userEmail}</span>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={() => {console.log('account')}}>
                <BadgeCheck />
                Account
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Bell />
                Notifications
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => {console.log('log out')}}>
              <LogOut />
              Log Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
