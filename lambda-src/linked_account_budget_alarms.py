#!/usr/bin/env python3

# Unless explicitly stated otherwise all files in this repository are licensed
# under the Apache License Version 2.0.
# This product includes software developed at TechNative (https://www.technative.nl/).
# Copyright 2022 TechNative B.V.

import json
import boto3
import datetime
import json
import logging
import os
import sys
import pprint
import requests

pp = pprint.PrettyPrinter(indent=4)
lambda_conf = {}
sts_master_account_role_arn = ''

def init_conf():
    global lambda_conf
    global sts_master_account_role_arn
    global default_threshold
    global slack_webhook_url

    slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    lambda_conf = json.loads(os.environ.get('LAMBDA_CONF'))
    sts_master_account_role_arn = os.environ.get('STS_MASTER_ACCOUNT_ROLE_ARN')
    default_threshold = os.environ.get('DEFAULT_THRESHOLD')

def send_alarms(account_conf, title, message):
    send_slack_message(title, message, slack_webhook_url)

def send_slack_message(title, message, webhook_url):
    url = webhook_url
    title = (f":warning: "+title)
    slack_data = {
        "username": "NotificationBot",
        "icon_emoji": ":satellite:",
        "attachments": [
            {
                "color": "#FF0000",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

def one_day_period():
    now = datetime.datetime.utcnow()
    start = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')

    return {'Start': start, 'End': end}

def account_conf(accountnr):
    if accountnr in lambda_conf["configured_accounts"]:
        account_conf = lambda_conf["configured_accounts"][accountnr]
    else:
        account_conf = { "threshold_amount": default_threshold }

    return account_conf

def account_cost_exceed(account):
    conf = account_conf(account['id'])

    if(float(account['total_cost']) > float(conf['threshold_amount'])):
        return True

def assume_role_service_client(role_arn, service_id):
    sts = boto3.client('sts')
    session_name = 'Session-' + service_id
    assumed_role_object = sts.assume_role ( RoleArn=role_arn, RoleSessionName=session_name)
    credentials=assumed_role_object['Credentials']
    return boto3.client(
            service_id,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
            )

def exceeded_accounts_list():

    ce_client = assume_role_service_client(sts_master_account_role_arn, 'ce');
    ce = boto3.client('ce')
    cost = ce_client.get_cost_and_usage(
            TimePeriod = one_day_period(),
            Granularity = 'DAILY',
            GroupBy = [{"Type": "DIMENSION","Key": "LINKED_ACCOUNT"}],
            Metrics=['UnblendedCost'])

    account_dict = {}
    for account_info in cost['DimensionValueAttributes']:
        account_dict[account_info['Value']] = {
                "id" : account_info['Value'],
                "name" : account_info['Attributes']['description']
                }

    accounts_exceeded = []
    for account_cost in cost['ResultsByTime'][0]['Groups']:

        account_dict[account_cost['Keys'][0]]['total_cost'] = float(account_cost['Metrics']['UnblendedCost']['Amount'])

        if account_cost_exceed(account_dict[account_cost['Keys'][0]]):
            account_dict[account_cost['Keys'][0]]['conf'] = account_conf(account_dict[account_cost['Keys'][0]]['id'])
            accounts_exceeded.append(account_dict[account_cost['Keys'][0]])

    return accounts_exceeded

def send_alarms_for_exceeded_accounts():
    accounts_exceeded = exceeded_accounts_list()
    period = one_day_period()

    for account in accounts_exceeded:
        send_alarms(account['conf'],
                "WARNING COSTS TO HIGH 📈 : " + account['name'] + " ("+account['id']+")",
                "The costs are to high of account " + account['id'] + "\n"
                "Threshhold: $ "+ str("{:.2f}".format(float(account['conf']['threshold_amount']))) + "\n"
                "Total costs: $ "+ str(round(account['total_cost'],2)) + "\n"
                "Period: "+ period['Start'] + " > " + period['End'] + " (24h)\n"
                )

def lambda_handler(event, lambda_context):

    init_conf()
    send_alarms_for_exceeded_accounts();

    return json.dumps(True)

## THIS BLOCK IS TOO RUN LAMBDA LOCALLY
if __name__ == '__main__':

    with open(os.path.dirname(os.path.abspath(__file__))+'/../budget-alarms-conf.json', 'r') as f:
        contents = f.read()
        os.environ["LAMBDA_CONF"] = contents

    lambda_handler({}, {})
