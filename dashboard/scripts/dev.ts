#!/usr/bin/env tsx

import { safeRun as run, safeSpawn } from './utils/safe-run';

/**
 * Wait for database to be ready by attempting connections
 */
async function waitForDatabase(maxRetries = 30): Promise<void> {
  console.log('⏳ Waiting for database to be ready...');

  for (let i = 0; i < maxRetries; i++) {
    try {
      // First try using docker exec pg_isready
      const dockerCode = await run(
        'docker',
        ['exec', 'postgres-dev', 'pg_isready', '-U', 'postgres', '-d', 'dev_db'],
        true
      );

      if (dockerCode === 0) {
        // Double-check with actual connection test
        const connectionCode = await run('tsx', ['scripts/test-db-connection.ts'], true);
        if (connectionCode === 0) {
          console.log('✅ Database is healthy and ready');
          return;
        }
      }
    } catch (error) {
      // Try fallback connection test directly
      try {
        const connectionCode = await run('tsx', ['scripts/test-db-connection.ts'], true);
        if (connectionCode === 0) {
          console.log('✅ Database is ready (via connection test)');
          return;
        }

        console.log('❌ Database connection test failed:', connectionCode);
      } catch (fallbackError) {
        console.error('❌ Database connection test failed:', fallbackError);
      }
    }

    process.stdout.write('.');
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  throw new Error('❌ Database failed to become ready within timeout');
}

async function main(): Promise<void> {
  const noSeed = process.argv.includes('--no-dev-seed');

  console.log('🚀 Starting Graphium development environment...\n');
  if (noSeed) {
    console.log('🚫 Skipping dev data seeding (--no-dev-seed flag detected)\n');
  }

  // Determine whether to use `docker compose` or legacy `docker-compose`
  let dockerCmd: string = 'docker';
  let composeUpArgs: string[] = ['compose', 'up', '-d'];
  let composeDownArgs: string[] = ['compose', 'down', '-v']; // -v removes volumes for clean state

  console.log('🐳 Starting Docker containers...');
  let upCode = await run(dockerCmd, composeUpArgs);

  // Fallback to legacy docker-compose if the first attempt failed
  if (upCode !== 0) {
    console.log('`docker compose` failed, attempting to use `docker-compose` binary...');
    dockerCmd = 'docker-compose';
    composeUpArgs = ['up', '-d'];
    composeDownArgs = ['down', '-v'];
    upCode = await run(dockerCmd, composeUpArgs);
  }

  if (upCode !== 0) {
    console.error('❌ Failed to start Docker containers');
    process.exit(upCode);
  }

  try {
    // Wait for database to be ready
    await waitForDatabase();

    // Run database migrations
    console.log('\n📊 Running database migrations...');
    const migrateCode = await run('pnpm', ['run', 'db:migrate']);
    if (migrateCode !== 0) {
      console.error('❌ Database migration failed');
      process.exit(migrateCode);
    }
    console.log('✅ Database migrations completed');

    // Seed the database (conditionally)
    if (!noSeed) {
      console.log('🌱 Seeding database with development data...');
      const seedCode = await run('pnpm', ['run', 'db:seed:dev']);
      if (seedCode !== 0) {
        console.error('❌ Database seeding failed');
        process.exit(seedCode);
      }
      console.log('✅ Database seeding completed');
    } else {
      const seedCode = await run('pnpm', ['run', 'db:seed:prod']);
    }

    console.log('\n🎉 Development environment is ready!');
    console.log('🌐 Starting Next.js development server...\n');

    // Run Next.js dev server (turbopack enabled) as child process
    const nextProc = safeSpawn('pnpm', ['run', 'next:dev']);

    // Ensure Docker containers are stopped when Next.js dev server exits
    const cleanup = async (): Promise<void> => {
      console.log('\n🧹 Cleaning up development environment...');
      console.log('🐳 Stopping Docker containers and removing volumes...');
      await run(dockerCmd, composeDownArgs);
      console.log('✅ Cleanup completed');
      process.exit();
    };

    nextProc.on('exit', cleanup);

    process.on('SIGINT', () => {
      nextProc.kill('SIGKILL');
    });

    process.on('SIGTERM', () => {
      nextProc.kill('SIGKILL');
    });
  } catch (error) {
    console.error('❌ Failed to initialize development environment:', error);
    console.log('🧹 Cleaning up Docker containers...');
    await run(dockerCmd, composeDownArgs);
    process.exit(1);
  }
}

main().catch(err => {
  console.error('❌ Development script failed:', err);
  process.exit(1);
});
