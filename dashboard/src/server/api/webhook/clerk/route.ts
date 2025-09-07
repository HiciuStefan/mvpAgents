import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { verifyWebhook } from '@clerk/nextjs/webhooks';
import {
  upsertClerkUser,
  deleteClerkUser,
  upsertClerkOrganization,
  deleteClerkOrganization,
  upsertClerkOrganizationMembership,
  deleteClerkOrganizationMembership,
} from '~/server/db/queries/clerk-webhooks';
import { try_catch } from '~/lib/try_catch';

export async function POST(req: NextRequest): Promise<NextResponse> {
  const { error } = await try_catch(async () => {
    const { type, data } = await verifyWebhook(req);

    switch (type) {
      case 'user.created':
      case 'user.updated':
        await upsertClerkUser(data);
        break;

      case 'user.deleted':
        await deleteClerkUser(data);
        break;

      case 'organization.created':
      case 'organization.updated':
        await upsertClerkOrganization(data);
        break;

      case 'organization.deleted':
        await deleteClerkOrganization(data);
        break;

      case 'organizationMembership.created':
      case 'organizationMembership.updated':
        await upsertClerkOrganizationMembership(data);
        break;

      case 'organizationMembership.deleted':
        await deleteClerkOrganizationMembership(data);
        break;

      default:
        // TODO: subscription events
        console.log(`Unhandled webhook type: ${type}`);
        return;
    }

    console.log(`Successfully processed webhook: ${type}`);
    return;
  });
  if (error) {
    console.error('Webhook verification failed:', error);
    return new NextResponse(`Error verifying webhook: ${error.message}`, {
      status: 400,
    });
  }

  return new NextResponse('Webhook processed successfully', { status: 200 });
}
