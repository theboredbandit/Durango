import imaplib
import email
from email.header import decode_header
#uncomment these when downloading attacments
from durango.search import KMPSearch
#import webbrowser
#import os

# creating a 2-d list to store messages
arr=[[]]
def readmail(username, password):

    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)

    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    N = 20
    # total number of emails
    messages = int(messages[0])
    keywords=['test','viva','scheduled','quiz','assignment','exam','meeting','task','homework','contest']

    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        message_id=imap.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
        hp = HeaderParser()
        header_string = message_id[0][1]
        header = hp.parsestr(header_string)
        m_id= parseaddr(header['message-id'])[1]
        for response in msg:
            if isinstance(response, tuple):
                flag=0
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode()
                # email sender
                from_ = msg.get("From")
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            b=body
                            for item in keywords:
                                if KMPSearch(item,subject):
                            	    flag=1
                            	    break
                            if flag==0:
                                for item in keywords:
                                    if KMPSearch(item,b):
                                        flag=1
                                        break
                            if flag==1:
                                arr.append(["From: "+ from_,"Subject: "+subject,"Mail Body:"+b,m_id])
                                #print("="*100)
       
    imap.close()
    imap.logout()
    return arr

