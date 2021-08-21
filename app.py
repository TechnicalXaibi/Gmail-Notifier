from flask import Flask, request
import os
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import time
import threading

app = Flask(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
#SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


"""Shows basic usage of the Gmail API.
Lists the user's Gmail messages.
"""
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'https://my-notifier2.herokuapp.com/webcredentials.json', SCOPES)
        creds = flow.run_local_server(port=0)


    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('gmail', 'v1', credentials=creds)

#@app.before_first_request

def new_mail_checker():
    unread_msg_count = 0
    while True:
        print("in loop")
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q = "is:unread").execute()
        messages = results.get('messages', [])
        if len(messages) > unread_msg_count:
            print("in if")
            account_sid = 'ACeb44a0298b6deaadede4ce06127a52fd'
            auth_token = 'fdb97656046db19e99d5aa5a4d3f224b'
            client = Client(account_sid, auth_token)

            message = client.messages.create(
                            body=f"Sir Jahanzaib! You have {len(messages)} Unread Emails.\nReply With \'Check\' to check them.",
                            from_='whatsapp:+14155238886',
                            to='whatsapp:+923168838332'
                        )

            unread_msg_count = len(messages)

        print('out of if lopping',unread_msg_count)
        time.sleep(10)

thread = threading.Thread(target=new_mail_checker)


@app.route("/")
def home():
    print("in /")
    return "Assalam-o-Alaikum, World!" 
    

@app.route("/sms", methods=['POST'])
def sms_reply():
    print("in sms")

    """Respond to incoming messages with a text message."""
    # Fetch the message
    msg = request.form.get('Body')
    resp = MessagingResponse()

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q = "is:unread").execute()
    messages = results.get('messages', [])
    if msg == 'Check' or msg == 'check':
        print("in check")
        if not messages:
            resp.message('You have no New Mail.')
            return str(resp)
        else: 
            mail = f"Sir Jahanzaib! You have {len(messages)} unread mails in Gmail Account.\n"
            for message in messages:
                msg = service.users().messages().get(userId = 'me', id = message['id']).execute()          
                email_data = msg['payload']['headers']
                # subject = None
                # from_name = None

                for values in email_data:
                    name = values['name']
                    
                    if name == 'From':
                        from_name = values['value']
                    
                    if name == 'Subject':
                        subject = values['value']
                    # if subject == None or from_name == None:
                    #     continue
                    
                        mail = mail + (f"\nFrom: {from_name}\nSubject : {subject}\n    {msg['snippet']}\n")
                
            resp.message(mail)
            print(mail)
            time.sleep(2)
            return str(resp)
    elif msg == 'Running' or msg == 'running':
        resp.message('It\'s working...')
        print("in run")
        return str(resp)
    else:
        resp.message('I am a Simple Bot. Please Reply with \"Check\" to check your New Mails.')
        print("in else")
        return str(resp)

if __name__ == "__main__":
    thread.start()
    app.run(debug=True, threaded=True, use_reloader=False)
