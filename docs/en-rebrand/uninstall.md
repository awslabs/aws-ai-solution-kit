To uninstall AI Solution Kit, you must delete the Amazon CloudFormation stack. 

You can use either the Amazon Web Services Management Console or the Amazon Web Services Command Line Interface (CLI) to delete the CloudFormation stack.

## Using the Amazon Web Services Management Console

1. Sign in to the [Amazon CloudFormation][cloudformation-console] console.
2. Select this solution’s installation stack.
3. Choose **Delete**.

## Using Amazon Web Services Command Line Interface

Determine whether the Amazon Web Services CLI is available in your environment. For installation instructions, see [What Is the Amazon Web Services Command Line Interface][aws-cli] in the *Amazon Web Services CLI User Guide*. After confirming that the Amazon Web Services CLI is available, run the following command.

```bash
$ aws cloudformation delete-stack --stack-name <installation-stack-name>
```


[cloudformation-console]: https://console.aws.amazon.com/cloudformation/home
[aws-cli]: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html
