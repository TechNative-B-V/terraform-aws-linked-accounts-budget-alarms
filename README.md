# Terraform AWS Linked Accounts Budget Alarms ![](https://img.shields.io/github/workflow/status/TechNative-B-V/terraform-aws-linked-accounts-budget-alarms/Lint?style=plastic)

<!-- SHIELDS -->

This module implements an automatic check if member accounts of an AWS
organization exceed their spent cost limits. When an account threshold is
reached a notification is sent to a slack channel.

[![](we-are-technative.png)](https://www.technative.nl)
[Hire us](https://www.technative.nl/services/) | [Kom bij ons werken](https://www.technative.nl/technative/#workingat)

## Why not AWS own budget module?

[AWS Budgets Service](https://aws.amazon.com/aws-cost-management/aws-budgets/)
must be pre configured for every account. You can not set a standard for new
accounts. This module checks every account, including new not yet provisioned
accounts with a default threshold.

## How does it work

Every day a lambda script runs the cost explorer and compares the total costs
of each linked account with the configured budget. If costs exceed a slack
notification is sent using a [webhook](https://api.slack.com/messaging/webhooks).

![](slacknot.png)

## Usage

[example](examples/using-sts)

### STS Access Role

You need a role with the querying account defined as trustee and a policy
allowing ListAccess to the Cost Explorer is must be created on the master
account. The ARN of this role should be configured in
`sts_master_account_role_arn.

### Json Budget Configuration

Every account can have it's own budget in dollars. It's defined in json.

```
{
  "configured_accounts": {
    "000000000011": {
      "threshold_amount": 2.5
    }
    "000000000012": {
      "threshold_amount": 50
    }
    "000000000013": {
      "threshold_amount": 2500
    }
  }
}
```

<!-- BEGIN_TF_DOCS -->
## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_lambda_function"></a> [lambda\_function](#module\_lambda\_function) | terraform-aws-modules/lambda/aws | 3.3.1 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.trigger_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.lambda_target](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_iam_policy_document.lambda_extra_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_check_schedule"></a> [check\_schedule](#input\_check\_schedule) | Schedule expression that defines when and/or how often the budgets should be checked.<br><br>See https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html for valid schedule expressions. | `string` | `"rate(1 day)"` | no |
| <a name="input_configured_accounts_json"></a> [configured\_accounts\_json](#input\_configured\_accounts\_json) | JSON string which configures account to have their own threshold cost amount. | `string` | `"{ \"configured_accounts\": {} }\n"` | no |
| <a name="input_default_threshold"></a> [default\_threshold](#input\_default\_threshold) | When an account has no own threshold configuration this default threshold triggers an alarm. | `number` | n/a | yes |
| <a name="input_slack_webhook_url"></a> [slack\_webhook\_url](#input\_slack\_webhook\_url) | Slack webhook url to channel which receives the notifications | `string` | n/a | yes |
| <a name="input_sts_master_account_role_arn"></a> [sts\_master\_account\_role\_arn](#input\_sts\_master\_account\_role\_arn) | STS Master Account Role ARN to the master account Cost Explorer Service.<br><br>When you run this function from another account then the master organization<br>account this role gives the querying account access. | `string` | `""` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
