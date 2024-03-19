
param name string
param location string = resourceGroup().location
param tags object = {}
param prefix string
param dbserverDatabaseName string
param keyVaultName string

module dbserver 'core/database/cosmos/mongo/cosmos-mongo-db.bicep' = {
  name: name
  params: {
    accountName: '${prefix}-mongodb'
    location: location
    databaseName: dbserverDatabaseName
    tags: tags
    keyVaultName: keyVaultName
  }
}

output dbserverDatabaseName string = dbserverDatabaseName
