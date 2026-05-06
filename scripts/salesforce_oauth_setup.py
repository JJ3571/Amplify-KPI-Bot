#!/usr/bin/env python3
"""
Salesforce OAuth Setup Script
Interactive script to obtain and store OAuth refresh token for automated access
"""

import json
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict
import requests


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from Salesforce"""
    
    authorization_code = None
    
    def do_GET(self):
        """Handle GET request with authorization code"""
        # Parse query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            OAuthCallbackHandler.authorization_code = params['code'][0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <html>
            <head><title>Salesforce OAuth - Success</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✅ Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        elif 'error' in params:
            error = params.get('error', ['Unknown'])[0]
            error_desc = params.get('error_description', [''])[0]
            
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <html>
            <head><title>Salesforce OAuth - Error</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ Authorization Failed</h1>
                <p><strong>Error:</strong> {error}</p>
                <p>{error_desc}</p>
                <p>Please close this window and check the terminal for instructions.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress server log messages"""
        pass


def exchange_code_for_tokens(
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    instance_url: str
) -> Dict[str, str]:
    """
    Exchange authorization code for access and refresh tokens
    
    Args:
        code: Authorization code from OAuth callback
        client_id: OAuth client ID from Connected App
        client_secret: OAuth client secret from Connected App
        redirect_uri: Redirect URI (must match Connected App)
        instance_url: Salesforce instance URL
        
    Returns:
        Dictionary with tokens and instance info
    """
    token_url = f"{instance_url}/services/oauth2/token"
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    return response.json()


def run_oauth_flow():
    """Run interactive OAuth flow to obtain refresh token"""
    
    print("=" * 70)
    print("Salesforce OAuth Setup - Authorization Code Flow")
    print("=" * 70)
    print()
    print("This script will help you obtain a refresh token for automated access.")
    print("You'll need:")
    print("  1. A Connected App created in Salesforce")
    print("  2. Client ID and Client Secret from that app")
    print("  3. Your Salesforce instance URL")
    print()
    
    # Get configuration from user
    client_id = input("Enter Client ID from Connected App: ").strip()
    if not client_id:
        print("❌ Client ID is required")
        return
    
    client_secret = input("Enter Client Secret from Connected App: ").strip()
    if not client_secret:
        print("❌ Client Secret is required")
        return
    
    instance_url = input("Enter Salesforce instance URL (e.g., https://amplify.my.salesforce.com): ").strip()
    if not instance_url:
        print("❌ Instance URL is required")
        return
    
    # Remove trailing slash
    instance_url = instance_url.rstrip('/')
    
    # Use localhost callback
    redirect_uri = "http://localhost:8080/oauth/callback"
    port = 8080
    
    print()
    print("=" * 70)
    print("Step 1: Starting local callback server...")
    print("=" * 70)
    
    # Start local server to receive callback
    server = HTTPServer(('localhost', port), OAuthCallbackHandler)
    
    # Build authorization URL
    auth_url = f"{instance_url}/services/oauth2/authorize"
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'api refresh_token offline_access'
    }
    
    auth_url_full = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    print()
    print("=" * 70)
    print("Step 2: Opening browser for authorization...")
    print("=" * 70)
    print()
    print("Your browser will open to Salesforce login.")
    print("Please:")
    print("  1. Log in with your Okta/SSO credentials")
    print("  2. Authorize the Connected App")
    print("  3. Wait for the success message")
    print()
    print(f"If the browser doesn't open, visit this URL:")
    print(f"{auth_url_full}")
    print()
    
    input("Press Enter to open browser...")
    
    # Open browser
    webbrowser.open(auth_url_full)
    
    print()
    print("Waiting for authorization callback...")
    print("(This may take a minute - complete the login in your browser)")
    print()
    
    # Wait for one request (the callback)
    server.handle_request()
    
    if not OAuthCallbackHandler.authorization_code:
        print("❌ Failed to receive authorization code")
        return
    
    print()
    print("=" * 70)
    print("Step 3: Exchanging code for tokens...")
    print("=" * 70)
    
    try:
        tokens = exchange_code_for_tokens(
            OAuthCallbackHandler.authorization_code,
            client_id,
            client_secret,
            redirect_uri,
            instance_url
        )
        
        print("✅ Successfully obtained tokens!")
        print()
        
        # Save to credentials file
        credentials_file = "credentials.json"
        
        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
        except FileNotFoundError:
            creds = {}
        
        # Add Salesforce OAuth credentials
        creds.update({
            'salesforce_client_id': client_id,
            'salesforce_client_secret': client_secret,
            'salesforce_refresh_token': tokens['refresh_token'],
            'salesforce_instance_url': tokens['instance_url']
        })
        
        with open(credentials_file, 'w') as f:
            json.dump(creds, f, indent=2)
        
        print("=" * 70)
        print("✅ Setup Complete!")
        print("=" * 70)
        print()
        print(f"OAuth credentials saved to: {credentials_file}")
        print()
        print("The following were added/updated:")
        print(f"  - salesforce_client_id: {client_id[:20]}...")
        print(f"  - salesforce_client_secret: [hidden]")
        print(f"  - salesforce_refresh_token: [hidden]")
        print(f"  - salesforce_instance_url: {tokens['instance_url']}")
        print()
        print("You can now use the Salesforce API with:")
        print("  python salesforce_client.py")
        print()
        print("⚠️  Security Note:")
        print("  - Never commit credentials.json to git")
        print("  - The refresh token grants ongoing access")
        print("  - Keep it secure like a password")
        print()
        
    except Exception as e:
        print(f"❌ Token exchange failed: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")


if __name__ == "__main__":
    try:
        run_oauth_flow()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
