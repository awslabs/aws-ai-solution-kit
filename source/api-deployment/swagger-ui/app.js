const express = require('express')
const serverless = require('serverless-http')
const swaggerUi = require('swagger-ui-express')
const YAML = require('yamljs');
const swaggerDocument = YAML.load('./openapi.yaml');
swaggerDocument.servers = [{ url: process.env.SWAGGER_SPEC_URL }]

var options = {
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: 'AI Solution Kit Open API',
  customfavIcon: './favicon.ico',
  explorer: true
};

const app = express()
app.use(
  '/api-docs',
  swaggerUi.serve,
  swaggerUi.setup(swaggerDocument, options)
)

module.exports.handler = serverless(app)

// app.listen(3000, () => {
//   console.log(`Example app listening at http://localhost:3000`)
// })