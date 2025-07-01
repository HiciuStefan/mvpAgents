import { email_router } from '~/server/api/routers/email';
import { twitter_router } from '~/server/api/routers/twitter';
import { website_router } from '~/server/api/routers/website';
import { processed_items_router }from '~/server/api/routers/latest_items';
import { createCallerFactory, createTRPCRouter } from '~/server/api/trpc';

/**
 * This is the primary router for your server.
 *
 * All routers added in /api/routers should be manually added here.
 */
export const appRouter = createTRPCRouter({
	email: email_router,
	twitter: twitter_router,
	website: website_router,
	processed_items: processed_items_router
});

// export type definition of API
export type AppRouter = typeof appRouter;

/**
 * Create a server-side caller for the tRPC API.
 * @example
 * const trpc = createCaller(createContext);
 * const res = await trpc.post.all();
 *       ^? Post[]
 */
export const createCaller = createCallerFactory(appRouter);
