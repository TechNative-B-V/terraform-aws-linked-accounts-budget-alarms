module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"
  version = "3.3.1"

  function_name = "linked_account_budget_alarms"
  description   = "check budgets and send alarms"
  handler       = "linked_account_budget_alarms.lambda_handler"
  runtime       = "python3.9"

  source_path = [
    format("%s/lambda-src", abspath(path.module)),
    {
      pip_requirements = format("%s/lambda-src/requirements.txt", abspath(path.module))
    }
  ]

  publish = true
  allowed_triggers = {
    PeriodicallyTriggerLambda = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.trigger_lambda.arn
    }
  }

  timeout = 15

  environment_variables = {
   LAMBDA_CONF = var.configured_accounts_json
   STS_MASTER_ACCOUNT_ROLE_ARN = var.sts_master_account_role_arn
   SLACK_WEBHOOK_URL = var.slack_webhook_url
   DEFAULT_THRESHOLD = var.default_threshold
  }

  attach_policy_json = true
  policy_json = data.aws_iam_policy_document.lambda_extra_permissions.json
}

data "aws_iam_policy_document" "lambda_extra_permissions" {
  statement {
    actions   = ["sts:AssumeRole"]
    resources = ["*"]
  }
}

resource "aws_cloudwatch_event_rule" "trigger_lambda" {
  schedule_expression = var.check_schedule
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule = aws_cloudwatch_event_rule.trigger_lambda.name
  arn  = module.lambda_function.lambda_function_arn
}

