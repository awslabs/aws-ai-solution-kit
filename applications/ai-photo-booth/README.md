## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template

## Deployment Steps

1. Deploy AI Solution Kit following the instructions
1. Record the API Gateway endpoint of AI Solution Kit, e.g. https://aa11bb22cc33.execute-api.us-east-1.amazonaws.com/prod
1. Run the following command
   > npm run build && cdk deploy --context api=<API_ENDPOINT>