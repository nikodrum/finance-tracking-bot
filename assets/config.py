import os

WEBHOOK_HOST = os.environ['HOST']
WEBHOOK_PORT = 80
WEBHOOK_LISTEN = os.environ['HOST']

WEBHOOK_SSL_CERT = './webhook/webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook/webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (os.environ['BOT_TOKEN'])

DATA_SCHEMA_CLEAN = ['category', 'subcategory', 'trandate', 'trantime', 'amount',
                     'amount_currency', 'cardamount', 'store']
DATA_SCHEMA = ["@card", "@appcode", "@trandate",
               "@trantime", "@amount", "@cardamount",
               "@rest", "@terminal", "@description"]

PRIVAT_API = "https://api.privatbank.ua/p24api/rest_fiz"
# PRIVAT_API = "http://localhost:5010/api/example"

SERVER_API = "http://localhost:5005"

CLIENT_SECRET_FILE = './credentials/google.json'
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
APPLICATION_NAME = "finance-tracking-system"
