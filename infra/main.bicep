targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@secure()
@description('Secret Key')
param secretKey string

param webAppExists bool = false

@description('Id of the user or app to assign application roles')
param principalId string = ''

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var prefix = '${name}-${resourceToken}'
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

var deployments = [
  {
    name: 'gpt-35-turbo-16k'
    model: {
      format: 'OpenAI'
      name: 'gpt-35-turbo-16k'
      version: '0613'
    }
    sku: {
      name: 'Standard'
      capacity: 120
    }
    raiPolicyName: 'CustomContentFilter643'
  }
]

var raiPolicies = [
  {
    name: 'CustomContentFilter643'
    mode: 'Default'
    basePolicyName: 'Microsoft.Default'
    contentFilters: [
      {
          name: 'hate'
          allowedContentLevel: 'High'
          blocking: true
          enabled: true
          source: 'Prompt'
      }
      {
          name: 'sexual'
          allowedContentLevel: 'High'
          blocking: true
          enabled: true
          source: 'Prompt'
      }
      {
          name: 'selfharm'
          allowedContentLevel: 'High'
          blocking: true
          enabled: true
          source: 'Prompt'
      }
      {
          name: 'violence'
          allowedContentLevel: 'High'
          blocking: true
          enabled: true
          source: 'Prompt'
      }
      {
          name: 'hate'
          allowedContentLevel: 'High'
          blocking: true
          enabled: true
          source: 'Completion'
      }
      {
          name: 'sexual'
          allowedContentLevel: 'High'
          blocking: true
          enabled: true
          source: 'Completion'
      }
      {
          name: 'selfharm'
          allowedContentLevel: 'High'
          blocking: true
          enabled: true
          source: 'Completion'
      }
      {
          name: 'violence'
          allowedContentLevel: 'High'
          blocking: true
          enabled: true
          source: 'Completion'
      }
      {
          name: 'jailbreak'
          blocking: true
          enabled: true
          source: 'Prompt'
      }
    ]
  }
]

// Azure OpenAI
module aoai './core/ai/cognitiveservices.bicep' = {
  name: 'aoai'
  scope: resourceGroup
  params: {
    name: '${take(prefix, 17)}-ai'
    location: location
    tags: tags
    keyVaultName: keyVault.outputs.name
    deployments: deployments
    policies: raiPolicies
  }
}

// Store secrets in a keyvault
module keyVault './core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: resourceGroup
  params: {
    name: '${take(replace(prefix, '-', ''), 17)}-vault'
    location: location
    tags: tags
    principalId: principalId
  }
}

module db 'db.bicep' = {
  name: 'db'
  scope: resourceGroup
  params: {
    name: 'dbserver'
    location: location
    tags: tags
    prefix: prefix
    keyVaultName: keyVault.outputs.name
    dbserverDatabaseName: 'polonius'
  }
}

// Monitor application with Azure Monitor
module monitoring 'core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    applicationInsightsDashboardName: '${prefix}-appinsights-dashboard'
    applicationInsightsName: '${prefix}-appinsights'
    logAnalyticsName: '${take(prefix, 50)}-loganalytics' // Max 63 chars
  }
}

// Container apps host (including container registry)
module containerApps 'core/host/container-apps.bicep' = {
  name: 'container-apps'
  scope: resourceGroup
  params: {
    name: 'app'
    location: location
    containerAppsEnvironmentName: '${prefix}-containerapps-env'
    containerRegistryName: '${replace(prefix, '-', '')}registry'
    logAnalyticsWorkspaceName: monitoring.outputs.logAnalyticsWorkspaceName
  }
}

// Web frontend
module web 'web.bicep' = {
  name: 'web'
  scope: resourceGroup
  dependsOn: [aoai, db, apimapi]
  params: {
    name: replace('${take(prefix, 19)}-ca', '--', '-')
    location: location
    tags: tags
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    keyVaultName: keyVault.outputs.name
    identityName: '${prefix}-id-web'
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
    exists: webAppExists
  }
}



// APIM
module apim './core/gateway/apim.bicep' = {
  name: 'apim'
  dependsOn: [aoai]
  scope: resourceGroup
  params: {
    name: '${prefix}-apim'
    location: location
    tags: tags
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    keyVaultName: keyVault.outputs.name
  }
}

module apimapi './core/gateway/openai-apim-api.bicep' = {
  name: 'apim-api'
  scope: resourceGroup
  params: {
    apiManagementServiceName: apim.outputs.apimServiceName
    openAIEndpoint: aoai.outputs.endpoint
  }
}

var secrets = [
  {
    name: 'SECRETKEY'
    value: secretKey
  }  
]

@batchSize(1)
module keyVaultSecrets './core/security/keyvault-secret.bicep' = [for secret in secrets: {
  name: 'keyvault-secret-${secret.name}'
  scope: resourceGroup
  params: {
    keyVaultName: keyVault.outputs.name
    name: secret.name
    secretValue: secret.value
  }
}]

output AZURE_LOCATION string = location
output AZURE_CONTAINER_ENVIRONMENT_NAME string = containerApps.outputs.environmentName
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerApps.outputs.registryLoginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerApps.outputs.registryName
output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = web.outputs.SERVICE_WEB_IDENTITY_PRINCIPAL_ID
output SERVICE_WEB_NAME string = web.outputs.SERVICE_WEB_NAME
output SERVICE_WEB_URI string = web.outputs.SERVICE_WEB_URI
output SERVICE_WEB_IMAGE_NAME string = web.outputs.SERVICE_WEB_IMAGE_NAME
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.endpoint
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output APPLICATIONINSIGHTS_NAME string = monitoring.outputs.applicationInsightsName

output BACKEND_URI string = web.outputs.uri
