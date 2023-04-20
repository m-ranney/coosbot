import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

# Replace these with your own values

os.environ['OAUTH2_CLIENT_ID'] = 'GOOGLE_CAL_CLIENT_ID'
os.environ['OAUTH2_CLIENT_SECRET'] = 'GOOGLE_CAL_CLIENT_SECRET'

client_id = os.environ['OAUTH2_CLIENT_ID']
client_secret = os.environ['OAUTH2_CLIENT_SECRET']

print("OAUTH2_CLIENT_ID:", client_id)
print("OAUTH2_CLIENT_SECRET:", client_secret)

flow = InstalledAppFlow.from_client_config(
    client_config={
        "installed": {
            "client_id": '276102916706-h6q7orgvm879tpj3cq36rvjsmarhq5hq.apps.googleusercontent.com',
            "client_secret": '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',
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
        }
    },
    scopes=["https://www.googleapis.com/auth/calendar"],
)

creds = flow.run_local_server(port=8080)

print("Refresh token:", creds.refresh_token)

