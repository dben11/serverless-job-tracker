# 1. DynamoDB Table
resource "aws_dynamodb_table" "job_tracker_table" {
  name           = "JobTracker"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "JobID"

  attribute {
    name = "JobID"
    type = "S"
  }
}

# 2. Zip the Python Code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

# 3. Lambda Function
resource "aws_lambda_function" "job_tracker_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "JobScraperFunction"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      ALERT_EMAIL = var.alert_email
    }
  }
}

# 4. EventBridge Rule (The Alarm Clock)
resource "aws_cloudwatch_event_rule" "hourly_trigger" {
  name                = "HourlyJobCheck"
  description         = "Triggers the job scraper every hour"
  schedule_expression = "rate(1 hour)"
}

# 5. EventBridge Target (Connects Rule to Lambda)
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.hourly_trigger.name
  target_id = "JobTrackerLambda"
  arn       = aws_lambda_function.job_tracker_lambda.arn
}

# 6. Lambda Permission (Allows EventBridge to trigger Lambda)
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.job_tracker_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.hourly_trigger.arn
}
