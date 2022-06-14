## Upgrade scenario 1

When you have deployed and are using some of the API features from release 1.0.0, you can continue to use the original APIs that have been deployed in your Amazon account while deploying the features provided in the new APIs available in release 1.2.0. 

The interface definition parameters of the four APIs (General OCR, Image Super Resolution, Human Image Segmentation, Pornography Detection) in the release 1.0.0 are identical to the same four features in release 1.2.0, and you only need to replace the original URLs to use them. 

## Upgrade scenario 2

If you want to switch the original API invoke URL to the new version, you can perform the following operations after deploying the new version:

1. Sign in to the [Amazon CloudFormation console](https://console.aws.amazon.com/cloudformation/).
2. On the **Stacks** page, select the solution’s root stack.
3. Choose the **Outputs** tab, and find the invoke URL.
4. Replace the old invoke URL in the code.
5. After the replacement, you can completely remove the original stack in the Amazon CloudFormation console to avoid incurring extra cost, which takes about 10 minutes.