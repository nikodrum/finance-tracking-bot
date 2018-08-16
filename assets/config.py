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
