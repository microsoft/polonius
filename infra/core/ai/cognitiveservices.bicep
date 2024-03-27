param name string
param location string = resourceGroup().location
param tags object = {}
@description('The custom subdomain name used to access the API. Defaults to the value of the name parameter.')
param customSubDomainName string = name
param deployments array = []
param policies array = []
param kind string = 'OpenAI'
param publicNetworkAccess string = 'Enabled'
param sku object = {
  name: 'S0'
}

param keyVaultName string

resource account 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: kind
  properties: {
    customSubDomainName: customSubDomainName
    publicNetworkAccess: publicNetworkAccess
  }
  sku: sku
}

@batchSize(1)
resource raiPolicy 'Microsoft.CognitiveServices/accounts/raiPolicies@2023-10-01-preview' = [for policy in policies: {
  parent: account
  name: policy.name
  properties: {
    mode: policy.mode
    basePolicyName: policy.basePolicyName
    contentFilters: policy.contentFilters
  }
}]

@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in deployments: {
  dependsOn: [raiPolicy]
  parent: account
  name: deployment.name
  sku: deployment.sku
  properties: {
    model: deployment.model
    raiPolicyName: contains(deployment, 'raiPolicyName') ? deployment.raiPolicyName : null
  }
}]

module keyVaultSecrets '../security/keyvault-secret.bicep' = {
  name: 'keyvault-secret-deployment-name'
  scope: resourceGroup()
  params: {
    keyVaultName: keyVaultName
    name: 'AZURE-OPENAI-DEPLOYMENT-NAME'
    secretValue: deployments[0].name
  }
}

module keyVaultSecretApiSecret '../security/keyvault-secret.bicep' = {
  name: 'keyvault-secret-api-key'
  scope: resourceGroup()
  params: {
    keyVaultName: keyVaultName
    name: 'AZURE-OPENAI-API-KEY'
    secretValue: account.listKeys().key1
  }
}

output endpoint string = account.properties.endpoint
output id string = account.id
output name string = account.name
