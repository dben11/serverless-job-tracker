variable "aws_region" {
  description = "The AWS region to deploy into"
  type        = string
  default     = "us-east-1" # Change if you used a different region
}

variable "alert_email" {
  description = "The email address to receive job alerts (must be verified in SES)"
  type        = string
}
