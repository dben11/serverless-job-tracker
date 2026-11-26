import json
import boto3
import urllib.request
import os

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
ses = boto3.client('ses', region_name='us-east-1')
table = dynamodb.Table('JobTracker')

def lambda_handler(event, context):
    ALERT_EMAIL = os.environ.get('ALERT_EMAIL')
    debug_messages = []

    if not ALERT_EMAIL:
        return {'statusCode': 500, 'body': 'Missing ALERT_EMAIL'}

    debug_messages.append(f"Using email: {ALERT_EMAIL}")

    url = "https://remotive.com/api/remote-jobs?category=software-dev"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return {'statusCode': 500, 'body': f'API Error: {e}'}

    api_jobs = data.get("jobs", [])
    debug_messages.append(f"Fetched {len(api_jobs)} total jobs from API.")
    
    # 1. Define the keywords HERE, before we use them
    keywords = ["entry", "junior", "jr", "cloud", "devops", "aws", "associate"]
    
    # 2. Now we can safely count them
    matching_jobs_count = sum(1 for job in api_jobs if any(k in job["title"].lower() for k in keywords))
    debug_messages.append(f"Found {matching_jobs_count} jobs matching your keywords.")
    
    jobs_to_email = []
    
    # 3. Loop through and filter
    for job in api_jobs:
        job_title = job["title"].lower()
        
        if any(keyword in job_title for keyword in keywords):
            job_id = str(job["id"])
            original_title = job["title"]
            company = job["company_name"]
            
            response = table.get_item(Key={'JobID': job_id})
            
            if 'Item' not in response:
                jobs_to_email.append({"title": original_title, "company": company})
                table.put_item(Item={'JobID': job_id, 'Title': original_title})
                debug_messages.append(f"Found new job to email: {original_title}")
            else:
                debug_messages.append(f"Skipped (already in DB): {original_title}")

    # 4. Send email if there are new matches
    if jobs_to_email:
        email_body = "Here are your new entry-level cloud jobs:\n\n"
        for job in jobs_to_email:
            email_body += f"- {job['title']} at {job['company']}\n"
            
        try:
            ses.send_email(
                Source=ALERT_EMAIL,
                Destination={'ToAddresses': [ALERT_EMAIL]},
                Message={
                    'Subject': {'Data': 'New Entry-Level Cloud Jobs Found!'},
                    'Body': {'Text': {'Data': email_body}}
                }
            )
            debug_messages.append("SUCCESS: Email sent via SES.")
        except Exception as e:
            debug_messages.append(f"SES ERROR: {e}")
    else:
        debug_messages.append("No NEW matching jobs found. Email not sent.")

    # Return the debug messages to your screen
    return {
        'statusCode': 200,
        'body': json.dumps(debug_messages)
    }
