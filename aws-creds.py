import os
import json
import sys
import io
from datetime import datetime
import pyterprise
import configparser
import subprocess
from os import path

current_dir = os.getcwd() 
home = os.path.expanduser("~")
specific_profile = False

if (len(sys.argv) > 1):
    profile=sys.argv[1]
    specific_profile = True

def get_credentials_from_aws_vault(profile):
    credentials = {}
    config_parser = configparser.ConfigParser()
    command_to_run = "aws-vault exec {} --prompt=terminal -- env | grep AWS > {}/.aws/temp_creds".format(profile,home)
    #with Capturing() as results:
    subprocess.run(command_to_run, shell=True, check=False, text=True)
    
    with open('{}/.aws/temp_creds'.format(home), 'r') as file:
        response = file.read()
    
    if (not 'AWS_SESSION_TOKEN' in response):
        print("An Error occurred while trying to retrieve credentials. Aborting")
        sys.exit()

    s_config = """
    [AWS]
    {}
    """.format(response)

    buf = io.StringIO(s_config)
    config = configparser.ConfigParser()
    config_parser.read_file(buf)

    credentials["AWS_SESSION_TOKEN"] = config_parser.get('AWS', 'AWS_SESSION_TOKEN')
    credentials["AWS_ACCESS_KEY_ID"] =  config_parser.get('AWS', 'AWS_ACCESS_KEY_ID')
    credentials["AWS_SECRET_ACCESS_KEY"] = config_parser.get('AWS', 'AWS_SECRET_ACCESS_KEY')

    return credentials

def get_terraform_json_file():
    if (not os.path.exists(current_dir + "/.terraform/terraform.tfstate")):
        raise Exception("Could not find the terraform files, maybe run terraform init ???")

    with open('.terraform/terraform.tfstate') as json_file: 
        data = json.load(json_file) 

    return data

def get_terraform_org():
    data = get_terraform_json_file()

    return data['backend']['config']['organization']

def get_terraform_host():
    data = get_terraform_json_file()

    if data['backend']['config']['hostname'] != None:
        host = "https://" + data['backend']['config']['hostname']
    else:
        host = "https://app.terraform.io"

    return host

def get_terraform_environment():
    environment = ''
    data = get_terraform_json_file()
    
    try:
        if (path.exists(".terraform/environment")):
            with open('.terraform/environment') as f:
                environment =  f.read()
    except:
        pass

    return environment.strip()

def get_terraform_workspace():
    workspace = None

    data = get_terraform_json_file()
    environment = get_terraform_environment()
    prefix = None
    try:
        prefix = data["backend"]["config"]["workspaces"]["prefix"]
        if (prefix != None):
                workspace = prefix + environment
    except KeyError:
        pass

    if (prefix == None):
        try:
            workspace = data["backend"]["config"]["workspaces"]["name"]
        except KeyError:
            raise Exception("Could not figure out the workspace, try to run terraform init")

    return workspace.strip()

def get_terraform_token():
    terraform_token_file = home + "/.terraform.d/credentials.tfrc.json"
    if (not os.path.exists(terraform_token_file)):
        raise Exception("Could not find the terraform token file, you should probably run terraform login")

    with open(terraform_token_file) as json_file: 
        data = json.load(json_file)

    return data["credentials"]["app.terraform.io"]["token"]

def get_variables_by_key(variables):
    variables_by_key = {}
    for variable in variables:
        variables_by_key[variable.key] = variable

    return variables_by_key

def update_terraform_credentials(credentials, terraform_token, terraform_url, workspace_name):
    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    client = pyterprise.Client()
    client.init(token=terraform_token, url=terraform_url)
    tf_org = get_terraform_org()
    org = client.set_organization(id=tf_org)
    workspace = org.get_workspace(workspace_name)

    variables = get_variables_by_key(workspace.list_variables())

    variables['AWS_ACCESS_KEY_ID'].update(value=credentials['AWS_ACCESS_KEY_ID'], description="Updated by aws-creds on {}".format(dt_string))
    variables['AWS_SECRET_ACCESS_KEY'].update(value=credentials['AWS_SECRET_ACCESS_KEY'], description="Updated by aws-creds on {}".format(dt_string))
    variables['AWS_SESSION_TOKEN'].update(value=credentials['AWS_SESSION_TOKEN'], description="Updated by aws-creds on {}".format(dt_string))

def update_aws_credentials_file(home, credentials):
    config_parser = configparser.ConfigParser()
    config_parser.read('{}/.aws/credentials'.format(home))   
    
    config_parser['default']['aws_access_key_id'] =  credentials['AWS_ACCESS_KEY_ID']
    config_parser['default']['aws_secret_access_key'] = credentials['AWS_SECRET_ACCESS_KEY']
    config_parser['default']["aws_session_token"] = credentials['AWS_SESSION_TOKEN']

    with open('{}/.aws/credentials'.format(home), 'w') as configfile:
       config_parser.write(configfile)

if (not specific_profile):
    profile = get_terraform_environment()

credentials = get_credentials_from_aws_vault(profile)

if (not specific_profile):
    terraform_token = get_terraform_token()
    terraform_url = get_terraform_host()
    workspace_name = get_terraform_workspace()
    update_terraform_credentials(credentials, terraform_token, terraform_url, workspace_name)
    print("Done updating terraform credentials for {}".format(workspace_name))

update_aws_credentials_file(home, credentials)
print("Done updating aws credentials for {}".format(profile))


