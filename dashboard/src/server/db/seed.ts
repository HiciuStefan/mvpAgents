/* eslint-disable */
// @ts-nocheck
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { opportunity_statuses, currencies } from './schema/sales-pipelines';
import { taxRates, unitsOfMeasure } from './schema/service-catalog';
// import dotenv from 'dotenv';

// dotenv.config();

// Direct database connection for seeding
const connection = postgres(process.env.POSTGRES_URL!);
const db = drizzle(connection);

async function seed(): Promise<void> {
  console.log('🌱 Seeding essential lookup data...');

  // Seed default opportunity statuses
  console.log('📊 Seeding opportunity statuses...');
  await db
    .insert(opportunity_statuses)
    .values([
      {
        name: 'open',
        translationKey: 'Opportunities.status.open',
        isDefault: true,
      },
      {
        name: 'won',
        translationKey: 'Opportunities.status.won',
        isDefault: true,
      },
      {
        name: 'lost',
        translationKey: 'Opportunities.status.lost',
        isDefault: true,
      },
      {
        name: 'abandoned',
        translationKey: 'Opportunities.status.abandoned',
        isDefault: true,
      },
    ])
    .onConflictDoNothing();

  // Seed default currencies
  console.log('💰 Seeding currencies...');
  await db
    .insert(currencies)
    .values([{ code: 'RON' }, { code: 'EUR' }, { code: 'USD' }])
    .onConflictDoNothing();

  // Seed default tax rates for Romania
  console.log('💸 Seeding tax rates...');
  await db
    .insert(taxRates)
    .values([
      {
        code: '0%',
        rate: '0.00',
        organizationId: null,
      },
      {
        code: '11%',
        rate: '0.11',
        organizationId: null,
      },
      {
        code: '21%',
        rate: '0.21',
        organizationId: null,
      },
    ])
    .onConflictDoNothing();

  // Seed default units of measure for architecture/construction
  console.log('📏 Seeding units of measure...');
  await db
    .insert(unitsOfMeasure)
    .values([
      // Area measurements
      {
        code: 'mp',
        nameTranslationKey: 'units.area.squareMeter',
        organizationId: null, // Global unit
      },
      {
        code: 'ml',
        nameTranslationKey: 'units.length.linearMeter',
        organizationId: null,
      },
      {
        code: 'm',
        nameTranslationKey: 'units.length.meter',
        organizationId: null,
      },
      {
        code: 'km',
        nameTranslationKey: 'units.length.kilometer',
        organizationId: null,
      },
      // Volume measurements
      {
        code: 'mc',
        nameTranslationKey: 'units.volume.cubicMeter',
        organizationId: null,
      },
      {
        code: 'l',
        nameTranslationKey: 'units.volume.liter',
        organizationId: null,
      },
      // Weight measurements
      {
        code: 'kg',
        nameTranslationKey: 'units.weight.kilogram',
        organizationId: null,
      },
      {
        code: 't',
        nameTranslationKey: 'units.weight.ton',
        organizationId: null,
      },
      // Time measurements
      {
        code: 'ora',
        nameTranslationKey: 'units.time.hour',
        organizationId: null,
      },
      {
        code: 'zi',
        nameTranslationKey: 'units.time.workDay',
        organizationId: null,
      },
      // Quantity measurements
      {
        code: 'buc',
        nameTranslationKey: 'units.quantity.piece',
        organizationId: null,
      },
    ])
    .onConflictDoNothing();

  console.log('✅ Essential data seeded successfully!');
}

seed()
  .catch(error => {
    console.error('❌ Error seeding essential data:', error);
    process.exit(1);
  })
  .finally(async () => {
    await connection.end();
    process.exit(0);
  });
