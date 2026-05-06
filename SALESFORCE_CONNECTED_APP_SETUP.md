# Salesforce Connected App Setup Guide

This guide is for **Salesforce administrators** to create a Connected App for the Amplify KPI Bot to access Salesforce data via OAuth 2.0 API.

---

## Overview

The Amplify KPI Bot needs API access to query Salesforce reports and data. Since your organization uses Okta SSO, standard username/password authentication won't work. Instead, the bot will use OAuth 2.0 with a refresh token.

**What this enables:**

- Automated data retrieval from Salesforce (reports)
- Works with Okta SSO enforcement
- Secure, revokable access
- No need to store passwords

---

## Step 1: Create Connected App

1. **Log into Salesforce** as an administrator
2. **Navigate to Setup** → Search for "App Manager"
3. **Click "New Connected App"**
4. **Fill in Basic Information:**

   - **Connected App Name:** `Amplify KPI Bot`
   - **API Name:** `Amplify_KPI_Bot` (auto-fills)
   - **Contact Email:** Your email address
5. **Enable OAuth Settings:**

   - ☑️ Check "Enable OAuth Settings"
6. **Callback URL:**

   ```
   http://localhost:8080/oauth/callback
   ```

   *(This is for one-time interactive setup only)*
7. **Selected OAuth Scopes** - Add these scopes:

   - `Access and manage your data (api)`
   - `Perform requests on your behalf at any time (refresh_token, offline_access)`
8. **Additional Settings:**

   - ☑️ Check "Require Secret for Web Server Flow"
   - ☑️ Check "Require Secret for Refresh Token Flow"
   - Leave other checkboxes unchecked
9. **Click "Save"**
10. **Click "Continue"** on the confirmation page

---

## Step 2: Get Client ID and Client Secret

After creating the Connected App:

1. **Go back to App Manager** (Setup → App Manager)
2. **Find "Amplify KPI Bot"** in the list
3. **Click the dropdown arrow** → Select "View"
4. **Copy these values:**

   - **Consumer Key** = This is the `Client ID`
   - **Consumer Secret** = Click "Click to reveal" to see the `Client Secret`

**Save these values securely** - you'll need to provide them to the user running the OAuth setup script.

---

## Step 3: Configure Policies (Important!)

1. **Still on the Connected App details page**, click "Edit Policies"
2. **Permitted Users:**

   - Select: **"Admin approved users are pre-authorized"**
   - This allows specific users/profiles to use the app
3. **IP Relaxation:**

   - Select: **"Relax IP restrictions"**
   - This allows the refresh token to work from different locations
4. **Refresh Token Policy:**

   - Select: **"Refresh token is valid until revoked"**
   - This ensures the bot can run indefinitely
5. **Click "Save"**

---

## Step 4: Assign Users/Profiles

You need to grant access to the users who will authorize the app:

1. **On the Connected App page**, scroll to "Profiles" or "Permission Sets"
2. **Click "Manage Profiles"** or "Manage Permission Sets"
3. **Select the appropriate profile/permission set:**

   - Add the profile of the user who will run the initial OAuth setup
   - Typically "System Administrator" or a service account profile
4. **Click "Save"**

---

## Step 5: Verify API Access

Ensure the user has these permissions:

- ✅ **"API Enabled"** permission
- ✅ Access to required objects (Case, Report, etc.)
- ✅ "View All Data" or specific object permissions as needed

Check under: **Setup → Users → [Select User] → Permission Sets or Profile**

---

## Step 6: Provide Credentials to User

Give the user these three pieces of information:

1. **Client ID** (Consumer Key from Step 2)
2. **Client Secret** (Consumer Secret from Step 2)
3. **Instance URL** (e.g., `https://amplify.my.salesforce.com`)

The user will run the OAuth setup script to complete authorization.

---

## Security Best Practices

### Token Management

- ✅ Refresh tokens grant ongoing access - treat them like passwords
- ✅ They can be revoked at any time from Setup → Session Management
- ✅ Set up monitoring for API usage

### Access Control

- ✅ Use "Admin approved users are pre-authorized" to control who can authorize
- ✅ Create a dedicated service account user with minimal required permissions
- ✅ Consider using a Permission Set for granular access control

### Auditing

- ✅ Review API usage regularly in Setup → Event Monitoring
- ✅ Check Login History for OAuth logins
- ✅ Monitor for unusual patterns

---

## Troubleshooting

### "Redirect URI mismatch" error

- Ensure the callback URL is exactly: `http://localhost:8080/oauth/callback`
- No trailing slashes
- Must match exactly what's in the Connected App

### "User is not admin approved"

- Check that the user's profile is added in Step 4
- Verify the Connected App policy is set to "Admin approved users are pre-authorized"

### "API not enabled for user"

- Verify user has "API Enabled" permission
- Check profile or permission sets

### Refresh token expires unexpectedly

- Check Connected App policies → ensure "valid until revoked" is selected
- Verify IP Relaxation is enabled
- Check org-wide session timeout settings

---

## Revoking Access

If you need to revoke the bot's access:

### Option 1: Revoke the Refresh Token

1. **Setup → Identity → OAuth and OpenID Connect Settings**
2. Find the token and revoke it

### Option 2: Disable the Connected App

1. **Setup → App Manager**
2. Find "Amplify KPI Bot"
3. Click dropdown → "Disable"

### Option 3: Remove User Access

1. **Setup → App Manager → Amplify KPI Bot**
2. Click "Manage Profiles" or "Manage Permission Sets"
3. Remove the user's profile

---

## Summary Checklist

- [ ] Created Connected App with OAuth enabled
- [ ] Set callback URL to `http://localhost:8080/oauth/callback`
- [ ] Added required OAuth scopes (api, refresh_token, offline_access)
- [ ] Enabled "Require Secret for Web Server Flow"
- [ ] Configured policies (admin approved, IP relaxation, refresh token valid until revoked)
- [ ] Assigned user profiles/permission sets
- [ ] Verified user has API Enabled permission
- [ ] Provided Client ID, Client Secret, and Instance URL to user

---

## Next Steps

After completing this setup:

1. **Provide credentials** to the user (Client ID, Secret, Instance URL)
2. **User runs OAuth setup:**

   ```bash
   python scripts/salesforce_oauth_setup.py
   ```
3. **User logs in** via Okta/SSO when browser opens
4. **Refresh token is saved** to credentials.json
5. **Bot can now access Salesforce API** automatically

---

## Questions?

Contact your Salesforce administrator or refer to:

- [Salesforce Connected Apps Documentation](https://help.salesforce.com/s/articleView?id=sf.connected_app_overview.htm)
- [OAuth 2.0 Web Server Flow](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_web_server_flow.htm)
