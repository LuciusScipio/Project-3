import boto3
from datetime import datetime, timedelta

def get_ec2_instance_id_by_tag(tag_name, tag_value, region):
    """
    Retrieves the instance ID of an EC2 instance by its tag name and value.
    """
    try:
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': f'tag:{tag_name}',
                    'Values': [tag_value]
                },
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        )

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                return instance['InstanceId']

    except Exception as e:
        print(f"Error retrieving instance ID: {e}")
        return None

def get_cpu_utilization(instance_id, region):
    """
    Retrieves the average CPU utilization for a given EC2 instance.

    """
    if not instance_id:
        print("Instance ID not provided. Exiting.")
        return None

    try:
        cloudwatch = boto3.client('cloudwatch', region_name=region)
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            StartTime=datetime.utcnow() - timedelta(minutes=5),
            EndTime=datetime.utcnow(),
            Period=300,  # 5 minutes in seconds
            Statistics=['Average']
        )

        if not response['Datapoints']:
            print("No data points found for CPU utilization.")
            return None

        # Sort the data points by timestamp and get the most recent one
        last_datapoint = sorted(response['Datapoints'], key=lambda x: x['Timestamp'], reverse=True)[0]
        return last_datapoint['Average']

    except Exception as e:
        print(f"Error retrieving CloudWatch metric: {e}")
        return None

def publish_to_sns(topic_arn, message, region):
    """
    Publishes a message to a given SNS topic.
    """
    try:
        sns_client = boto3.client('sns', region_name=region)
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message
        )
        print(f"Published message to SNS topic: {response['MessageId']}")
    except Exception as e:
        print(f"Error publishing to SNS: {e}")

if __name__ == '__main__':
    # Need to configure your AWS credentials and region.
    
    
    
    aws_region = 'us-east-1'
    
    instance_name = 'FlaskAppServer'
    sns_topic_arn = 'arn:aws:sns:us-east-1:858257512397:High-Flask-App-usage:ba636d1e-b4fb-47b4-adc3-afa3a245c92b'
    cpu_threshold = 50.0 # Set the CPU threshold (in percent)

    print(f"Finding instance ID for '{instance_name}' in region '{aws_region}'...")
    ec2_instance_id = get_ec2_instance_id_by_tag('Name', instance_name, aws_region)

    if ec2_instance_id:
        print(f"Found instance ID: {ec2_instance_id}")
        
        print("\nRetrieving CPU utilization for the last 5 minutes...")
        cpu_usage = get_cpu_utilization(ec2_instance_id, aws_region)
        
        if cpu_usage is not None:
            print(f"Average CPU Utilization: {cpu_usage:.2f}%")
            
            # Check if CPU utilization exceeds the threshold
            if cpu_usage > cpu_threshold:
                message = f"ALERT: CPU utilization for instance {instance_name} ({ec2_instance_id}) has exceeded the threshold of {cpu_threshold:.2f}% with a value of {cpu_usage:.2f}%."
                print("--- Threshold exceeded. Publishing message to SNS. ---")
                publish_to_sns(sns_topic_arn, message, aws_region)
            else:
                print(f"CPU utilization is below the threshold of {cpu_threshold:.2f}%. No action taken.")
    else:
        print(f"Could not find an EC2 instance with the name '{instance_name}'.")
