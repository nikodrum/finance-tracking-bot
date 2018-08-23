from apiclient import discovery
import httplib2
from oauth2client import file, client, tools
import base64

from assets.config import APPLICATION_NAME, CLIENT_SECRET_FILE, SCOPES
from assets.loggers import logger


class GmailAPIWrapper(object):
    user_id = 'me'
    LABEL_INBOX = 'INBOX'
    LABEL_UNREAD = 'UNREAD'

    def __init__(self):

        store = file.Storage("./credentials/gg-token.json")
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = discovery.build(
            'gmail', 'v1', http=creds.authorize(httplib2.Http())
        )
        self.m_id = None

    def get_unread_message_list(self):
        try:
            return self.service.users() \
                .messages() \
                .list(
                userId=self.user_id,
                labelIds=[self.LABEL_INBOX,
                          self.LABEL_UNREAD]
            ).execute()['messages']
        except KeyError:
            pass

    def get_message_by_id(self, m_id):
        return self.service.users().messages() \
            .get(userId=self.user_id, id=m_id).execute()

    def get_message_from(self, email):

        mssg_list = self.get_unread_message_list()
        if not mssg_list:
            return None
        for mssg in mssg_list:

            m_id = mssg['id']
            message = self.get_message_by_id(m_id)
            payload = message['payload']
            headers = payload['headers']

            for item in headers:
                if item["name"] == "From":
                    if email in item["value"]:
                        return m_id

    def get_attachment(self, message, filename):
        file_data = None
        for part in message['payload']['parts']:
            if filename in part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = self.service.users().messages().attachments()\
                            .get(userId=self.user_id,
                                 messageId=self.m_id,
                                 id=att_id).execute()
                    data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
        return file_data.decode("utf-8")

    def get_mono_trs(self):
        self.m_id = self.get_message_from("info@monobank.com.ua")
        if self.m_id:
            message = self.get_message_by_id(self.m_id)
            trs = self.get_attachment(message, 'long.csv')
            if trs:
                self.service.users().messages() \
                    .modify(userId=self.user_id,
                            id=self.m_id,
                            body={'removeLabelIds': ['UNREAD']}
                            ).execute()
                return trs
            logger.info("File not found in message.")
            return None
        logger.info("Message not found")
