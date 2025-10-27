// Main entry point for Azure Functions
// This file imports all function definitions to register them

import './functions/scrapeTwitter';

// Export app for Azure Functions runtime
export { app } from '@azure/functions';




