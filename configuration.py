import os

VERSION = 0.1

#Bash command
#export DATABASE_URL="mysql://root:root@localhost:3306/referral"
DATABASE_URL = os.getenv("DATABASE_URL")


ENDPOINT_CALLBACK_CREDIT_ON_SIGNUP = os.getenv("ENDPOINT_BILLING_CREDIT","http://without.configured.url/%s")