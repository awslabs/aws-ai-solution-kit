---
title: Prevent DDoS attacks
weight: 7
---

In this step of the workshop, we will demonstrate the functionality provided by the WAF & Shield Automations Solution to detect this type of attack and block the responsible IP address in AWS WAF.

## Introduction
HTTP flood rule protects against attacks that consist of a large number of requests from a particular IP address, such as a web-layer DDoS attack or a brute-force login attempt. With this rule, you can set a threshold that defines the maximum number of incoming requests allowed from a single IP address within five minutes.

## Testing with Locust
[Locust](https://github.com/locustio/locust) is an open-source performance testing tool. You can install it in AWS CloudShell with the commands below.

        sudo yum install GCC python3-devel
<br>

        sudo pip3 install locust

Upload the cloudFronttest.py with the content below into AWS CloudShell.
        
        from locust import HttpUser, task

        class WebsiteUser(HttpUser):

            @task
            def access_demo_website(self):
                self.client.get("/")

And run locust for testing
        locust -f cloudFronttest.py --host http://*********.cloudfront.net --headless -u 500 -r 1

Access the Juice Shop with curl in the CloudShell again, it will be blocked by the AWS WAF.

        curl http://*********.cloudfront.net

## Conclusion
In this section, you learned about how-to simulate a web-layer DDoS attack, and the AWS WAF can stop the attacks by the HTTP Flood rule.