import os
import dotenv
import dropbox

dotenv.load_dotenv()

APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET, token_access_type='offline')

# Get the authorization URL and direct the user to it
authorize_url = auth_flow.start()
print("1. Go to: " + authorize_url)
print("2. Click 'Allow' (you might have to log in first)")
print("3. Copy the authorization code.")

# Enter the authorization code from the Dropbox page
auth_code = input("Enter the authorization code here: ").strip()

# Complete the OAuth2 flow and get tokens
try:
    oauth_result = auth_flow.finish(auth_code)
    print("Access token:", oauth_result.access_token)
    print("Refresh token:", oauth_result.refresh_token)
except Exception as e:
    print("Error: " + str(e))
