param name string
param location string = resourceGroup().location
param tags object = {}
@description('The custom subdomain name used to access the API. Defaults to the value of the name parameter.')
param customSubDomainName string = name
param deployments array = []
param kind string = 'OpenAI'
param publicNetworkAccess string = 'Enabled'
param sku object = {
  name: 'S0'
}

param keyVaultName string

resource account 'Microsoft.CognitiveServices/accounts@2022-10-01' = {
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
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2022-10-01' = [for deployment in deployments: {
  parent: account
  name: deployment.name
  properties: {
    model: deployment.model
    raiPolicyName: contains(deployment, 'raiPolicyName') ? deployment.raiPolicyName : null
    scaleSettings: deployment.scaleSettings
  }
}]

var settings = [
  {
    name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
    value: 'gpt-35-turbo-16k'
  }
]

@batchSize(1)
resource keyVaultSecrets 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = [for setting in settings: {
  parent: keyVault
  name: setting.name
  properties: {
    value: setting.value
  }
}]

resource keyVaultEndpoint 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = {
  parent: keyVault
  name: 'AZURE_OPENAI_ENDPOINT'
  properties: {
    value: account.properties.endpoint
  }
}

resource keyVaultApiKey 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = {
  parent: keyVault
  name: 'AZURE_OPENAI_API_KEY'
  properties: {
    value: account.listKeys().key1
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: keyVaultName
}

output endpoint string = account.properties.endpoint
output id string = account.id
output name string = account.name
