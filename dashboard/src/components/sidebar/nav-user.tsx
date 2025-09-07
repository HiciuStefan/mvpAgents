'use client';

import { useClerk, useUser } from '@clerk/nextjs';
import { BadgeCheck, Bell, ChevronsUpDown, LogOut } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '~/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '~/components/ui/dropdown-menu';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '~/components/ui/sidebar';
import { useIsClient } from '~/hooks/use-is-client';

// Placeholder component that matches the visual structure
function NavUserPlaceholder() {
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton size="lg" className="cursor-default">
          <Avatar className="h-8 w-8 rounded-lg">
            <AvatarFallback className="rounded-lg bg-muted animate-pulse" />
          </Avatar>
          <div className="grid flex-1 text-left text-sm leading-tight">
            <div className="h-4 w-24 bg-muted animate-pulse rounded" />
            <div className="h-3 w-32 bg-muted animate-pulse rounded mt-1" />
          </div>
          <ChevronsUpDown className="ml-auto size-4 opacity-50" />
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}

export function NavUser() {
  const isClient = useIsClient();
  const { user } = useUser();

  // Show placeholder during SSR and initial hydration
  if (!isClient) {
    return <NavUserPlaceholder />;
  }

  // Show nothing if no user is loaded yet
  if (!user) return null;

  return <NavUserClient user={user} />;
}

function NavUserClient({
  user,
}: {
  user: NonNullable<ReturnType<typeof useUser>['user']>;
}) {
  const { openUserProfile, signOut } = useClerk();
  const { isMobile } = useSidebar();

  const userDisplayName =
    user.fullName ??
    user.username ??
    user.emailAddresses[0]?.emailAddress ??
    'User';

  const userEmail = user.primaryEmailAddress?.emailAddress ?? '';
  const userAvatar = user.imageUrl;
  const userInitials = user.fullName
    ? user.fullName
        .split(' ')
        .slice(0, 2)
        .map(n => n[0])
        .join('')
        .toUpperCase()
    : userDisplayName.slice(0, 2).toUpperCase();

  const handleSignOut = async () => {
    await signOut({ redirectUrl: `/` });
  };

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
                <AvatarFallback className="rounded-lg">
                  {userInitials}
                </AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">
                  {userDisplayName}
                </span>
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
                  <AvatarFallback className="rounded-lg">
                    {userInitials}
                  </AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">
                    {userDisplayName}
                  </span>
                  <span className="truncate text-xs">{userEmail}</span>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={() => openUserProfile()}>
                <BadgeCheck />
                Account
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Bell />
                Notifications
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleSignOut}>
              <LogOut />
              Log Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
