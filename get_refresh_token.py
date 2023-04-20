import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

# Replace these with your own values
os.environ['OAUTH2_CLIENT_ID'] = 'GOOGLE_CAL_CLIENT_ID'
os.environ['OAUTH2_CLIENT_SECRET'] = 'GOOGLE_CAL_CLIENT_SECRET'

client_id = os.environ['OAUTH2_CLIENT_ID']
client_secret = os.environ['OAUTH2_CLIENT_SECRET']

flow = InstalledAppFlow.from_client_info(
    client_config={
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
        }
    },
    scopes=["https://www.googleapis.com/auth/calendar"],
)

creds = flow.run_local_server(port=0)

print("Refresh token:", creds.refresh_token)
