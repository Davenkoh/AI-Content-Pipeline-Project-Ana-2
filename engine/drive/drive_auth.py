#!/usr/bin/env python3
"""One-time OAuth consent for Drive uploads (user-delegated).
Prints the auth URL, opens the browser, runs a local server to catch the redirect,
and caches the token next to the client secret. Re-run any time to refresh.

Usage: python3 -u drive_auth.py
"""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drive_sync as D  # reuse _root(), SCOPES, OAUTH_TOKEN
from google_auth_oauthlib.flow import InstalledAppFlow

root = D._root()
cands = sorted(glob.glob(os.path.join(root, "oauth_client*.json")) +
               glob.glob(os.path.join(root, "client_secret*.json")))
if not cands:
    sys.exit("No OAuth client JSON at repo root (oauth_client*.json / client_secret*.json)")
print("client:", os.path.basename(cands[0]), flush=True)

flow = InstalledAppFlow.from_client_secrets_file(cands[0], D.SCOPES)
creds = flow.run_local_server(
    port=0, open_browser=True,
    authorization_prompt_message="\n>>> OPEN THIS URL TO AUTHORIZE (sign in, Advanced -> Continue -> Allow):\n\n{url}\n",
    success_message="Authorized. You can close this tab and return to the terminal.")
token_path = os.path.join(root, D.OAUTH_TOKEN)
with open(token_path, "w") as f:
    f.write(creds.to_json())
print("\nTOKEN SAVED ->", token_path, flush=True)
print("authorized account scopes:", creds.scopes, flush=True)
