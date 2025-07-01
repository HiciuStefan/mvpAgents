import postgres from 'postgres';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const sql = postgres(process.env.DATABASE_URL!, { max: 1 });
    await sql`SELECT 1`; // Simple query to test connection
    await sql.end();

    return NextResponse.json({ success: true, message: 'Connection successful' });
  } catch (err) {
    const error = err instanceof Error ? err : new Error('Unknown error');
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
