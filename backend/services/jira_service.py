"""
Jira Import — pulls assigned issues from a Jira Cloud project as tasks.

Setup (free, up to 10 users on Jira Free plan):
  1. https://id.atlassian.com/manage-profile/security/api-tokens -> "Create API token"
  2. Put in backend/.env:
       JIRA_SITE_URL=https://yourname.atlassian.net
       JIRA_EMAIL=you@example.com
       JIRA_API_TOKEN=
"""
import os
import requests
from requests.auth import HTTPBasicAuth

SITE_URL = os.environ.get("JIRA_SITE_URL", "")
EMAIL = os.environ.get("JIRA_EMAIL", "")
API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")


def is_configured() -> bool:
    return bool(SITE_URL and EMAIL and API_TOKEN)


def fetch_my_issues() -> list:
    if not is_configured():
        return []

    resp = requests.get(
        f"{SITE_URL}/rest/api/3/search",
        auth=HTTPBasicAuth(EMAIL, API_TOKEN),
        headers={"Accept": "application/json"},
        params={"jql": "assignee=currentUser() AND statusCategory != Done"},
        timeout=10,
    )
    resp.raise_for_status()
    issues = resp.json().get("issues", [])

    return [
        {
            "jira_key": issue["key"],
            "title": issue["fields"]["summary"],
            "status": issue["fields"]["status"]["name"],
        }
        for issue in issues
    ]
