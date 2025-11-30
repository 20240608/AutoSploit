#!/bin/bash

# Create Docker environment marker file
touch /.dockerenv

# Start Apache (still needed for AutoSploit)
/etc/init.d/apache2 start

# Note: PostgreSQL is not started locally because we use external msfdb container
# configured via POSTGRES_HOST environment variable

cd /AutoSploit

python3 autosploit.py
