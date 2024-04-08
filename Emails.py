from email.message import EmailMessage
import ssl
import smtplib
import email
import imaplib

EMAIL = "peterfishmaniot@outlook.com";
PASSWORD = "getreqed6000";
SERVER = 'smtp.office365.com'

def sendEmail(email_receiver, subject ,body):
    #variable with email sender
    email_sender = "peterfishmaniot@outlook.com";
    email_password = "getreqed6000";

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    #Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.office365.com', 587, context=context) as smtp:
        #login into the sender email
        smtp.login(email_sender, email_password)
        #send the email
        smtp.sendmail(email_sender, email_receiver, em.as_string())

def receiveEmail(senderEmail):
    # connect to the server and go to its inbox
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)
    # we choose the inbox but you can select others
    mail.select('inbox')

    # ALL  criteria =  retrieve every message inside the inbox
    # return with its status and a list of ids
    status, data = mail.search(None,
    'UNSEEN',
    'HEADER SUBJECT "Change Temperature Sugguestion"',
    'HEADER FROM "' + senderEmail +  '"')

    mail_ids = []
    for block in data:
        # the split function called without parameter
        # transforms the text or bytes into a list using
        # as separator the white spaces:
        # b'1 2 3'.split() => [b'1', b'2', b'3']
        mail_ids += block.split()

    # now for every id we'll fetch the email
    # to extract its content
    for i in mail_ids:
        # the fetch function fetch the email given its id
        # and format that you want the message to be
        status, data = mail.fetch(i, '(RFC822)')

        # the content data at the '(RFC822)' format comes on
        # a list with a tuple with header, content, and the closing
        # byte b')'
        for response_part in data:
            if isinstance(response_part, tuple):
                # we go for the content at its second element
                # skipping the header at the first and the closing
                # at the third
                message = email.message_from_bytes(response_part[1])
                mail_from = message['from']
                mail_subject = message['subject']

                # then for the text we have a little more work to do
                # because it can be in plain text or multipart
                # if its not plain text we need to separate the message
                # from its annexes to get the text
                if message.is_multipart():
                    mail_content = ''
                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    mail_content = message.get_payload()

                return "yes" in mail_content.lower();