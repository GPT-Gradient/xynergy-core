/**
 * Initialize Operational Layer Database
 * Sets up Firestore collections and sample data for Phase 1
 *
 * Usage:
 * ts-node scripts/init-operational-layer-database.ts
 */

import * as admin from 'firebase-admin';

// Initialize Firebase Admin
if (process.env.GOOGLE_APPLICATION_CREDENTIALS) {
  admin.initializeApp();
} else {
  const serviceAccount = require('../serviceAccountKey.json');
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
  });
}

const db = admin.firestore();

/**
 * Create system permission templates
 */
async function createPermissionTemplates() {
  console.log('Creating permission templates...');

  const templates = [
    {
      id: 'beta_user_phase_1',
      name: 'Beta User - Phase 1',
      description: 'Permissions for Phase 1 beta users (First 100 users)',
      targetRole: 'beta_user_p1',
      permissions: [
        'crm.read',
        'crm.write',
        'crm.contacts.*',
        'crm.interactions.*',
        'slack.read',
        'slack.write',
        'slack.channels.*',
        'gmail.read',
        'gmail.write',
        'gmail.messages.*',
      ],
      isSystemTemplate: true,
      createdBy: 'system',
      createdAt: new Date().toISOString(),
    },
    {
      id: 'beta_user_phase_2',
      name: 'Beta User - Phase 2',
      description: 'Permissions for Phase 2 beta users (100-700 users)',
      targetRole: 'beta_user_p2',
      permissions: [
        'crm.read',
        'crm.write',
        'slack.read',
        'slack.write',
        'gmail.read',
        'gmail.write',
      ],
      isSystemTemplate: true,
      createdBy: 'system',
      createdAt: new Date().toISOString(),
    },
    {
      id: 'beta_user_phase_3',
      name: 'Beta User - Phase 3',
      description: 'Permissions for Phase 3 beta users (700+ users)',
      targetRole: 'beta_user_p3',
      permissions: [
        'crm.read',
        'slack.read',
        'gmail.read',
      ],
      isSystemTemplate: true,
      createdBy: 'system',
      createdAt: new Date().toISOString(),
    },
    {
      id: 'team_admin',
      name: 'Team Admin',
      description: 'Full access to tenant resources',
      targetRole: 'team_admin',
      permissions: ['*'],
      isSystemTemplate: true,
      createdBy: 'system',
      createdAt: new Date().toISOString(),
    },
    {
      id: 'team_member',
      name: 'Team Member',
      description: 'Basic read access',
      targetRole: 'team_member',
      permissions: [
        'crm.read',
        'slack.read',
        'gmail.read',
      ],
      isSystemTemplate: true,
      createdBy: 'system',
      createdAt: new Date().toISOString(),
    },
  ];

  for (const template of templates) {
    await db.collection('permission_templates').doc(template.id).set(template);
    console.log(`  ✅ Created template: ${template.name}`);
  }

  console.log(`✅ Created ${templates.length} permission templates\n`);
}

/**
 * Create sample tenants
 */
async function createSampleTenants() {
  console.log('Creating sample tenants...');

  const tenants = [
    {
      id: 'clearforge',
      name: 'ClearForge (Master)',
      type: 'master',
      businessEntityId: 'clearforge',
      status: 'active',
      isBetaTenant: false,
      features: ['all'],
      featureFlags: {
        betaProgram: true,
        advancedAnalytics: true,
        aiFeatures: true,
      },
      limits: {
        maxUsers: 1000,
        maxStorage: 1000000, // 1TB in MB
        maxApiCalls: 1000000,
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: 'nexus',
      name: 'NEXUS (Continuum Gen 1)',
      type: 'continuum_project',
      businessEntityId: 'nexus',
      status: 'active',
      isBetaTenant: true,
      betaPhase: 'phase_1',
      features: ['crm', 'communication', 'ai'],
      featureFlags: {
        betaProgram: true,
        advancedAnalytics: false,
        aiFeatures: true,
      },
      limits: {
        maxUsers: 100,
        maxStorage: 50000, // 50GB in MB
        maxApiCalls: 100000,
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ];

  for (const tenant of tenants) {
    await db.collection('tenants').doc(tenant.id).set(tenant);
    console.log(`  ✅ Created tenant: ${tenant.name}`);
  }

  console.log(`✅ Created ${tenants.length} tenants\n`);
}

/**
 * Create sample super admin user
 */
async function createSuperAdminUser() {
  console.log('Creating super admin user...');

  const adminUser = {
    uid: 'admin_shawn',
    email: 'shawn@clearforge.com',
    name: 'Shawn Sloan',
    globalRole: 'super_admin',
    activeTenantId: 'clearforge',
    tenantRoles: {
      clearforge: {
        role: 'super_admin',
        permissions: ['*'],
        grantedAt: new Date().toISOString(),
        grantedBy: 'system',
      },
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  await db.collection('users').doc(adminUser.uid).set(adminUser);
  console.log(`  ✅ Created super admin: ${adminUser.name} (${adminUser.email})`);
  console.log(`✅ Super admin created\n`);
}

/**
 * Create sample beta user
 */
async function createSampleBetaUser() {
  console.log('Creating sample beta user...');

  const betaUser = {
    uid: 'user_beta_test',
    email: 'beta@example.com',
    name: 'Test Beta User',
    globalRole: null,
    activeTenantId: 'nexus',
    tenantRoles: {
      nexus: {
        role: 'beta_user_p1',
        permissions: [
          'crm.read',
          'crm.write',
          'crm.contacts.*',
          'slack.read',
          'slack.write',
          'gmail.read',
          'gmail.write',
        ],
        grantedAt: new Date().toISOString(),
        grantedBy: 'admin_shawn',
      },
    },
    betaStatus: {
      phase: 'phase_1',
      joinedAt: new Date().toISOString(),
      lifetimeAccess: ['nexus'],
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  await db.collection('users').doc(betaUser.uid).set(betaUser);
  console.log(`  ✅ Created beta user: ${betaUser.name} (${betaUser.email})`);
  console.log(`✅ Beta user created\n`);
}

/**
 * Main initialization function
 */
async function initializeDatabase() {
  console.log('===================================');
  console.log('Operational Layer Database Init');
  console.log('Phase 1: Foundation');
  console.log('===================================\n');

  try {
    await createPermissionTemplates();
    await createSampleTenants();
    await createSuperAdminUser();
    await createSampleBetaUser();

    console.log('===================================');
    console.log('✅ Database initialization complete!');
    console.log('===================================\n');

    console.log('Summary:');
    console.log('- 5 permission templates created');
    console.log('- 2 tenants created (clearforge, nexus)');
    console.log('- 1 super admin created (shawn@clearforge.com)');
    console.log('- 1 beta user created (beta@example.com)');
    console.log('');
    console.log('Test Credentials:');
    console.log('Super Admin: shawn@clearforge.com');
    console.log('Beta User: beta@example.com');
    console.log('');
    console.log('Next steps:');
    console.log('1. Deploy Permission Service to Cloud Run');
    console.log('2. Update Intelligence Gateway with middleware');
    console.log('3. Test permission flows end-to-end');

    process.exit(0);
  } catch (error) {
    console.error('❌ Error initializing database:', error);
    process.exit(1);
  }
}

// Run initialization
initializeDatabase();
