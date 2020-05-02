import imaplib
import email
from email.header import decode_header
from durango.search import KMPSearch
from durango.models import Task
#uncomment these when downloading attacments
#import webbrowser
#import os

# creating a 2-d list to store messages

def readmail(username, password):
    arr=[]
    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)

    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    
    # total number of emails
    messages = int(messages[0])
    if messages<15:
        N=messages
    else:
        N=15#checks top 15 mails matching with given keywords 
    keywords=['test','viva','scheduled','quiz','assignment','exam','meeting','task','homework','contest','round']
    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        #if current mail_id matcheswith some message_id already in the database
        for response in msg:
            if isinstance(response, tuple):
                flag=0
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                 #decode th message id
                m_id=decode_header(msg["MESSAGE-ID"])[0][0]
                # decode the email subject
                subject = decode_header(msg["Subject"])[0][0]
                #decode the date received
                date=decode_header(msg["Date"])[0][0]
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
                                arr.append(["From: "+ from_,"Received on:"+date,""+subject,""+b,m_id])
                                #print("="*100) 
       
    imap.close()
    imap.logout()
    return arr

