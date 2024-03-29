# AWS Credential script

Install aws-vault (`brew install --cask aws-vault`)

Install aws cli

```
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

The purpose of this script is to populate temporary credentials when using aws-vault (https://github.com/99designs/aws-vault).

The script uses aws-vault to generate temporary aws credentials, and add them to the `~/.aws/credentials` file.

Copy the binary file to your `/usr/local/bin` folder, or any other folder in your path.

Use: `aws-creds [AWS profile]`

You can download an x86 or an arm binary from the releases area.

If you need to compile it locally, use the instructions below.

# Compile from sracth install python 3.7.9 (did not work with 3.8)

ON Linux

`CONFIGURE_OPTS=--enable-shared pyenv install 3.7.9`

ON MAC

Update xcode tools to the latest version

```
softwareupdate -ia
```

```
env PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.7.9
pyenv global 3.7.9
pip install pipenv==2022.5.2
```


# Trigger initialization script and compile

It creates the virtual environment if it does not exist (I was using pipenv)
installe the required modules, triggers the compile, and
copy the executable to the /usr/local/bin folder.

`./compile.sh`
