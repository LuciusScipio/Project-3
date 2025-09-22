## Project 3: Automate AWS Resource Monitoring with Python and CloudWatch - Automate CPU usage monitoring on Python Flask App from Project-2 ##

### Steps I used

1. Set up a CloudWatch Dashboard to Monitor the EC2 Instance CPU usage.
2. Create an SNS topic and a subscription with email as protocol.
3. Write a python script: 
    - import the _boto3_ library to:
        - create a _CloudWatch_ client using the `get_metric_statistics` method to programmatically fetch CPU utilization data for the EC2 instance, 
        - create the _EC2_ client using the `describe_instances` method to find the instance ID of the EC2 instance, 
        - and to publish a message to the specified SNS topic when the CPU utilization exceeds a certain threshold.
4. Install the _boto3_ dependencies in the same folder as the python script and zip it all for _AWS Lambda_
5. Create the Lamda function, create a role, upload the zipped deployment package and update the handler field to "boto3 script".lambda_handler 
6. Update the Lamda function role to have read-only permissions for EC2 and CloudWatch (`DescribeInstances` and `GetMetricStatistics`) and `Publish` for SNS.
7. Create a new scheduled rule in event bridge, select Lambda as a target and the defined Lambda function
