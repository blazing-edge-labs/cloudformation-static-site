#!/usr/bin/env python

# Creates or updates cloudformation stack


import argparse
import yaml
import boto
import boto.s3
import boto.cloudformation
from templates import static_site as template


def get_deploy_config():
    text = open("config/config.yml", 'r')
    return yaml.load(text)


def cfn_connect(region_name):
    return boto.cloudformation.connect_to_region(region_name)


def cfn_update(cfn_conn, stack_name, template_body, parameters):
    # only valid capability
    capabilities = ["CAPABILITY_IAM"]

    cfn_conn.update_stack(stack_name, template_body=template_body,
                          capabilities=capabilities, parameters=parameters)


def cfn_create(cfn_conn, stack_name, template_body, parameters):
    # only valid capability
    capabilities = ["CAPABILITY_IAM"]

    cfn_conn.create_stack(stack_name, template_body=template_body,
                          capabilities=capabilities, parameters=parameters)


def get_parameters():
    text = open("config/params.yml", 'r')
    params = yaml.load(text)

    return params.items()


def update(config, params):
    cfn_conn = cfn_connect(config['region_name'])
    cfn_update(cfn_conn, config['stack_name'], template.get(), params)

    print "Updating stack: {0}".format(config['stack_name'])


def create(config, params):
    cfn_conn = cfn_connect(config['region_name'])
    cfn_create(cfn_conn, config['stack_name'], template.get(), params)

    print "Creating stack: {0}".format(config['stack_name'])


def parse_args():
    parser = argparse.ArgumentParser(
        description='Creates or updates a Cloudformation stack')
    parser.add_argument('-c', '--create', action='store_true')
    return parser.parse_args()


def main(args=None):
    args = parse_args()
    config = get_deploy_config()
    params = get_parameters()

    # in case create flag is active do create, update is default action
    if args.create:
        return create(config, params)

    update(config, params)


if __name__ == "__main__":
    main()
