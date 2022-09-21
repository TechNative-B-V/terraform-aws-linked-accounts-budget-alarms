module "linked-accounts-budget-alarms" {
  source  = "TechNative-B-V/linked-accounts-budget-alarms/aws"
  version = "0.1.0"

  sts_master_account_role_arn = "arn:aws:iam::XXXXXXXXXXXX:role/MonitoringCostExplorer"
  slack_webhook_url = "https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
  default_threshold = 200
  configured_accounts_json = file("./budget-alarms-conf.json")
}

