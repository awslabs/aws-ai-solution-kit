The API Resource Browser provides a display framework that offers an interactive documentation site based on [Swagger UI](https://swagger.io/tools/swagger-ui/) to facilitate the reading of AI application interface specification documents defined based on the OpenAPI specification and to support integration testing. The following is an example of how to view and test API calls using the **API Resource Browser**.

When you deploy a solution via Amazon CloudFormation (deployment.md#amazon-cloudformation) and set the parameter **APIExplorer** to *yes*, you can see the API calls in Amazon CloudFormation's Outputs tab, click on the URL to access the [Swagger UI](https://swagger.io/tools/swagger-ui/) based API resource browser.

If the user does not activate (active) the API in the interaction document when deploying the solution, only the reference definition of the API can be seen in the API Explorer, and online testing is not available. APIs have been classified by functional type into Optical Character Recognition (OCR), Facial & Body (face and body recognition), Image Understanding, Computer Vision Production, Natural After expanding the corresponding types, you can view the request method and pattern definition of the API. results. This test feature is currently only available when the API Gateway authentication method is NONE.

Here is an example of how to test the API using the **General Text Recognition** API.

- Expand the **/general-ocr-standard** path in the **Optical Character Recognition(OCR)** tab to see the request method of the **general-ocr-standard** API standard model.
- Click **Try it out** and enter the sample data for testing in the blank field under **Request body**, e.g.
``` json
{
"url": "https://images-cn.ssl-images-amazon.cn/images/G/28/AGS/LIANG/Deals/2020/Dealpage_KV/1500300.jpg"
}
```
- After confirming that the format is correct, click the blue **Execute** below, and you can see the text-aware JSON results returned at **Responses body** after running, and you can save the processing results by copying or downloading the button link on the right.
- In **Response headers** you can see the details of the response headers.
- Click the blue **Execute** button to the right of **Clear** to clear the **Request body** and **Responses** test results.
