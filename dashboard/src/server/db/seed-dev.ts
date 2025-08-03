// @ts-nocheck
import 'dotenv/config';

import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { users, users_organizations, organizations } from './schema/users';
import { clients, clientToContactPersons, contactPersons } from './schema/clients';
import { sales_pipelines, pipeline_stages, opportunities, opportunity_statuses } from './schema/sales-pipelines';
import { serviceCategories, standardServiceItems } from './schema/service-catalog';
import { createCategoryOptimized } from '../lib/catalog/category-operations';
import { inArray, eq, and, type InferInsertModel } from 'drizzle-orm';
import { faker } from '@faker-js/faker';
import { createInsertSchema } from 'drizzle-zod';
import type { User, Organization } from './types/users';
import type { Client, ContactPerson } from './types/clients';
import type { SalesPipeline, PipelineStage } from './types/sales';

// ===== CONFIGURATION =====
const SEED_CONFIG = {
  CONTACTS_PER_ORG: 15,
  PERSONS_PER_ORG: 25,
  PIPELINES_PER_ORG: 5,
  OPPORTUNITIES_PER_ORG: 100,
  MAIN_CATEGORIES: 4,
  SUBCATEGORIES_PER_MAIN: 3,
  SUB_SUBCATEGORIES_CHANCE: 0.5, // 50% chance a subcategory has another level
  ITEMS_PER_CATEGORY_MIN: 3,
  ITEMS_PER_CATEGORY_MAX: 8,
  UNCATEGORIZED_ITEMS: 10,
} as const;

// ===== HELPER FUNCTIONS =====
function randomFromArray<T>(array: T[]): T {
  return faker.helpers.arrayElement(array);
}

function randomInt(min: number, max: number): number {
  return faker.number.int({ min, max });
}

// ===== DATA GENERATORS =====
function generateContact(organizationId: string, createdByUserId: string): InferInsertModel<typeof clients> {
  const clientType = randomFromArray(['company', 'individual']) as 'company' | 'individual';
  const name = clientType === 'company' ? faker.company.name() : faker.person.fullName();

  return {
    organizationId: organizationId,
    name,
    clientType: clientType,
    vatCode: faker.finance.accountNumber(9),
    registrationNumber: faker.finance.accountNumber(4),
    billingAddress: faker.location.streetAddress({ useFullAddress: true }),
    createdByUserId: createdByUserId,
    updatedByUserId: createdByUserId,
  };
}

function generatePerson(organizationId: string, createdByUserId: string): InferInsertModel<typeof contactPersons> {
  const firstName = faker.person.firstName();
  const lastName = faker.person.lastName();
  return {
    organizationId: organizationId,
    firstName: firstName,
    lastName: lastName,
    emailPrimary: faker.internet.email({ firstName, lastName }),
    phonePrimary: faker.phone.number(),
    jobTitle: faker.person.jobTitle(),
    createdByUserId: createdByUserId,
    updatedByUserId: createdByUserId,
  };
}

function generatePersonForIndividualClient(
  organizationId: string,
  createdByUserId: string,
  clientName: string
): InferInsertModel<typeof contactPersons> {
  // Split the client name into first and last name
  const nameParts = clientName.trim().split(' ');
  const firstName = nameParts[0] || 'Unknown';
  const lastName = nameParts.slice(1).join(' ') || 'Client';

  return {
    organizationId: organizationId,
    firstName: firstName,
    lastName: lastName,
    emailPrimary: faker.internet.email({ firstName, lastName }),
    phonePrimary: faker.phone.number(),
    jobTitle: 'Owner', // Default job title for individual clients
    createdByUserId: createdByUserId,
    updatedByUserId: createdByUserId,
  };
}

function generateSalesPipeline(
  organizationId: string,
  createdByUserId: string
): InferInsertModel<typeof sales_pipelines> {
  const pipelineTypes = [
    'Sales Pipeline',
    'Lead Generation',
    'Customer Acquisition',
    'Enterprise Sales',
    'Quick Wins',
    'Strategic Accounts',
    'Partner Channel',
    'Inbound Process',
  ];
  const name = `${randomFromArray(pipelineTypes)} ${faker.number.int({ min: 100, max: 999 })}`;

  return {
    organizationId: organizationId,
    name,
    isDefault: faker.helpers.maybe(() => true, { probability: 0.3 }) ?? false, // 30% chance of being default
    createdByUserId: createdByUserId,
    updatedByUserId: createdByUserId,
  };
}

function generatePipelineStage(
  organizationId: string,
  pipelineId: string,
  stageName: string,
  order: number,
  totalStages: number,
  createdByUserId: string
): InferInsertModel<typeof pipeline_stages> {
  return {
    organizationId: organizationId,
    salesPipelineId: pipelineId,
    name: stageName,
    stageOrder: order,
    probabilityPercent: Math.floor((order / totalStages) * 100),
    status: order === totalStages ? 'won' : undefined,
    createdByUserId: createdByUserId,
    updatedByUserId: createdByUserId,
  };
}

function generateOpportunity(
  organizationId: string,
  clientId: string,
  contactPersonId: string,
  pipelineId: string,
  stageId: string,
  ownerUserId: string
): InferInsertModel<typeof opportunities> {
  const projectTypes = [
    'Web Development',
    'Mobile App',
    'E-commerce',
    'CRM Implementation',
    'Digital Marketing',
    'Data Analytics',
    'Cloud Migration',
    'API Integration',
    'Consulting Services',
    'Software License',
    'Training Program',
    'Support Contract',
  ];

  // Only use currencies that are seeded in seed.ts
  const currencyCodes = ['RON', 'EUR', 'USD'];

  const name = `${randomFromArray(projectTypes)} - ${faker.company.buzzPhrase()}`;

  return {
    organizationId: organizationId,
    name,
    clientId: clientId,
    contactPersonId: contactPersonId,
    salesPipelineId: pipelineId,
    currentPipelineStageId: stageId,
    estimatedValue: faker.number.int({ min: 5000, max: 500000 }),
    currencyCode: randomFromArray(currencyCodes), // Only use currencies from seed.ts
    expectedCloseDate: faker.date.future({ years: 1 }).toISOString().split('T')[0],
    closeProbability: faker.number.int({ min: 10, max: 95 }),
    ownerUserId: ownerUserId,
    sourceDescription: faker.helpers.arrayElement([
      'Website inquiry',
      'Referral',
      'Cold outreach',
      'Trade show',
      'LinkedIn',
      'Partner referral',
      'Content marketing',
      'Webinar',
    ]),
    notes: faker.lorem.paragraph(),
    status: 'open',
    createdByUserId: ownerUserId,
    updatedByUserId: ownerUserId,
  };
}

// Type definitions for service category structure
interface ServiceCategoryStructure {
  subcategories: string[];
  subSubcategories: Record<string, string[]>;
}

type CategoryRecord = {
  id: string;
  name: string;
  organizationId?: string;
  description: string | null;
  parentCategoryId: string | null;
  materializedPath?: string[] | null;
  createdAt: Date;
  updatedAt: Date;
  createdByUserId?: string | null;
  updatedByUserId?: string | null;
  deletedAt?: Date | null;
};

// Predefined category structures for architecture/construction services
const SERVICE_CATEGORY_STRUCTURE: Record<string, ServiceCategoryStructure> = {
  'Urbanism și Planificare': {
    subcategories: ['Planuri Urbanistice', 'Certificate de Urbanism', 'Studii de Fezabilitate', 'Consultanță Urbanism'],
    subSubcategories: {
      'Planuri Urbanistice': [
        'PUG - Plan Urbanistic General',
        'PUZ - Plan Urbanistic Zonal',
        'PUD - Plan Urbanistic de Detaliu',
      ],
      'Certificate de Urbanism': ['CU Informare', 'CU Amplasament', 'CU Demolare'],
      'Studii de Fezabilitate': ['Studii Urbane', 'Analize Teritoriale', 'Studii de Impact'],
    },
  },
  'Arhitectură Rezidențială': {
    subcategories: ['Proiecte Locuințe', 'Documentații Tehnice', 'Avize și Autorizații', 'Supraveghere Execuție'],
    subSubcategories: {
      'Proiecte Locuințe': ['Case Individuale', 'Blocuri Rezidențiale', 'Ansambluri Rezidențiale'],
      'Documentații Tehnice': [
        'DTAC - Documentație Tehnică',
        'PT+DE - Proiect Tehnic + Detalii Execuție',
        'AS-BUILT - Planuri de Recepție',
      ],
      'Avize și Autorizații': ['Autorizație de Construire', 'Avize Specialitate', 'Receptii Finale'],
    },
  },
  'Design Interior': {
    subcategories: ['Concept Design', 'Proiectare Detaliată', 'Planuri Execuție', 'Coordonare Lucrări'],
    subSubcategories: {
      'Concept Design': ['Schițe Conceptuale', 'Planuri Funcționale', 'Randări 3D'],
      'Proiectare Detaliată': ['Planuri Mobilier', 'Planuri Instalații', 'Detalii Finisaje'],
      'Planuri Execuție': ['Planuri Tâmplărie', 'Planuri Electrică', 'Planuri Sanitare'],
    },
  },
  'Servicii Complementare': {
    subcategories: ['Consultanță Tehnică', 'Expertiză Tehnică', 'Măsurători Topografice', 'Certificări Energetice'],
    subSubcategories: {
      'Consultanță Tehnică': ['Consultanță Reglementări', 'Optimizare Proiecte', 'Analiza Costurilor'],
      'Expertiză Tehnică': ['Expertiză Tehnică Construcții', 'Evaluări Structurale', 'Diagnosticări Clădiri'],
      'Măsurători Topografice': ['Ridicări Topografice', 'Implantări', 'Verificări Dimensionale'],
    },
  },
} as const;

function generateServiceItem(
  organizationId: string,
  category: CategoryRecord,
  createdByUserId: string
): InferInsertModel<typeof standardServiceItems> {
  const serviceNames = [
    // Urbanism și Planificare
    'Întocmire PUG',
    'Întocmire PUZ',
    'Întocmire PUD',
    'Certificate de Urbanism Informare',
    'Certificate de Urbanism Amplasament',
    'Studiu de Fezabilitate Urbană',
    'Analiză Teritorială',
    'Studiu de Impact',
    'Consultanță Reglementări Urbanism',

    // Arhitectură Rezidențială
    'Proiect Arhitectură Casă Individuală',
    'Proiect Arhitectură Bloc Rezidențial',
    'Documentație Tehnică DTAC',
    'Proiect Tehnic + Detalii Execuție (PT+DE)',
    'Planuri AS-BUILT',
    'Documentație Autorizație Construire',
    'Obținere Avize Specialitate',
    'Supraveghere Execuție Lucrări',
    'Receptie Finală Construcție',
    'Întocmire Cărți Tehnice',

    // Design Interior
    'Concept Design Apartament',
    'Concept Design Casă',
    'Proiect Amenajare Interioare',
    'Planuri Mobilier',
    'Planuri Instalații Interior',
    'Detalii Finisaje',
    'Randări 3D Fotorealiste',
    'Planuri Tâmplărie',
    'Planuri Instalații Electrice',
    'Planuri Instalații Sanitare',
    'Coordonare Execuție Design',

    // Servicii Complementare
    'Expertiză Tehnică Construcții',
    'Evaluare Structurală',
    'Diagnosticare Clădire',
    'Ridicare Topografică',
    'Implantare Construcție',
    'Verificare Dimensională',
    'Certificat Energetic',
    'Consultanță Tehnică',
    'Optimizare Proiect',
    'Analiză Costuri Construcție',
  ];

  // Only use units of measure that are seeded in seed.ts
  const unitsOfMeasureCodes = [
    'mp', // Metru pătrat
    'ml', // Metru liniar
    'm', // Metru
    'km', // Kilometru
    'mc', // Metru cub
    'l', // Litru
    'kg', // Kilogram
    't', // Tonă
    'ora', // Oră
    'zi', // Zi lucrătoare
    'buc', // Bucată
  ];

  // Only use tax rates that are seeded in seed.ts
  const taxRateCodes = ['0%', '11%', '21%'];

  // Only use currencies that are seeded in seed.ts
  const currencyCodes = ['RON', 'EUR', 'USD'];

  const name = randomFromArray(serviceNames);
  const unitOfMeasureCode = randomFromArray(unitsOfMeasureCodes);

  // Generate realistic pricing based on unit of measure for Romanian architecture market
  let basePrice: number;
  switch (unitOfMeasureCode) {
    case 'ora':
      basePrice = faker.number.int({ min: 80, max: 300 }); // 80-300 RON/oră
      break;
    case 'zi':
      basePrice = faker.number.int({ min: 600, max: 2400 }); // 600-2400 RON/zi
      break;
    case 'mp':
      basePrice = faker.number.int({ min: 20, max: 150 }); // 20-150 RON/mp
      break;
    case 'buc':
    case 'set':
    case 'lot':
    case 'punct':
    case 'forfet':
      basePrice = faker.number.int({ min: 200, max: 5000 }); // Generic price for quantity/special units
      break;
    case 'ml':
    case 'm':
    case 'km':
    case 'mc':
    case 'l':
    case 'kg':
    case 't':
      basePrice = faker.number.int({ min: 50, max: 1000 }); // Generic price for other common units
      break;
    default:
      basePrice = faker.number.int({ min: 200, max: 5000 }); // 200-5000 RON/bucată
  }

  const costMultiplier = faker.number.float({ min: 0.6, max: 0.8 });
  const standardUnitCost = Math.round(basePrice * costMultiplier * 100) / 100;

  // Generate Romanian architecture service codes
  const codePrefix = name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 4);
  const codeSuffix = faker.string.alphanumeric({ length: 3, casing: 'upper' });

  return {
    organizationId: organizationId,
    name,
    code: `${codePrefix}-${codeSuffix}`,
    description: `Serviciu de ${name.toLowerCase()} conform normativelor românești în vigoare`,
    unitOfMeasureCode,
    standardUnitCost: standardUnitCost.toString(),
    standardUnitPrice: basePrice.toString(),
    costCurrency: randomFromArray(currencyCodes),
    taxRate: randomFromArray(taxRateCodes),
    categoryId: category.id,
    materializedPath: category.materializedPath,
    createdByUserId: createdByUserId,
    updatedByUserId: createdByUserId,
  };
}

// Zod schemas for validation
const insertContactPersonSchema = createInsertSchema(contactPersons);
const insertClientToContactPersonSchema = createInsertSchema(clientToContactPersons);
const insertSalesPipelineSchema = createInsertSchema(sales_pipelines);
const insertPipelineStageSchema = createInsertSchema(pipeline_stages);
const insertOpportunitySchema = createInsertSchema(opportunities);
const insertServiceItemSchema = createInsertSchema(standardServiceItems);

// Database connection
const connection = postgres(process.env.POSTGRES_URL!, {
  connection: {
    search_path: 'graphium',
  },
  max: 1, // Limit connection pool to 1 for scripts
  idle_timeout: 5, // Close idle connections after 5 seconds
  connect_timeout: 30, // Connection timeout
});

const db = drizzle(connection, {
  schema: {
    organizations,
    users,
    clients,
    contactPersons,
    clientToContactPersons,
    sales_pipelines,
    pipeline_stages,
    opportunities,
    serviceCategories,
    standardServiceItems,
  },
});

const main = async (): Promise<void> => {
  console.log('🌱 Starting database seeding with external system data + Faker.js...');
  console.log('💡 Note: Individual clients will have matching contact persons with the same name');
  console.log(
    `📊 Config: ${SEED_CONFIG.CONTACTS_PER_ORG} contacts, ${SEED_CONFIG.PERSONS_PER_ORG} persons, ${SEED_CONFIG.PIPELINES_PER_ORG} pipelines, ${SEED_CONFIG.OPPORTUNITIES_PER_ORG} opportunities, ${SEED_CONFIG.MAIN_CATEGORIES} main categories, ${SEED_CONFIG.SUBCATEGORIES_PER_MAIN} subcategories per main, ${SEED_CONFIG.UNCATEGORIZED_ITEMS} uncategorized items`
  );

  // Set a seed for reproducible results during development
  faker.seed(12345);

  try {
    // ===== SEED OPPORTUNITY STATUSES (required for pipeline stages) =====
    console.log('📊 Seeding opportunity statuses...');
    await db
      .insert(opportunity_statuses)
      .values([
        {
          name: 'open',
          translationKey: 'opportunities.status.open',
          isDefault: true,
        },
        {
          name: 'won',
          translationKey: 'opportunities.status.won',
          isDefault: true,
        },
        {
          name: 'lost',
          translationKey: 'opportunities.status.lost',
          isDefault: true,
        },
        {
          name: 'abandoned',
          translationKey: 'opportunities.status.abandoned',
          isDefault: true,
        },
      ])
      .onConflictDoNothing();

    // ===== SEED ORGANIZATIONS (from external system) =====
    console.log('🏢 Seeding organizations from external system...');
    const orgs: Organization[] = await db
      .insert(organizations)
      .values([
        {
          organizationId: 'org_2xcv8IlEKOekR8OKhYTdqj8Sp6K',
          name: 'Tech Solutions Inc',
        },
        {
          organizationId: 'org_2ycyNgrH31JSgRvhiZbTu4Hh3sT',
          name: 'Digital Marketing Co',
        },
      ])
      .onConflictDoNothing()
      .returning();

    // If no orgs were inserted (due to conflict), fetch existing ones
    let organizations_list = orgs;
    if (organizations_list.length === 0) {
      organizations_list = await db.select().from(organizations);
    }

    console.log(`✓ Organizations ready: ${organizations_list.map(org => org.name).join(', ')}`);

    // ===== SEED USERS ONCE (from external system) =====
    console.log('👥 Seeding users from external system...');
    const userIdsToSeed = [
      'user_2x00FmRXjPQPm1JCyDNbCGpjqLo',
      'user_2wRev75pcCX6pwry6gwxGVqxOgj',
      'user_2zoPrOUz9TlknrK6BAJtprdWlx4',
      'user_2zmdqciIEd54jKeiFbQc0OJSqWO',
    ];

    const usersToInsert = userIdsToSeed.map(userId => {
      let firstName = 'Test';
      let lastName = 'User';
      let email = `${userId.substring(5, 10)}@graphium.com`;

      if (userId === 'user_2x00FmRXjPQPm1JCyDNbCGpjqLo') {
        firstName = 'John';
        lastName = 'Manager';
        email = 'john@techsolutions.com';
      } else if (userId === 'user_2wRev75pcCX6pwry6gwxGVqxOgj') {
        firstName = 'Sarah';
        lastName = 'Sales';
        email = 'sarah@techsolutions.com';
      } else if (userId === 'user_2zoPrOUz9TlknrK6BAJtprdWlx4') {
        firstName = 'Alice';
        lastName = 'Developer';
        email = 'alice@graphium.com';
      } else if (userId === 'user_2zmdqciIEd54jKeiFbQc0OJSqWO') {
        firstName = 'Bob';
        lastName = 'Engineer';
        email = 'bob@graphium.com';
      }

      return {
        userId,
        firstName,
        lastName,
        email,
        isActive: true,
        webhook: false,
      };
    });

    await db.insert(users).values(usersToInsert).onConflictDoNothing();

    const allUsers: User[] = await db.select().from(users).where(inArray(users.userId, userIdsToSeed));

    if (allUsers.length !== userIdsToSeed.length) {
      throw new Error('Failed to create or find all specified users');
    }

    console.log(`✓ Users ready: ${allUsers.map(u => `${u.firstName} ${u.lastName}`).join(', ')}`);

    // ===== LINK USERS TO ALL ORGANIZATIONS =====
    console.log('🔗 Linking users to organizations...');
    for (const organization of organizations_list) {
      for (const user of allUsers) {
        await db
          .insert(users_organizations)
          .values({
            userId: user.userId,
            organizationId: organization.organizationId,
          })
          .onConflictDoNothing();
      }
      console.log(`✓ Linked users to ${organization.name}`);
    }

    // ===== CREATE ORG-SPECIFIC DATA FOR EACH ORGANIZATION =====
    for (const organization of organizations_list) {
      console.log(`\n🏗️  Creating data for organization: ${organization.name}`);

      // Arrays to store created entities for this org
      const createdPersons: ContactPerson[] = [];
      const createdContacts: Client[] = [];
      const createdPipelines: SalesPipeline[] = [];
      const createdStages: PipelineStage[] = [];
      const createdCategories: CategoryRecord[] = [];
      const createdServiceItems: InferInsertModel<typeof standardServiceItems>[] = [];

      // ===== CREATE CONTACTS AND PERSONS (with Faker.js) =====
      console.log('🏢 Creating contacts with Faker.js...');
      for (let i = 0; i < SEED_CONFIG.CONTACTS_PER_ORG; i++) {
        const randomUser = randomFromArray(allUsers);
        const clientData = generateContact(organization.organizationId, randomUser.userId);
        const [contact] = await db.insert(clients).values([clientData]).returning();
        createdContacts.push(contact);
        console.log(`  ✓ Created contact: ${contact.name} (${contact.clientType})`);

        // For individual clients, create a corresponding contact person with the same name
        if (contact.clientType === 'individual') {
          const personData = insertContactPersonSchema.parse(
            generatePersonForIndividualClient(organization.organizationId, randomUser.userId, contact.name)
          );
          const [person] = await db.insert(contactPersons).values([personData]).returning();
          createdPersons.push(person);
          console.log(`    ✓ Created matching person: ${person.firstName} ${person.lastName}`);

          // Immediately link the individual client to their corresponding person
          const linkData = insertClientToContactPersonSchema.parse({
            organizationId: organization.organizationId,
            clientId: contact.id,
            contactPersonId: person.id,
            roleAtClient: 'Owner',
            isPrimaryContactForClient: true,
            createdByUserId: randomUser.userId,
            updatedByUserId: randomUser.userId,
          });
          await db.insert(clientToContactPersons).values([linkData]);
          console.log(`    ✓ Linked individual client to their person`);
        }
      }

      // ===== CREATE ADDITIONAL PERSONS (with Faker.js) =====
      console.log('📞 Creating additional persons with Faker.js...');
      const additionalPersonsCount = SEED_CONFIG.PERSONS_PER_ORG - createdPersons.length;
      for (let i = 0; i < additionalPersonsCount; i++) {
        const randomUser = randomFromArray(allUsers);
        const personData = insertContactPersonSchema.parse(
          generatePerson(organization.organizationId, randomUser.userId)
        );
        const [person] = await db.insert(contactPersons).values([personData]).returning();
        createdPersons.push(person);
        console.log(`  ✓ Created person: ${person.firstName} ${person.lastName}`);
      }

      // ===== LINK ADDITIONAL PERSONS TO CONTACTS =====
      console.log('🔗 Linking additional persons to contacts...');

      // Get all persons that are not already linked (exclude individual client persons)
      const linkedPersonIds = new Set<string>();
      const existingLinks = await db
        .select({ contactPersonId: clientToContactPersons.contactPersonId })
        .from(clientToContactPersons)
        .where(eq(clientToContactPersons.organizationId, organization.organizationId));

      existingLinks.forEach(link => linkedPersonIds.add(link.contactPersonId));

      const unlinkedPersons = createdPersons.filter(person => !linkedPersonIds.has(person.id));

      for (const person of unlinkedPersons) {
        const numContacts = randomInt(1, Math.min(2, createdContacts.length));
        const shuffledContacts = faker.helpers.shuffle([...createdContacts]);

        for (let i = 0; i < numContacts; i++) {
          const contact = shuffledContacts[i];
          const randomUser = randomFromArray(allUsers);

          // Check if this person is already linked to this contact
          const existingLink = await db
            .select()
            .from(clientToContactPersons)
            .where(
              and(
                eq(clientToContactPersons.clientId, contact.id),
                eq(clientToContactPersons.contactPersonId, person.id)
              )
            );

          if (existingLink.length === 0) {
            const linkData = insertClientToContactPersonSchema.parse({
              organizationId: organization.organizationId,
              clientId: contact.id,
              contactPersonId: person.id,
              roleAtClient: faker.person.jobTitle(),
              isPrimaryContactForClient: i === 0,
              createdByUserId: randomUser.userId,
              updatedByUserId: randomUser.userId,
            });

            await db.insert(clientToContactPersons).values([linkData]);
            console.log(`  ✓ Linked ${person.firstName} ${person.lastName} to ${contact.name}`);
          }
        }
      }

      // ===== CREATE SALES PIPELINES (with Faker.js) =====
      console.log('🔄 Creating sales pipelines with Faker.js...');
      for (let i = 0; i < SEED_CONFIG.PIPELINES_PER_ORG; i++) {
        const randomUser = randomFromArray(allUsers);
        const pipelineData = insertSalesPipelineSchema.parse(
          generateSalesPipeline(organization.organizationId, randomUser.userId)
        );
        const [pipeline] = await db.insert(sales_pipelines).values([pipelineData]).returning();
        createdPipelines.push({
          ...pipeline,
          stages: [],
        });
        console.log(`  ✓ Created pipeline: ${pipeline.name}`);
      }

      // ===== CREATE PIPELINE STAGES =====
      console.log('📊 Creating pipeline stages...');
      const stageNameSets = [
        ['Lead', 'Qualified', 'Proposal', 'Closed'],
        ['Discovery', 'Demo', 'Negotiation', 'Won'],
        ['Initial Contact', 'Needs Analysis', 'Quote', 'Decision'],
        ['Prospect', 'Meeting', 'Proposal', 'Contract'],
      ];

      for (const pipeline of createdPipelines) {
        const randomUser = randomFromArray(allUsers);
        const stageNameSet = randomFromArray(stageNameSets);

        for (let i = 0; i < stageNameSet.length; i++) {
          const stageData = insertPipelineStageSchema.parse(
            generatePipelineStage(
              organization.organizationId,
              pipeline.id,
              stageNameSet[i],
              i + 1,
              stageNameSet.length,
              randomUser.userId
            )
          );
          const [stage] = await db.insert(pipeline_stages).values([stageData]).returning();
          createdStages.push(stage);
        }
      }

      // ===== CREATE OPPORTUNITIES (with Faker.js) =====
      console.log('💼 Creating opportunities with Faker.js...');
      for (let i = 0; i < SEED_CONFIG.OPPORTUNITIES_PER_ORG; i++) {
        const randomContact = randomFromArray(createdContacts);
        const randomPerson = randomFromArray(createdPersons);
        const randomUser = randomFromArray(allUsers);
        const randomPipeline = randomFromArray(createdPipelines);
        const pipelineStages = createdStages.filter(s => s.salesPipelineId === randomPipeline.id);
        const randomStage = randomFromArray(pipelineStages);

        const opportunityData = insertOpportunitySchema.parse(
          generateOpportunity(
            organization.organizationId,
            randomContact.id,
            randomPerson.id,
            randomPipeline.id,
            randomStage.id,
            randomUser.userId
          )
        );

        await db.insert(opportunities).values([opportunityData]);
      }

      // ===== CREATE SERVICE CATEGORIES (with Faker.js) =====
      console.log('📂 Creating hierarchical service categories...');

      const mainCategoryNames = Object.keys(SERVICE_CATEGORY_STRUCTURE);

      const categoryHierarchy: Record<
        string,
        { main: CategoryRecord; subs: CategoryRecord[]; subSubs: CategoryRecord[] }
      > = {};

      // Create main categories
      for (let i = 0; i < SEED_CONFIG.MAIN_CATEGORIES; i++) {
        const randomUser = randomFromArray(allUsers);
        const mainCategoryName = mainCategoryNames[i];

        const mainCategory = await createCategoryOptimized(
          mainCategoryName,
          faker.lorem.sentence(),
          null, // no parent for main categories
          organization.organizationId,
          randomUser.userId
        );

        createdCategories.push(mainCategory);
        categoryHierarchy[mainCategoryName] = { main: mainCategory, subs: [], subSubs: [] };
        console.log(`  ✓ Created main category: ${mainCategory.name}`);

        // Create subcategories for this main category
        const structure = SERVICE_CATEGORY_STRUCTURE[mainCategoryName];
        if (!structure) {
          console.warn(`Structure not found for category: ${mainCategoryName}`);
          continue;
        }

        const numSubcategories = randomInt(
          SEED_CONFIG.SUBCATEGORIES_PER_MAIN,
          Math.min(SEED_CONFIG.SUBCATEGORIES_PER_MAIN + 1, structure.subcategories.length)
        );

        for (let j = 0; j < numSubcategories; j++) {
          const randomUser = randomFromArray(allUsers);
          const subCategoryName = structure.subcategories[j];

          const subCategory = await createCategoryOptimized(
            subCategoryName,
            faker.lorem.sentence(),
            mainCategory.id, // parent category
            organization.organizationId,
            randomUser.userId
          );

          createdCategories.push(subCategory);
          categoryHierarchy[mainCategoryName].subs.push(subCategory);
          console.log(`  ✓ Created subcategory: ${subCategory.name} (under ${mainCategory.name})`);

          // Maybe create sub-subcategories (third level)
          if (faker.helpers.maybe(() => true, { probability: SEED_CONFIG.SUB_SUBCATEGORIES_CHANCE })) {
            const subSubStructure = structure.subSubcategories[subCategoryName];
            if (subSubStructure && Array.isArray(subSubStructure) && subSubStructure.length > 0) {
              const numSubSubcategories = randomInt(2, Math.min(4, subSubStructure.length));

              for (let k = 0; k < numSubSubcategories; k++) {
                const randomUser = randomFromArray(allUsers);
                const subSubCategoryName = subSubStructure[k];

                const subSubCategory = await createCategoryOptimized(
                  subSubCategoryName,
                  faker.lorem.sentence(),
                  subCategory.id, // parent subcategory
                  organization.organizationId,
                  randomUser.userId
                );

                createdCategories.push(subSubCategory);
                categoryHierarchy[mainCategoryName].subSubs.push(subSubCategory);
                console.log(`    ✓ Created sub-subcategory: ${subSubCategory.name} (under ${subCategory.name})`);
              }
            }
          }
        }
      }

      // ===== CREATE SERVICE ITEMS (with Faker.js) =====
      console.log('🛠️  Creating service items for each category...');

      // Create items for each category
      for (const category of createdCategories) {
        const numItems = randomInt(SEED_CONFIG.ITEMS_PER_CATEGORY_MIN, SEED_CONFIG.ITEMS_PER_CATEGORY_MAX);

        for (let i = 0; i < numItems; i++) {
          const randomUser = randomFromArray(allUsers);
          const serviceItemData = insertServiceItemSchema.parse(
            generateServiceItem(organization.organizationId, category, randomUser.userId)
          );
          const [serviceItem] = await db.insert(standardServiceItems).values([serviceItemData]).returning();
          createdServiceItems.push(serviceItem);
          console.log(`  ✓ Created service item: ${serviceItem.name} (${serviceItem.code}) in ${category.name}`);
        }
      }

      // Create a "Servicii Generale" category for uncategorized items
      console.log('📝 Creating uncategorized service items...');
      const randomUser = randomFromArray(allUsers);

      const generalCategory = await createCategoryOptimized(
        'Servicii Generale',
        'Servicii diverse care nu se încadrează în categoriile specifice',
        null, // no parent for general category
        organization.organizationId,
        randomUser.userId
      );

      createdCategories.push(generalCategory);
      console.log(`  ✓ Created general category: ${generalCategory.name}`);

      // Create uncategorized items
      for (let i = 0; i < SEED_CONFIG.UNCATEGORIZED_ITEMS; i++) {
        const randomUser = randomFromArray(allUsers);
        const serviceItemData = insertServiceItemSchema.parse(
          generateServiceItem(organization.organizationId, generalCategory, randomUser.userId)
        );
        const [serviceItem] = await db.insert(standardServiceItems).values([serviceItemData]).returning();
        createdServiceItems.push(serviceItem);
        console.log(`  ✓ Created uncategorized item: ${serviceItem.name} (${serviceItem.code})`);
      }

      console.log(`✅ Completed data creation for ${organization.name}:`);
      console.log(`  - ${createdContacts.length} contacts`);
      console.log(`  - ${createdPersons.length} persons`);
      console.log(`  - ${createdPipelines.length} sales pipelines`);
      console.log(`  - ${createdStages.length} pipeline stages`);
      console.log(`  - ${SEED_CONFIG.OPPORTUNITIES_PER_ORG} opportunities`);
      console.log(`  - ${createdCategories.length} service categories`);
      console.log(`  - ${createdServiceItems.length} service items`);
    }

    console.log('\n🎉 Database seeding completed successfully!');
    console.log(`📊 Final Summary:`);
    console.log(`  - ${organizations_list.length} organizations`);
    console.log(`  - ${allUsers.length} users (linked to all organizations)`);
    console.log(`  - Data created for each organization individually`);
  } catch (error) {
    console.error('❌ Error during seeding:', error);
    process.exit(1);
  }
};

main()
  .catch(error => {
    console.error('❌ Seed script failed:', error);
    process.exit(1);
  })
  .finally(async () => {
    try {
      await connection.end();
      console.log('🔌 Database connection closed successfully');
    } catch (error) {
      console.error('❌ Error closing database connection:', error);
    }
    process.exit(0);
  });
