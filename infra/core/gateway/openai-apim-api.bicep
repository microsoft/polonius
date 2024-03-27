param apiManagementServiceName string
param apiName string = 'azure-openai-service-api'
param apiPath string = '/'
param openAIEndpoint string

resource apiManagementService 'Microsoft.ApiManagement/service@2022-08-01' existing = {
  name: apiManagementServiceName
}

resource apiManagementApi 'Microsoft.ApiManagement/service/apis@2022-08-01' = {
  name: apiName
  parent: apiManagementService
  properties: {
    displayName: 'Azure OpenAI Service API'
    description: 'Azure OpenAI APIs for completions and search'
    subscriptionRequired: true
    serviceUrl: openAIEndpoint
    path: apiPath
    protocols: [
      'https'
    ]    
    subscriptionKeyParameterNames: {
      header: 'Ocp-Apim-Subscription-Key'
      query: 'subscription-key'
    }
  }
}

resource apiManagementApiPolicy 'Microsoft.ApiManagement/service/apis/policies@2022-08-01' = {
  name: 'policy'
  parent: apiManagementApi
  properties: {
    value: '<policies> <inbound> <base /> <set-header name="api-key" exists-action="append"> <value>{{openai-api-key}}</value> </set-header> </inbound> <backend> <base /> </backend> <outbound> <base /> </outbound> <on-error> <base /> </on-error> </policies>'
    format: 'xml'
  }
}

resource chatCompletionOperation 'Microsoft.ApiManagement/service/apis/operations@2022-08-01' = {
  parent: apiManagementApi
  name: 'ChatCompletions_Create'
  properties: {
    displayName: 'Creates a completion for the chat message'
    method: 'POST'
    urlTemplate: '/deployments/{deployment-id}/chat/completions?api-version={api-version}'
    templateParameters: [
      {
        name: 'deployment-id'
        type: 'string'
        required: true
        values: []
        schemaId: azure_openai_service_api_schema.name
        typeName: 'Deployments-deployment-id-ChatCompletionsPostRequest'
      }
      {
        name: 'api-version'
        type: 'string'
        required: true
        values: []
        schemaId: azure_openai_service_api_schema.name
        typeName: 'Deployments-deployment-id-ChatCompletionsPostRequest-1'
      }
    ]
    description: 'Creates a completion for the chat message'
    request: {
      queryParameters: []
      headers: []
      representations: [
        {
          contentType: 'application/json'
          examples: {
            default: {
              value: {}
            }
          }
          schemaId: azure_openai_service_api_schema.name
          typeName: 'Deployments-deployment-id-ChatCompletionsPostRequest-2'
        }
      ]
    }
    responses: [
      {
        statusCode: 200
        description: 'OK'
        representations: [
          {
            contentType: 'application/json'
            examples: {
              default: {
                value: {}
              }
            }
            schemaId: azure_openai_service_api_schema.name
            typeName: 'Deployments-deployment-id-ChatCompletionsPost200ApplicationJsonResponse'
          }
        ]
        headers: []
      }
    ]
  }
}

resource azure_openai_service_api_Completions_Create 'Microsoft.ApiManagement/service/apis/operations@2022-08-01' = {
  parent: apiManagementApi
  name: 'Completions_Create'
  properties: {
    displayName: 'Creates a completion for the provided prompt, parameters and chosen model.'
    method: 'POST'
    urlTemplate: '/deployments/{deployment-id}/completions?api-version={api-version}'
    templateParameters: [
      {
        name: 'deployment-id'
        type: 'string'
        required: true
        values: []
        schemaId: azure_openai_service_api_schema.name
        typeName: 'Deployments-deployment-id-CompletionsPostRequest'
      }
      {
        name: 'api-version'
        type: 'string'
        required: true
        values: []
        schemaId: azure_openai_service_api_schema.name
        typeName: 'Deployments-deployment-id-CompletionsPostRequest-1'
      }
    ]
    description: 'Creates a completion for the provided prompt, parameters and chosen model.'
    request: {
      queryParameters: []
      headers: []
      representations: [
        {
          contentType: 'application/json'
          examples: {
            default: {
              value: {}
            }
          }
          schemaId: azure_openai_service_api_schema.name
          typeName: 'Deployments-deployment-id-CompletionsPostRequest-2'
        }
      ]
    }
    responses: [
      {
        statusCode: 200
        description: 'OK'
        representations: [
          {
            contentType: 'application/json'
            examples: {
              default: {
                value: {}
              }
            }
            schemaId: azure_openai_service_api_schema.name
            typeName: 'Deployments-deployment-id-CompletionsPost200ApplicationJsonResponse'
          }
        ]
        headers: [
          {
            name: 'apim-request-id'
            description: 'Request ID for troubleshooting purposes'
            type: 'string'
            values: []
            schemaId: azure_openai_service_api_schema.name
            typeName: 'Deployments-deployment-id-CompletionsPost200apim-request-idResponseHeader'
          }
        ]
      }
      {
        statusCode: 400
        description: 'Service unavailable'
        representations: [
          {
            contentType: 'application/json'
            examples: {
              default: {
                value: {}
              }
            }
            schemaId: azure_openai_service_api_schema.name
            typeName: 'errorResponse'
          }
        ]
        headers: [
          {
            name: 'apim-request-id'
            description: 'Request ID for troubleshooting purposes'
            type: 'string'
            values: []
            schemaId: azure_openai_service_api_schema.name
            typeName: 'Deployments-deployment-id-CompletionsPostdefaultapim-request-idResponseHeader'
          }
        ]
      }
      {
        statusCode: 500
        description: 'Service unavailable'
        representations: [
          {
            contentType: 'application/json'
            examples: {
              default: {
                value: {}
              }
            }
            schemaId: azure_openai_service_api_schema.name
            typeName: 'errorResponse'
          }
        ]
        headers: [
          {
            name: 'apim-request-id'
            description: 'Request ID for troubleshooting purposes'
            type: 'string'
            values: []
            schemaId: azure_openai_service_api_schema.name
            typeName: 'Deployments-deployment-id-CompletionsPostdefaultapim-request-idResponseHeader'
          }
        ]
      }
    ]
  }
}

resource azure_openai_service_api_embeddings_create 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: apiManagementApi
  name: 'embeddings_create'
  properties: {
    displayName: 'Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.'
    method: 'POST'
    urlTemplate: '/deployments/{deployment-id}/embeddings?api-version={api-version}'
    templateParameters: [
      {
        name: 'deployment-id'
        description: 'The deployment id of the model which was deployed.'
        type: 'string'
        required: true
        values: []
        schemaId: azure_openai_service_api_schema.name
        typeName: 'Deployments-deployment-id-EmbeddingsPostRequest'
      }
      {
        name: 'api-version'
        type: 'string'
        required: true
        values: []
        schemaId: azure_openai_service_api_schema.name
        typeName: 'Deployments-deployment-id-EmbeddingsPostRequest-1'
      }
    ]
    description: 'Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.'
    request: {
      queryParameters: []
      headers: []
      representations: [
        {
          contentType: 'application/json'
          examples: {
            default: {
              value: {}
            }
          }
          schemaId: azure_openai_service_api_schema.name
          typeName: 'Deployments-deployment-id-EmbeddingsPostRequest-2'
        }
      ]
    }
    responses: [
      {
        statusCode: 200
        description: 'OK'
        representations: [
          {
            contentType: 'application/json'
            examples: {
              default: {
                value: {}
              }
            }
            schemaId: azure_openai_service_api_schema.name
            typeName: 'Deployments-deployment-id-EmbeddingsPost200ApplicationJsonResponse'
          }
        ]
        headers: []
      }
    ]
  }  
}

resource azure_openai_service_api_schema 'Microsoft.ApiManagement/service/apis/schemas@2023-05-01-preview' = {
  parent: apiManagementApi
  name: '6601b0fec486511e7cbb3ef6'
  properties: {
    contentType: 'application/vnd.oai.openapi.components+json'
    document: {}
  }
}

