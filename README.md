# Project  3: Fully Automated, Resilient, and Monitored Cloud Deployment
## Automate CPU usage monitoring on Python Flask App from Project-2

This project demonstrates a robust, production-ready cloud architecture leveraging Infrastructure-as-Code (IaC) for deployment and a serverless pipeline for automated resource monitoring and alerting. It merges a containerized application deployment (Project 2) with a serverless monitoring system to create a resilient, observable solution.

-----

## 💡 The Problem: Deploy & Defend

### Requirement

A reliable, cost-effective and proactive alerting system for the core application infrastructure, specifically the "FlaskAppServer" EC2 instance. Standard CloudWatch alarms lacked the flexibility to combine complex logic (like dynamic resource lookup and custom notification formatting) into a single, scheduled check.

The core challenge :

  **Proactive Observability:** The deployed application needs to be continuously monitored. If the **AWS EC2** host experiences high load (e.g., **CPU Utilization** exceeds a critical threshold), the operations team must be **immediately notified** to prevent performance degradation.

This solution provides a complete **DevOps pipeline** for deployment and a crucial layer of **proactive monitoring**.

-----

## 🏗️ The Architecture: Infrastructure and Alerting

The architecture is split into two tightly integrated systems: the **Deployment Stack** (managed by Terraform) and the **Monitoring Pipeline** (managed by AWS Serverless services).

### **Architecture Diagram**

### **1. Deployment Stack**

| Tool/Service | Purpose | Details |
| :--- | :--- | :--- |
| **Terraform** (IaC) | Infrastructure Provisioning | Manages the creation of the EC2 instance, the Security Group (`web_sg`), and outputs the public IP. |
| **AWS EC2** | Compute Host | The virtual server (using Ubuntu 24.04 LTS) running the application. |
| **AWS Security Group** | Network Security | Allows inbound **SSH (Port 22)** and **HTTP (Port 80)** traffic from the internet (`0.0.0.0/0`). |
| **Docker** | Containerization | Packages the Flask app into an immutable container, ensuring consistent deployment. |
| **Linux `user_data` Script** | Bootstrapping | Automatically installs **Docker** and **Git**, clones the GitHub repository (`https://github.com/LuciusScipio/Project-2.git`), builds the Docker image, and runs the container, mapping container port **5000** to host port **80**. |

### **2. Monitoring Pipeline Idea**

| Tool/Service | Purpose | Details |
| :--- | :--- | :--- |
| **AWS CloudWatch** | Metrics Source | Collects the **`CPUUtilization`** metric for the EC2 instance named `FlaskAppServer`. Source of truth for all resource metrics and dashboard visualization. |
| **AWS EventBridge** | Scheduler | Triggers the Lambda function on a **scheduled rule** (e.g., every 5 minutes). |
| **AWS Lambda** | Serverless Compute | Executes the Python monitoring script periodically. |
| **Python** (`boto3`) | Logic Layer, Dynamic Instance Lookup and ClodWatch Metric retrieval | The script finds the EC2 instance ID by its tag, fetches the latest CPU metric, and checks if it is above the **50.0%** threshold. |
| **AWS SNS** | Notification Service | Publishes a critical **ALERT** message when the CPU threshold is exceeded. Subscribed to by an email address for real-time alerts. |

-----


## 🛠️ Monitoring Pipeline Flowchart 
This section details the operational flow of both the **Monitoring Pipeline**, illustrating how its health is continuously observed.

This serverless flow ensures the application host is continuously monitored for performance bottlenecks.

1.  **Scheduler Trigger:** **AWS EventBridge** rule triggers on a defined schedule (e.g., every 5 minutes).
2.  **Lambda Function Invocation:** The **AWS Lambda** function starts execution.
3.  **Script Execution (Python/Boto3):** The `get_cpu_utilization.py` script runs:
    * Uses **Boto3 EC2 Client** to find the instance ID for `FlaskAppServer`.
    * Uses **Boto3 CloudWatch Client** to retrieve the latest `CPUUtilization` metric for that instance ID.
4.  **Threshold Check:** The script checks if `Average CPU Utilization > 50.0%`.
5.  **Alerting Logic:**
    * **IF NO (Below Threshold):** The script prints a status message and exits.
    * **IF YES (Exceeds Threshold):** The script uses the **Boto3 SNS Client** to publish a critical alert message.
6.  **Notification Delivery:** The **SNS Topic** sends the alert message to all subscribed endpoints, resulting in an immediate **Email Notification** to the operations team.

-----

## 🧗 Challenges Overcame

Implementing this project required overcoming several common DevOps and CloudOps hurdles, demonstrating strong troubleshooting and debugging skills.

| Challenge | Root Cause | Solution/Fix |
| :--- | :--- | :--- |
| **Serverless Permissions** | The Lambda function, by default, lacks permissions to interact with other AWS services. | Updated the Lambda execution role to include `ec2:DescribeInstances`, `cloudwatch:GetMetricStatistics`, and `sns:Publish` permissions. |
|**Dynamic Resource Identification (EC2)**| The Lambda script could not rely on a hardcoded EC2 Instance ID, as the instance might be replaced or auto-scaled| Implemented a dynamic lookup function using boto3.client('ec2').describe_instances with a tag filter. This ensures the monitoring system is decoupled from the underlying infrastructure's lifecycle.|**Lambda Deployment Packaging**| Ensuring the Lambda execution environment had the necessary Python dependencies for the script to run outside of the local environment.|Used the proper Lambda deployment workflow, bundling the Python script and all required dependencies (including Boto3) into a single, versioned deployment package.

-----

## 📈 Key Metrics & Achievements

  * **Proactive Alerting:** Implemented a system that can detect and report a sustained spike in EC2 **CPU Utilization above 50%** within a **5-minute window**, minimizing the time-to-detection (MTTD) for performance issues.
  * **Reduced Human Error:** The entire infrastructure and initial deployment are provisioned with a single `terraform apply` command, eliminating manual steps and ensuring environment consistency.
  * **Cost-Effectiveness:** Leveraged **AWS Lambda** and **EventBridge** for monitoring, incurring compute costs only when the monitoring script runs, which is significantly more cost-effective than running a dedicated, always-on server for monitoring.

-----

## 📖 Deployment Instructions





### **Phase 1: Preparation and Local Scripting**

1.  **Monitor EC2 Usage:** Set up a **CloudWatch Dashboard** to visually monitor the EC2 Instance's CPU usage.
2.  **Set Up Notification:** Create an **SNS topic** and configure a subscription using the **email** protocol to receive alerts.
3.  **Develop Python Script:** Write a Python script (e.g. `get_cpu_utilization.py`or just use the one uploaded) that uses the **`boto3`** library. It is responsible for fetching the metric, applying the logic, and sending the alert. Ensure:
    * It  uses the **EC2 client**'s `describe_instances` method to find the EC2 instance ID.
    * It uses the **CloudWatch client**'s `get_metric_statistics` method to programmatically fetch CPU utilization data for the EC2 instance.
    * It publishes a message to the specified **SNS topic** when the CPU utilization exceeds a certain threshold.

**Note:** Ensure to update the constants in get_cpu_utilization.py with your environment details:

a. **Target EC2 instance tag name**<br>
instance_name<br>
b. **The ARN**<br>
sns_topic_arn<br>
c. **Alert threshold**<br>
cpu_threshold

4.  **Package for Lambda:** Install the necessary **`boto3` dependencies** in the same folder as your Python script and **zip** the entire package for deployment to **AWS Lambda**.

---

### **Phase 2: AWS Lambda Setup**

1.  **Create Lambda Function and Role:**
    * Create the **Lambda function** itself.
    * Create an appropriate **IAM Role** for the function.
    * Upload the zipped deployment package to the function.
    * Update the handler field to the correct function entry point, for example: `"boto3 script".lambda_handler`.
2.  **Configure IAM Permissions:** Update the Lambda function's IAM role to grant the necessary minimum permissions:
    * **EC2:** Read-only permission (`DescribeInstances`).
    * **CloudWatch:** Read-only permission (`GetMetricStatistics`).
    * **SNS:** Permission to send messages (`Publish`).

---

### **Phase 3: Scheduling the Monitoring Job**

1.  **Create EventBridge Rule:** Create a new **scheduled rule** in **EventBridge** (formerly CloudWatch Events).
2.  **Set Target:** Select **Lambda** as the target for the rule and specify the defined Lambda function.

The Lambda function will now execute periodically according to the schedule, checking the EC2 CPU usage and publishing alerts to your SNS topic as configured.

### **Phase 3: Cleanup (if needed)**

To destroy all provisioned AWS resources and avoid charges:

```bash
terraform destroy --auto-approve
```

-----

## 🗂️ Troubleshooting: Debugging a Failed Deployment

| Problem Faced | Log/Symptom | How I Fixed It |
| :--- | :--- | :--- |
| **CloudWatch Log Access** | No monitoring alerts are received. | **Checked Lambda Logs** (in CloudWatch Logs) to debug the Python script. Discovered the Lambda IAM role was missing the **`sns:Publish`** permission, which was added to enable notifications. |





## 🐞 Troubleshooting a Failed Alert

If the monitoring system fails to send an email alert when the CPU threshold is exceeded, the first step is always to check the central logging system: CloudWatch Logs.

|Troubleshooting Step| Action in CloudWatch Logs| Diagnostic Outcome|
|--|--|--|
| **Step 1: Check Execution** | Navigate to Lambda → Monitor tab → CloudWatch Logs. Check the latest Log Stream for the EventBridge trigger time.|If no log stream exists: The EventBridge rule is misconfigured or disabled.
|**Step 2: Check Dynamic Lookup**|Review the logs for the message: `"Found instance ID: i-..."` |If instance ID is not found: The ec2:DescribeInstances Boto3 call failed, likely due to a wrong tag value or a missing ec2:DescribeInstances IAM permission.
|**Step 3: Check Alert Logic** | Look for the print statement indicating the calculated CPU usage **(e.g., "Average CPU Utilization: 85.34%")**.|If the usage is high but no SNS publish attempt is seen: The CPU threshold logic in the Python script may have an issue.
| **Step 4: Check SNS Publish** | Look for any error messages containing `"AccessDenied"` or `"SNS"`.|If an Access Denied error is present: The Lambda's IAM role is missing the `sns:Publish permission`. This is the most common cause of failed alerts.

CloudWatch Logs help to quickly pinpoint failures in the execution flow, the metric retrieval or the necessary permissions.
