#!/bin/bash

echo "Generating executable"
pyinstaller --onefile --clean aws-creds.py 
sudo mv dist/aws-creds /usr/local/bin
echo "Moved aws-creds to /usr/local/bin"
