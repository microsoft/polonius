param name string
param location string = resourceGroup().location
param tags object = {}

param applicationInsightsName string
param containerAppsEnvironmentName string
param containerRegistryName string
param exists bool
param identityName string
param serviceName string = 'web'
param keyVaultName string

resource webIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: keyVaultName
}

// Give the app access to KeyVault
module webKeyVaultAccess './core/security/keyvault-access.bicep' = {
  name: 'web-keyvault-access'
  params: {
    keyVaultName: keyVault.name
    principalId: webIdentity.properties.principalId
  }
}

module app 'core/host/container-app-upsert.bicep' = {
  name: '${serviceName}-container-app-module'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName })
    identityName: webIdentity.name
    exists: exists
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    env: [
      {
        name: 'RUNNING_IN_PRODUCTION'
        value: 'true'
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsights.properties.ConnectionString
      }
      {
        name: 'AZURE_COSMOS_CONNECTION_STRING'
        secretRef: 'azure-cosmos-connection-string'
      }
      {
        name: 'SECRET_KEY'
        secretRef: 'secret-key'
      }
      {
        name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
        secretRef: 'azure-openai-deployment-name'
      }
      {
        name: 'AZURE_OPENAI_API_KEY'
        secretRef: 'azure-openai-api-key'
      }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        secretRef: 'azure-openai-endpoint'
      }
    ]
    secrets: [
        {
          name: 'secret-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/SECRETKEY'
          identity: webIdentity.id
        }
        {
          name: 'azure-cosmos-connection-string'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/AZURE-COSMOS-CONNECTION-STRING'
          identity: webIdentity.id
        }
        {
          name: 'azure-openai-deployment-name'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/AZURE-OPENAI-DEPLOYMENT-NAME'
          identity: webIdentity.id
        }
        {
          name: 'azure-openai-api-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/APIM-SUBSCRIPTION-KEY'
          identity: webIdentity.id
        }
        {
          name: 'azure-openai-endpoint'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/AZURE-OPENAI-ENDPOINT'
          identity: webIdentity.id
        }
      ]
    targetPort: 8000
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = webIdentity.properties.principalId
output SERVICE_WEB_NAME string = app.outputs.name
output SERVICE_WEB_URI string = app.outputs.uri
output SERVICE_WEB_IMAGE_NAME string = app.outputs.imageName

output uri string = app.outputs.uri
