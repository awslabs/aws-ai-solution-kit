// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0


const express = require('express')
const serverless = require('serverless-http')
const swaggerUi = require('swagger-ui-express')
const YAML = require('yamljs');
const AWS = require('aws-sdk');

var apigateway = new AWS.APIGateway();

var params = {
  restApiId: process.env.REST_API_ID,
  limit: '100',
};

const apiPaths = []
var synced = true;
apigateway.getResources(params, function (err, data) {
  if (err) console.log(err, err.stack);
  else {
    for (i in data['items']) {
      apiPaths.push(data['items'][i]['path']);
    }
    console.log(apiPaths);
    synced = false;
  }
});

while(synced) {
  require('deasync').sleep(10);
}

const swaggerDocument = YAML.load(process.env.OPEN_API);
swaggerDocument.servers = [{ url: process.env.SWAGGER_SPEC_URL }];

for (i in swaggerDocument.paths) {
  // console.log(swaggerDocument.paths);
  if (!apiPaths.includes(i)) {
    swaggerDocument.paths[i] = null;
  }
}

for (i in swaggerDocument.tags) {
  // console.log(swaggerDocument.tags[i]['name']);
  var found = false;
  for (j in swaggerDocument.paths) {
    for (var k in swaggerDocument.paths[j]) {
      if (swaggerDocument.paths[j][k]['tags'].includes(swaggerDocument.tags[i]['name'])) {
        found = true;
        break;
      }
    }
  }
  if (!found) {
    swaggerDocument.tags[i] = null;
  }
}

const DisableTryItOutPlugin = function () {
  return {
    statePlugins: {
      spec: {
        wrapSelectors: {
          allowTryItOutFor: () => () => false
        }
      }
    }
  };
};

const DisableAuthorizePlugin = function () {
  return {
    wrapComponents: {
      authorizeBtn: () => () => null
    }
  };
};

var swaggerPlugins = 'AWS_IAM' == process.env.AUTH_TYPE ? [DisableTryItOutPlugin, DisableAuthorizePlugin] : [DisableAuthorizePlugin];

var options = {
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: 'AI Solution Kit OpenAPI',
  customfavIcon: '/favicon.ico',
  explorer: true,
  // customJs: '/custom.js',
  defaultModelsExpandDepth: -1,
  swaggerOptions: {
    plugins: swaggerPlugins
  }
};

const app = express()
app.use(
  '/api-explorer',
  swaggerUi.serve,
  swaggerUi.setup(swaggerDocument, options)
)

app.use(express.static('.'))
module.exports.handler = serverless(app)

// // test with --node app.js
// app.listen(3000, () => {
//   console.log(`Open http://localhost:3000/api-explorer`)
// })
