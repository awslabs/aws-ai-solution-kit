To uninstall AI Solution Kit, you must delete the AWS CloudFormation stack. 

You can use either the AWS Management Console or the AWS Command Line Interface (CLI) to delete the CloudFormation stack.

## Using the AWS Management Console

1. Sign in to the [AWS CloudFormation][cloudformation-console] console.
2. Select this solution’s installation stack.
3. Choose **Delete**.

## Using AWS Command Line Interface

Determine whether the AWS CLI is available in your environment. For installation instructions, see [What Is the AWS Command Line Interface][aws-cli] in the *AWS CLI User Guide*. After confirming that the AWS CLI is available, run the following command.

```bash
$ aws cloudformation delete-stack --stack-name <installation-stack-name>
```


[cloudformation-console]: https://console.aws.amazon.com/cloudformation/home
[aws-cli]: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html
