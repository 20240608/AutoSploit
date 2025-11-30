#!/bin/bash

# Create Docker environment marker
touch /.dockerenv

# Start Apache
/etc/init.d/apache2 start

# Run AutoSploit
cd /AutoSploit
python3 autosploit.py