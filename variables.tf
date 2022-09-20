variable "check_schedule" {
  type    = string
  default = "rate(1 day)"
  description = <<EOS
Schedule expression that defines when and/or how often the budgets should be checked.

See https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html for valid schedule expressions.
EOS
}

variable "sts_master_account_role_arn" {
  type    = string
  description = <<EOS
STS Master Account Role ARN to the master account Cost Explorer Service.

When you run this function from another account then the master organization
account this role gives the querying account access.

EOS
  default = ""
}

variable "slack_webhook_url" {
  type  = string
  description = "Slack webhook url to channel which receives the notifications"
}

variable "default_threshold" {
  type  = number
  description = "When an account has no own threshold configuration this default threshold triggers an alarm."
}

variable "configured_accounts_json" {
  type = string
  default = <<EOS
{ "configured_accounts": {} }
EOS

  description = <<EOS
JSON string which configures account to have their own threshold cost amount.

example:
{
  "configured_accounts": {
    "000000000013": {
      "threshold_amount": 250
    }
  }
}

EOS

}
