import os
import json
import sys
import io
import os.path
import configparser
import subprocess

current_dir = os.getcwd()
home = os.path.expanduser("~")

if len(sys.argv) > 1:
    profile = sys.argv[1]
else:
    profile = "integration"


def get_credentials_from_aws_vault(profile):
    credentials = {}
    config_parser = configparser.ConfigParser()
    command_to_run = "aws-vault exec {} --prompt=terminal -- env | grep AWS > {}/.aws/temp_creds".format(profile, home)
    # with Capturing() as results:
    subprocess.run(command_to_run, shell=True, check=False, text=True)

    with open("{}/.aws/temp_creds".format(home), "r") as file:
        response = file.read()

    if not "AWS_SESSION_TOKEN" in response:
        print("An Error occurred while trying to retrieve credentials. Aborting")
        sys.exit()

    s_config = """
    [AWS]
    {}
    """.format(
        response
    )

    buf = io.StringIO(s_config)
    config = configparser.ConfigParser()
    config_parser.read_file(buf)

    credentials["AWS_SESSION_TOKEN"] = config_parser.get("AWS", "AWS_SESSION_TOKEN")
    credentials["AWS_ACCESS_KEY_ID"] = config_parser.get("AWS", "AWS_ACCESS_KEY_ID")
    credentials["AWS_SECRET_ACCESS_KEY"] = config_parser.get("AWS", "AWS_SECRET_ACCESS_KEY")

    return credentials


def create_default_aws_creds_file():
    f = open(f"{home}/.aws/credentials", "a")
    f.write("[default]")
    f.close()


def update_aws_credentials_file(home, credentials):
    config_parser = configparser.ConfigParser()
    if not os.path.isfile(f"{home}/.aws/credentials"):
        create_default_aws_creds_file()

    config_parser.read(f"{home}/.aws/credentials")

    config_parser["default"]["aws_access_key_id"] = credentials["AWS_ACCESS_KEY_ID"]
    config_parser["default"]["aws_secret_access_key"] = credentials["AWS_SECRET_ACCESS_KEY"]
    config_parser["default"]["aws_session_token"] = credentials["AWS_SESSION_TOKEN"]

    with open(f"{home}/.aws/credentials", "w") as configfile:
        config_parser.write(configfile)


credentials = get_credentials_from_aws_vault(profile)

update_aws_credentials_file(home, credentials)
print("Done updating aws credentials for {}".format(profile))
