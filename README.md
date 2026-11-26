# Serverless Job Tracker (AWS + Terraform)

##  Overview
An automated, event-driven serverless application deployed via Terraform. This project solves the problem of manually searching for entry-level cloud roles by fetching jobs from a third-party API, filtering for relevant keywords, preventing duplicate alerts, and delivering formatted emails directly to the user's inbox.

##  Architecture
The infrastructure is fully provisioned using **Terraform (IaC)**.
*   **Amazon EventBridge:** Acts as a scheduled trigger, invoking the Lambda function every hour.
*   **AWS Lambda (Python 3.12):** Fetches data from the Remotive API, applies keyword filters, and manages the email logic.
*   **Amazon DynamoDB:** Acts as a state-management layer, storing seen Job IDs to prevent duplicate email notifications.
*   **Amazon SES (Simple Email Service):** Sends the formatted email alerts to the verified user.
*   **AWS IAM:** Manages the least-privilege roles and permissions for the Lambda function.

##  Challenges Solved (The Engineering Journey)
*   **API 403 Forbidden Error:** Resolved by adding a custom `User-Agent` header to the Python `urllib` request to bypass bot-blocking on the Remotive API.
*   **Silent Failures (No Email):** Discovered that the system was working correctly but had strict keyword filters. Implemented a `debug_messages` array to output the filter logic directly to the Lambda response for easier troubleshooting.
*   **Terraform Archive Error:** Fixed pathing issues by organizing the Python source code into a `src/` directory relative to the Terraform module.

##  How to Deploy
1. Ensure you have AWS CLI and Terraform installed.
2. Verify your email address in the Amazon SES Console (in your desired region).
3. Navigate to the `terraform/` directory.
4. Initialize Terraform: `terraform init`
5. Apply the infrastructure, passing your email as a variable: 
   `terraform apply -var="alert_email=your-email@example.com"`
6. Type `yes` when prompted.

##  Teardown
To avoid unnecessary AWS charges, destroy the infrastructure when finished:
`terraform destroy -var="alert_email=your-email@example.com"`

