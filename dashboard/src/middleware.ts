import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';
// import { ROUTES } from './lib/nav_items';

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhook/clerk(.*)',
]);

// Define onboarding routes that should be accessible during onboarding
// const isOnboardingRoute = createRouteMatcher(['/onboarding(.*)']);

export default clerkMiddleware(async (auth, req) => {
  const {
    pathname,
    // origin
  } = req.nextUrl;

  if (!isPublicRoute(req)) {
    await auth.protect();
  }

  if (
    pathname.startsWith('/api') ||
    pathname.startsWith('/trpc') ||
    pathname.startsWith('/api/trpc')
  ) {
    return NextResponse.next();
  }

  // const { orgId } = await auth();
  // // redirect to onboardingselection page when user has no active organization and is not on onboarding route
  // if (!orgId && !isPublicRoute(req) && !isOnboardingRoute(req)) {
  //   const selectionUrl = new URL(ROUTES.ONBOARDING.SELECTION, origin);
  //   selectionUrl.searchParams.set('redirectTo', pathname);
  //   return NextResponse.redirect(selectionUrl);
  // }
});

// export default clerkMiddleware(async (auth, req) => {
//   // if (!isPublicRoute(req)) {
//   //   await auth.protect()
//   // }
// });

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};
