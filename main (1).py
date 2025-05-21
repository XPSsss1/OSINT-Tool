import time
import sys
import os
import requests # This library is now used for real API calls

# ASCII Banner
BANNER = """
 ██████╗ ███████╗██╗███╗   ██╗████████╗
██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
██║   ██║███████╗██║██╔██╗ ██║   ██║   
██║   ██║╚════██║██║██║╚██╗██║   ██║   
╚██████╔╝███████║██║██║ ╚████║   ██║   
 ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   
"""

# --- Utility Functions for Terminal Output ---
def print_styled(text, style="info"):
    """Prints styled messages to the terminal."""
    if style == "header":
        print("\n" + "=" * 60)
        print(f"  {text.upper()}")
        print("=" * 60)
    elif style == "subheader":
        print(f"\n--- {text} ---")
    elif style == "info":
        print(f"[INFO] {text}")
    elif style == "warning":
        print(f"[WARN] {text}")
    elif style == "error":
        print(f"[ERROR] {text}")
    elif style == "success":
        print(f"[SUCCESS] {text}")
    else:
        print(text)

def simulate_loading(message="Processing", duration=2):
    """Simulates a loading animation in the terminal."""
    chars = "/-\\|"
    start_time = time.time()
    sys.stdout.write(f"{message} ")
    while time.time() - start_time < duration:
        for char in chars:
            sys.stdout.write(f"\r{message} {char}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r") # Clear loading line
    sys.stdout.flush()

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """Pauses execution until user presses Enter."""
    input("\nPress Enter to continue...")

# --- API Key Configuration ---
# Read API keys from environment variables
# Users will set these in their shell or Replit secrets
API_KEYS = {
    "IPINFO_API_KEY": os.getenv("OSINT_IPINFO_API_KEY"),
    "HIBP_API_KEY": os.getenv("OSINT_HIBP_API_KEY"),
    "SHODAN_API_KEY": os.getenv("OSINT_SHODAN_API_KEY"),
    # Add more API keys here as you integrate more real APIs
}

# --- Core OSINT Lookup Logic (with real API attempts) ---
def perform_osint_lookup(tool_id, query_input):
    """
    Attempts to perform a real OSINT lookup using configured API keys.
    Falls back to simulated data if API key is missing or call fails.
    """
    print_styled(f"Executing {tool_id.replace('_', ' ').title()} for: '{query_input}'", "info")

    # --- REAL API INTEGRATION EXAMPLES ---
    if tool_id == 'ipGeolocation':
        api_key = API_KEYS.get("IPINFO_API_KEY")
        if api_key:
            print_styled("Attempting real IP Geolocation via IPinfo.io...", "info")
            try:
                simulate_loading("Querying IPinfo.io", 2.5)
                response = requests.get(f"https://ipinfo.io/{query_input}/json?token={api_key}", timeout=5)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                data = response.json()
                if not data.get('error'):
                    print_styled("Real IP Geolocation data fetched successfully!", "success")
                    return {
                        "query": query_input,
                        "country": data.get('country_name', data.get('country', 'N/A')), # Use country_name from ipinfo.io if available
                        "city": data.get('city', 'N/A'),
                        "region": data.get('region', 'N/A'),
                        "latitude": data.get('loc', 'N/A').split(',')[0] if data.get('loc') else 'N/A',
                        "longitude": data.get('loc', 'N/A').split(',')[1] if data.get('loc') else 'N/A',
                        "isp": data.get('org', 'N/A'),
                        "timezone": data.get('timezone', 'N/A'),
                        "postal": data.get('postal', 'N/A'),
                        "real_data": True
                    }
                else:
                    print_styled(f"IPinfo.io API returned an error: {data.get('error', 'Unknown error')}", "error")
            except requests.exceptions.RequestException as e:
                print_styled(f"Failed to connect to IPinfo.io API: {e}", "error")
            except Exception as e:
                print_styled(f"Error processing IPinfo.io response: {e}", "error")
            print_styled("Falling back to simulated data for IP Geolocation.", "warning")
        else:
            print_styled("IPinfo.io API key not found. Using simulated data.", "warning")

    elif tool_id == 'emailBreachChecker':
        api_key = API_KEYS.get("HIBP_API_KEY")
        if api_key:
            print_styled("Attempting real Email Breach Check via HaveIBeenPwned...", "info")
            headers = {
                'hibp-api-key': api_key,
                'User-Agent': 'UltimateOSINTTool-v1.0', # HIBP requires a User-Agent
                'Accept': 'application/json'
            }
            try:
                simulate_loading("Querying HaveIBeenPwned", 2.5)
                response = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{query_input}", headers=headers, timeout=5)

                if response.status_code == 404:
                    print_styled("Email not found in any known breaches.", "success")
                    return {"query": query_input, "breaches": [], "pastes": [], "found": False, "real_data": True}

                response.raise_for_status()
                data = response.json()

                breaches_found = [b['Name'] for b in data]
                print_styled(f"Real Email Breach data fetched successfully! Found {len(breaches_found)} breaches.", "success")
                return {
                    "query": query_input,
                    "breaches": breaches_found,
                    "pastes": [], # HIBP v3 API doesn't directly return pastes with breachedaccount
                    "found": len(breaches_found) > 0,
                    "real_data": True
                }
            except requests.exceptions.RequestException as e:
                print_styled(f"Failed to connect to HIBP API: {e}", "error")
                if response.status_code == 401:
                    print_styled("Check your HIBP API key. It might be invalid.", "error")
                elif response.status_code == 403:
                    print_styled("Access forbidden. Check HIBP API key permissions or rate limits.", "error")
            except Exception as e:
                print_styled(f"Error processing HIBP response: {e}", "error")
            print_styled("Falling back to simulated data for Email Breach Check.", "warning")
        else:
            print_styled("HaveIBeenPwned API key not found. Using simulated data.", "warning")

    elif tool_id == 'shodanIpScanner':
        api_key = API_KEYS.get("SHODAN_API_KEY")
        if api_key:
            print_styled("Attempting real Shodan IP Scan...", "info")
            try:
                simulate_loading("Querying Shodan.io", 3)
                response = requests.get(f"https://api.shodan.io/shodan/host/{query_input}?key={api_key}", timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get('error'):
                    print_styled(f"Shodan API returned an error: {data.get('error')}", "error")
                else:
                    open_ports = [f"{p['port']} ({p.get('service')})" for p in data.get('ports', [])]
                    services = [s['product'] for s in data.get('data', []) if s.get('product')]
                    vulnerabilities = data.get('vulns', [])

                    print_styled("Real Shodan data fetched successfully!", "success")
                    return {
                        "query": query_input,
                        "ip": data.get('ip_str'),
                        "country": data.get('country_name'),
                        "city": data.get('city'),
                        "isp": data.get('isp'),
                        "organization": data.get('org'),
                        "openPorts": open_ports,
                        "services": services,
                        "vulnerabilities": vulnerabilities,
                        "real_data": True
                    }
            except requests.exceptions.RequestException as e:
                print_styled(f"Failed to connect to Shodan API: {e}", "error")
            except Exception as e:
                print_styled(f"Error processing Shodan response: {e}", "error")
            print_styled("Falling back to simulated data for Shodan IP Scan.", "warning")
        else:
            print_styled("Shodan API key not found. Using simulated data.", "warning")
    # --- END REAL API INTEGRATION EXAMPLES ---

    # --- SIMULATED DATA FALLBACK (for all tools, and if real API fails) ---
    simulate_loading("Generating simulated data", 1.5)
    mock_data = {"query": query_input, "simulated": True}

    if tool_id == 'emailBreachChecker':
        mock_data.update({
            "breaches": ['Adobe 2013', 'LinkedIn 2012', 'Collection #1'] if 'example.com' in query_input else [],
            "pastes": ['Pastebin (2020)', 'Hastebin (2021)'] if 'test@' in query_input else [],
            "found": '@' in query_input
        })
    elif tool_id == 'emailValidityChecker':
        mock_data.update({
            "isValid": '@' in query_input and '.' in query_input,
            "syntaxOk": True,
            "domainExists": True
        })
    elif tool_id == 'emailToPhoneMapper':
        mock_data.update({
            "phoneNumber": '+15551234567 (simulated)' if 'john.doe@' in query_input else 'Not found (simulated)'
        })
    elif tool_id == 'emailDnsMxLookup':
        mock_data.update({
            "mxRecords": ['gmail-smtp-in.l.google.com', 'alt1.gmail-smtp-in.l.google.com'] if 'gmail.com' in query_input else ['mail.example.com'],
            "spfRecord": 'v=spf1 include:_spf.google.com ~all'
        })
    elif tool_id == 'emailProviderDetection':
        mock_data.update({
            "provider": 'Gmail' if 'gmail.com' in query_input else ('Outlook' if 'outlook.com' in query_input else 'Custom/Unknown')
        })
    elif tool_id == 'emailProfilePictureFetcher':
        mock_data.update({
            "gravatarFound": 'Yes' if 'test@example.com' in query_input else 'No',
            "gravatarUrl": 'https://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50?s=200' if 'test@example.com' in query_input else 'N/A'
        })
    elif tool_id == 'disposableEmailDetector':
        mock_data.update({
            "isDisposable": 'mailinator.com' in query_input or 'tempmail.org' in query_input
        })
    elif tool_id == 'emailSocialMediaPresence':
        mock_data.update({
            "socialMedia": ['Twitter', 'LinkedIn'] if 'elon.musk@x.com' in query_input else ['LinkedIn']
        })
    elif tool_id == 'googleAccountInfo':
        mock_data.update({
            "googleAccountFound": 'Possible' if 'google.com' in query_input else 'Unlikely',
            "lastLoginAttempt": '2024-05-20 (simulated)'
        })
    elif tool_id == 'emailDomainCompanyFinder':
        mock_data.update({
            "companyName": 'Google LLC' if 'google.com' in query_input else 'Unknown',
            "companyWebsite": 'https://www.google.com' if 'google.com' in query_input else 'N/A'
        })
    # Phone Number OSINT
    elif tool_id == 'phoneNumberCarrierLookup':
        mock_data.update({
            "carrier": 'AT&T Mobility' if '555' in query_input else 'Verizon Wireless',
            "country": 'United States'
        })
    elif tool_id == 'phoneNumberGeolocation':
        mock_data.update({
            "possibleLocation": 'California, USA (simulated)' if '555' in query_input else 'New York, USA (simulated)',
            "timezone": 'America/Los_Angeles'
        })
    elif tool_id == 'phoneNumberTypeDetection':
        mock_data.update({
            "type": 'VOIP' if query_input.startswith('+1800') else 'Mobile'
        })
    elif tool_id == 'socialMediaLinkedToPhone':
        mock_data.update({
            "linkedAccounts": ['WhatsApp', 'Telegram'] if '1234567' in query_input else []
        })
    elif tool_id == 'spamCallDatabaseCheck':
        mock_data.update({
            "spamRisk": 'High (Reported by 100+ users)' if '555-0100' in query_input else 'Low'
        })
    elif tool_id == 'internationalPhoneFormatting':
        mock_data.update({
            "formatted": '+1 (555) 123-4567',
            "countryCode": '+1',
            "nationalFormat": '(555) 123-4567'
        })
    elif tool_id == 'reversePhoneNumberLookup':
        mock_data.update({
            "name": 'John Doe (simulated)' if '555-0100' in query_input else 'Unknown',
            "address": '123 Main St, Anytown (simulated)'
        })
    elif tool_id == 'voipVsNonVoipDetector':
        mock_data.update({
            "isVoip": query_input.startswith('+1800')
        })
    # IP & Location OSINT (excluding ipGeolocation which has real integration)
    elif tool_id == 'ipReverseDnsLookup':
        mock_data.update({
            "reverseDns": 'dns.google' if query_input == '8.8.8.8' else 'Unknown Host'
        })
    elif tool_id == 'ipAsnIspDetection':
        mock_data.update({
            "asn": 'AS15169',
            "isp": 'Google LLC',
            "organization": 'Google'
        })
    elif tool_id == 'ipToDomainHostname':
        mock_data.update({
            "domain": 'cloudflare.com' if query_input == '1.1.1.1' else 'Unknown'
        })
    elif tool_id == 'ipBlacklistCheck':
        mock_data.update({
            "blacklisted": 'Yes (Spamhaus, Barracuda)' if query_input == '192.0.2.1' else 'No'
        })
    elif tool_id == 'portScanner':
        mock_data.update({
            "openPorts": ['22 (SSH)', '80 (HTTP)', '443 (HTTPS)'] if query_input == '127.0.0.1' else ['No common ports open']
        })
    elif tool_id == 'ipTraceroute':
        mock_data.update({
            "hops": ['1. Router (192.168.1.1)', '2. ISP Gateway (10.0.0.1)', '3. Next Hop (x.x.x.x)', '... (simulated)']
        })
    elif tool_id == 'subnetCalculator':
        mock_data.update({
            "networkAddress": '192.168.1.0',
            "broadcastAddress": '192.168.1.255',
            "usableHosts": 254
        })
    elif tool_id == 'localIpFinder':
        mock_data.update({
            "localIp": '192.168.1.100 (simulated)'
        })
    elif tool_id == 'vpnProxyTorDetector':
        mock_data.update({
            "detected": 'VPN/Proxy Detected' if '104.28.1.1' in query_input else 'No VPN/Proxy/TOR'
        })
    # Domain & Website OSINT
    elif tool_id == 'whoisLookup':
        mock_data.update({
            "registrant": 'Domain Privacy Service (simulated)',
            "creationDate": '1995-03-15',
            "expirationDate": '2025-03-15',
            "registrar": 'MarkMonitor Inc.'
        })
    elif tool_id == 'dnsRecordFetcher':
        mock_data.update({
            "aRecords": ['192.0.2.1'],
            "mxRecords": ['mail.example.com'],
            "nsRecords": ['ns1.example.com', 'ns2.example.com']
        })
    elif tool_id == 'subdomainFinder':
        mock_data.update({
            "subdomains": ['www', 'blog', 'api', 'dev']
        })
    elif tool_id == 'websiteTechnologyStackIdentifier':
        mock_data.update({
            "technologies": ['React', 'Node.js', 'Nginx', 'Tailwind CSS']
        })
    elif tool_id == 'sslCertificateInfoGrabber':
        mock_data.update({
            "issuer": 'Let\'s Encrypt',
            "validFrom": '2024-01-01',
            "validTo": '2024-04-01',
            "subject": 'example.com'
        })
    elif tool_id == 'websiteArchiveChecker':
        mock_data.update({
            "snapshots": ['2000-01-01', '2010-05-10', '2023-11-20']
        })
    elif tool_id == 'webCrawlerForMetadata':
        mock_data.update({
            "metaDescription": 'This is a simulated website description.',
            "keywords": ['simulated', 'web', 'data'],
            "author": 'Simulated Author'
        })
    elif tool_id == 'openDirectoryScanner':
        mock_data.update({
            "foundDirectories": ['/admin/', '/uploads/', '/backup/']
        })
    elif tool_id == 'siteCmsDetector':
        mock_data.update({
            "cms": 'WordPress'
        })
    elif tool_id == 'domainAgeChecker':
        mock_data.update({
            "domainAgeYears": 29,
            "creationDate": '1995-03-15'
        })
    # Username / Social Media OSINT
    elif tool_id == 'usernameCheckerAcrossPlatforms':
        mock_data.update({
            "availableOn": ['Facebook', 'Instagram'],
            "takenOn": ['Twitter', 'GitHub']
        })
    elif tool_id == 'socialMediaPresenceGrabber':
        mock_data.update({
            "profiles": {
                "twitter": f"https://twitter.com/{query_input}",
                "instagram": f"https://instagram.com/{query_input}",
                "linkedin": f"https://linkedin.com/in/{query_input}"
            }
        })
    elif tool_id == 'twitterInfoExtractor':
        mock_data.update({
            "followers": 12345,
            "following": 678,
            "tweets": 5678,
            "bio": 'Simulated Twitter user.',
            "joinDate": '2010-01-01'
        })
    elif tool_id == 'instagramMetadataFetcher':
        mock_data.update({
            "posts": 150,
            "followers": 9876,
            "following": 432,
            "isPrivate": False
        })
    elif tool_id == 'tiktokUserInfoScanner':
        mock_data.update({
            "followers": '1.2M',
            "likes": '15M',
            "videos": 200
        })
    elif tool_id == 'youtubeChannelOsint':
        mock_data.update({
            "subscribers": '500K',
            "totalViews": '100M',
            "videosCount": 300,
            "joinDate": '2015-06-01'
        })
    elif tool_id == 'redditProfileScraper':
        mock_data.update({
            "karma": 15000,
            "cakeDay": '2018-03-01',
            "subreddits": ['r/OSINT', 'r/Cybersecurity']
        })
    elif tool_id == 'linkedinProfileAnalyzer':
        mock_data.update({
            "jobTitle": 'Senior OSINT Analyst',
            "company": 'Simulated Corp',
            "connections": 500
        })
    elif tool_id == 'githubUserProfileAnalyzer':
        mock_data.update({
            "repos": 25,
            "followers": 120,
            "stars": 500,
            "joinDate": '2017-09-01'
        })
    elif tool_id == 'profilePictureRecognition':
        mock_data.update({
            "matchFound": 'High confidence match (simulated)' if 'john.doe' in query_input else 'No match found (simulated)'
        })
    # Image & File OSINT
    elif tool_id == 'exifMetadataViewer':
        mock_data.update({
            "make": 'Canon',
            "model": 'EOS 5D Mark IV',
            "dateTaken": '2023-10-26 14:30:00',
            "gps": '34.0522 N, 118.2437 W (Los Angeles, CA) (simulated)',
            "software": 'Adobe Photoshop'
        })
    elif tool_id == 'reverseImageSearchViaApi':
        mock_data.update({
            "matches": ['Similar image on Wikipedia', 'Product page on Amazon']
        })
    elif tool_id == 'imageGeolocationFromMetadata':
        mock_data.update({
            "location": 'Eiffel Tower, Paris, France (simulated)',
            "latitude": 48.8584,
            "longitude": 2.2945
        })
    elif tool_id == 'pdfMetadataAnalyzer':
        mock_data.update({
            "author": 'Jane Doe',
            "creationDate": '2023-01-15',
            "lastModified": '2023-01-20',
            "software": 'Microsoft Word'
        })
    elif tool_id == 'documentFingerprinting':
        mock_data.update({
            "hash": 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0',
            "unique": True
        })
    elif tool_id == 'hashBasedMalwareCheck':
        mock_data.update({
            "virustotalResult": 'Detected as Malware (simulated)' if 'malware' in query_input else 'Clean (simulated)'
        })
    # Advanced OSINT / Other (excluding shodanIpScanner)
    elif tool_id == 'macAddressVendorLookup':
        mock_data.update({
            "vendor": 'Apple Inc.',
            "addressRange": '00:00:00:00:00:00 - 00:00:00:00:00:FF'
        })
    elif tool_id == 'deviceFingerprintGenerator':
        mock_data.update({
            "fingerprint": 'Browser: Chrome, OS: Windows 10, Screen: 1920x1080 (simulated)'
        })
    elif tool_id == 'osintAutomationToolRunner':
        mock_data.update({
            "status": 'Automation script for ' + query_input + ' executed (simulated).',
            "output": 'Simulated output from automation tool.'
        })
    elif tool_id == 'pastebinScraper':
        mock_data.update({
            "mentions": ['Found 3 pastes mentioning "password" (simulated)'] if 'password' in query_input else ['No mentions found (simulated)']
        })
    elif tool_id == 'googleDorkBuilder':
        mock_data.update({
            "dorks": [
                f'site:example.com inurl:admin "{query_input}"',
                f'filetype:pdf "confidential" "{query_input}"',
                f'intitle:"index of" "{query_input}"'
            ],
            "searchUrl": f'https://www.google.com/search?q=site:example.com+"{query_input}"'
        })
    else:
        mock_data.update({"error": "Tool not implemented or invalid query.", "simulated": True})

    return mock_data

# --- Tool Definitions ---
# Each tool has an ID, name, description, input prompt, and optional API key requirement.
TOOLS = {
    "emailOsint": {
        "name": "📧 Email OSINT",
        "tools": {
            "emailBreachChecker": {"name": "Email Breach Checker", "desc": "Check if an email has appeared in known data breaches.", "prompt": "Enter email address:"},
            "emailValidityChecker": {"name": "Email Validity Checker", "desc": "Verify if an email address is valid and exists.", "prompt": "Enter email address:"},
            "emailToPhoneMapper": {"name": "Email-to-Phone Number Mapper", "desc": "Attempt to map an email to a phone number (simulated).", "prompt": "Enter email address:"},
            "emailDnsMxLookup": {"name": "Email DNS/MX Record Lookup", "desc": "Retrieve DNS MX records for an email domain.", "prompt": "Enter email address:"},
            "emailProviderDetection": {"name": "Email Provider Detection", "desc": "Identify the email service provider.", "prompt": "Enter email address:"},
            "emailProfilePictureFetcher": {"name": "Email Profile Picture Fetcher (Gravatar)", "desc": "Check for associated Gravatar profile pictures.", "prompt": "Enter email address:"},
            "disposableEmailDetector": {"name": "Disposable Email Detector", "desc": "Determine if an email is from a disposable service.", "prompt": "Enter email address:"},
            "emailSocialMediaPresence": {"name": "Email Social Media Presence Checker", "desc": "Find social media accounts linked to an email (simulated).", "prompt": "Enter email address:"},
            "googleAccountInfo": {"name": "Google Account Info Extractor", "desc": "Extract public info from Google accounts (simulated).", "prompt": "Enter email address:"},
            "emailDomainCompanyFinder": {"name": "Email Domain Company Finder", "desc": "Find company details associated with an email domain.", "prompt": "Enter email address:"},
        }
    },
    "phoneNumberOsint": {
        "name": "📱 Phone Number OSINT",
        "tools": {
            "phoneNumberCarrierLookup": {"name": "Phone Number Carrier Lookup", "desc": "Identify the mobile carrier for a phone number.", "prompt": "Enter phone number:"},
            "phoneNumberGeolocation": {"name": "Phone Number Geolocation", "desc": "Find the approximate location of a phone number (simulated).", "prompt": "Enter phone number:"},
            "phoneNumberTypeDetection": {"name": "Phone Number Type Detection", "desc": "Determine if it's mobile, VOIP, or landline.", "prompt": "Enter phone number:"},
            "socialMediaLinkedToPhone": {"name": "Social Media Accounts Linked to Phone", "desc": "Discover social media profiles linked to a phone number (simulated).", "prompt": "Enter phone number:"},
            "spamCallDatabaseCheck": {"name": "Spam Call Database Check", "desc": "Check if a number is reported for spam calls (simulated).", "prompt": "Enter phone number:"},
            "internationalPhoneFormatting": {"name": "International Phone Formatting + Info", "desc": "Format and get info on international numbers.", "prompt": "Enter phone number:"},
            "reversePhoneNumberLookup": {"name": "Reverse Phone Number Lookup", "desc": "Attempt to find name/address associated with a number (simulated).", "prompt": "Enter phone number:"},
            "voipVsNonVoipDetector": {"name": "VOIP vs Non-VOIP Detector", "desc": "Distinguish between VOIP and traditional numbers.", "prompt": "Enter phone number:"},
        }
    },
    "ipLocationOsint": {
        "name": "🌍 IP & Location OSINT",
        "tools": {
            "ipGeolocation": {"name": "IP Geolocation", "desc": "Locate an IP address on a map (requires IPinfo.io API Key).", "prompt": "Enter IP Address:"},
            "ipReverseDnsLookup": {"name": "IP Reverse DNS Lookup", "desc": "Find the hostname associated with an IP.", "prompt": "Enter IP Address:"},
            "ipAsnIspDetection": {"name": "IP ASN and ISP Detection", "desc": "Identify the Autonomous System Number and Internet Service Provider.", "prompt": "Enter IP Address:"},
            "ipToDomainHostname": {"name": "IP to Domain/Hostname", "desc": "Resolve an IP address to its associated domain or hostname.", "prompt": "Enter IP Address:"},
            "ipBlacklistCheck": {"name": "IP Blacklist Check", "desc": "Check if an IP is listed on known spam/malware blacklists (simulated).", "prompt": "Enter IP Address:"},
            "portScanner": {"name": "Port Scanner", "desc": "Scan for open ports on a target IP address (simulated).", "prompt": "Enter IP Address:"},
            "ipTraceroute": {"name": "IP Traceroute", "desc": "Trace the path an IP packet takes to reach its destination (simulated).", "prompt": "Enter IP Address:"},
            "subnetCalculator": {"name": "Subnet Calculator", "desc": "Calculate network details from an IP and subnet mask (e.g., 192.168.1.0/24).", "prompt": "Enter IP/CIDR:"},
            "localIpFinder": {"name": "Local IP Finder", "desc": "Discover your local IP address (simulated).", "prompt": "N/A (Press Enter to get local IP):"},
            "vpnProxyTorDetector": {"name": "VPN/Proxy/TOR Detector", "desc": "Detect if an IP address belongs to a VPN, proxy, or TOR exit node (simulated).", "prompt": "Enter IP Address:"},
        }
    },
    "domainWebsiteOsint": {
        "name": "🌐 Domain & Website OSINT",
        "tools": {
            "whoisLookup": {"name": "WHOIS Lookup", "desc": "Retrieve domain registration information.", "prompt": "Enter domain name:"},
            "dnsRecordFetcher": {"name": "DNS Record Fetcher", "desc": "Fetch A, MX, NS, and other DNS records.", "prompt": "Enter domain name:"},
            "subdomainFinder": {"name": "Subdomain Finder", "desc": "Discover subdomains associated with a main domain (simulated).", "prompt": "Enter domain name:"},
            "websiteTechnologyStackIdentifier": {"name": "Website Technology Stack Identifier", "desc": "Identify technologies used by a website (e.g., CMS, frameworks) (simulated).", "prompt": "Enter website URL:"},
            "sslCertificateInfoGrabber": {"name": "SSL Certificate Info Grabber", "desc": "Extract details from a website's SSL certificate.", "prompt": "Enter website URL:"},
            "websiteArchiveChecker": {"name": "Website Archive Checker (Wayback Machine)", "desc": "View historical versions of a website (simulated).", "prompt": "Enter website URL:"},
            "webCrawlerForMetadata": {"name": "Web Crawler for Metadata", "desc": "Crawl a website to extract metadata (simulated).", "prompt": "Enter website URL:"},
            "openDirectoryScanner": {"name": "Open Directory Scanner", "desc": "Scan for publicly accessible directories (simulated).", "prompt": "Enter website URL:"},
            "siteCmsDetector": {"name": "Site CMS Detector", "desc": "Automatically detect the Content Management System (CMS) (simulated).", "prompt": "Enter website URL:"},
            "domainAgeChecker": {"name": "Domain Age Checker", "desc": "Determine the age of a domain name.", "prompt": "Enter domain name:"},
        }
    },
    "usernameSocialMediaOsint": {
        "name": "👤 Username / Social Media OSINT",
        "tools": {
            "usernameCheckerAcrossPlatforms": {"name": "Username Checker Across Platforms", "desc": "Check username availability or existence across social media (simulated).", "prompt": "Enter username:"},
            "socialMediaPresenceGrabber": {"name": "Social Media Presence Grabber", "desc": "Find linked social media profiles for a username (simulated).", "prompt": "Enter username:"},
            "twitterInfoExtractor": {"name": "Twitter Info Extractor", "desc": "Extract public information from a Twitter profile (simulated).", "prompt": "Enter Twitter handle:"},
            "instagramMetadataFetcher": {"name": "Instagram Metadata Fetcher", "desc": "Fetch public metadata from an Instagram profile (simulated).", "prompt": "Enter Instagram username:"},
            "tiktokUserInfoScanner": {"name": "TikTok User Info Scanner", "desc": "Scan public TikTok user information (simulated).", "prompt": "Enter TikTok username:"},
            "youtubeChannelOsint": {"name": "YouTube Channel OSINT", "desc": "Gather public data from a YouTube channel (simulated).", "prompt": "Enter YouTube channel URL/ID:"},
            "redditProfileScraper": {"name": "Reddit Profile Scraper", "desc": "Scrape public data from a Reddit user profile (simulated).", "prompt": "Enter Reddit username:"},
            "linkedinProfileAnalyzer": {"name": "LinkedIn Profile Analyzer", "desc": "Analyze public LinkedIn profile data (simulated).", "prompt": "Enter LinkedIn profile URL:"},
            "githubUserProfileAnalyzer": {"name": "GitHub User Profile Analyzer", "desc": "Analyze public GitHub user profile data (simulated).", "prompt": "Enter GitHub username:"},
            "profilePictureRecognition": {"name": "Profile Picture Recognition Tool", "desc": "Attempt to find matching profiles based on a profile picture (simulated).", "prompt": "Enter image URL/path:"},
        }
    },
    "imageFileOsint": {
        "name": "🖼️ Image & File OSINT",
        "tools": {
            "exifMetadataViewer": {"name": "EXIF Metadata Viewer", "desc": "Extract metadata from images (simulated).", "prompt": "Enter image URL/path:"},
            "reverseImageSearchViaApi": {"name": "Reverse Image Search via API", "desc": "Find the source or similar images online (simulated).", "prompt": "Enter image URL/path:"},
            "imageGeolocationFromMetadata": {"name": "Image Geolocation from Metadata", "desc": "Extract GPS coordinates from image EXIF (simulated).", "prompt": "Enter image URL/path:"},
            "pdfMetadataAnalyzer": {"name": "PDF Metadata Analyzer", "desc": "Extract metadata from PDF documents (simulated).", "prompt": "Enter PDF URL/path:"},
            "documentFingerprinting": {"name": "Document Fingerprinting", "desc": "Generate a unique hash for a document (simulated).", "prompt": "Enter document URL/path:"},
            "hashBasedMalwareCheck": {"name": "Hash-based Malware Check", "desc": "Check if a file hash is known malware (simulated).", "prompt": "Enter file hash:"},
        }
    },
    "advancedOsint": {
        "name": "🧠 Advanced OSINT / Other",
        "tools": {
            "macAddressVendorLookup": {"name": "MAC Address Vendor Lookup", "desc": "Identify the manufacturer from a MAC address (simulated).", "prompt": "Enter MAC Address:"},
            "deviceFingerprintGenerator": {"name": "Device Fingerprint Generator", "desc": "Generate a unique fingerprint for a device (simulated).", "prompt": "N/A (Press Enter to generate):"},
            "osintAutomationToolRunner": {"name": "OSINT Automation Tool Runner", "desc": "Simulate running an external OSINT automation script.", "prompt": "Enter script name/command:"},
            "shodanIpScanner": {"name": "Shodan IP Scanner", "desc": "Scan an IP for exposed services via Shodan (requires Shodan API Key).", "prompt": "Enter IP Address:"},
            "pastebinScraper": {"name": "Pastebin Scraper", "desc": "Scrape Pastebin for keywords (simulated).", "prompt": "Enter keyword:"},
            "googleDorkBuilder": {"name": "Google Dork Builder + Search", "desc": "Build advanced Google search queries (dorks) and provide search URL.", "prompt": "Enter search term:"},
        }
    },
    "osintWebsites": {
        "name": "🌐 OSINT Websites",
        "tools": {
            "websiteList": {
                "name": "List of OSINT Websites",
                "desc": "A curated list of valuable external resources. Open these manually in your browser.",
                "urls": [
                    {"name": "HaveIBeenPwned", "url": "https://haveibeenpwned.com/"},
                    {"name": "Epieos", "url": "https://epieos.com/"},
                    {"name": "PhoneInfoga (web version)", "url": "https://phoneinfoga.crvx.fr/"},
                    {"name": "Hunter.io", "url": "https://hunter.io/"},
                    {"name": "EmailRep", "url": "https://emailrep.io/"},
                    {"name": "TrueCaller (for phone lookup)", "url": "https://www.truecaller.com/"},
                    {"name": "WhatIsMyIP / IPInfo.io", "url": "https://ipinfo.io/"},
                    {"name": "ViewDNS.info", "url": "https://viewdns.info/"},
                    {"name": "IntelligenceX", "url": "https://intelx.io/"},
                    {"name": "DNSdumpster", "url": "https://dnsdumpster.com/"},
                    {"name": "VirusTotal", "url": "https://www.virustotal.com/"},
                    {"name": "Exif.tools", "url": "https://exif.tools/"},
                    {"name": "Censys.io", "url": "https://censys.io/"},
                    {"name": "Shodan.io", "url": "https://www.shodan.io/"},
                    {"name": "Archive.org (Wayback Machine)", "url": "https://archive.org/web/"},
                    {"name": "Social-Searcher", "url": "https://www.social-searcher.com/"},
                    {"name": "Namechk", "url": "https://namechk.com/"},
                    {"name": "Dehashed", "url": "https://dehashed.com/"},
                    {"name": "BreachDirectory", "url": "https://breachdirectory.org/"},
                    {"name": "ZoomEye", "url": "https://www.zoomeye.org/"},
                    {"name": "Tineye (reverse image)", "url": "https://tineye.com/"},
                    {"name": "Scylla.sh", "url": "https://scylla.sh/"},
                ]
            }
        }
    }
}

# --- Main Application Logic ---

def display_main_menu():
    """Displays the main categories menu."""
    clear_screen()
    print_styled(BANNER, "info")
    print_styled("Ultimate OSINT Terminal Tool", "header")
    print("\nChoose an OSINT category:")
    for i, (cat_id, cat_data) in enumerate(TOOLS.items()):
        print(f"{i+1}. {cat_data['name']}")
    print("0. Exit")
    print("-" * 60)

def display_category_menu(category_id):
    """Displays tools within a selected category."""
    clear_screen()
    category_data = TOOLS[category_id]
    print_styled(f"{category_data['name']} Tools", "header")
    print("\nSelect a tool to use:")
    tools_list = list(category_data['tools'].items())
    for i, (tool_id, tool_data) in enumerate(tools_list):
        print(f"{i+1}. {tool_data['name']}")
    print("0. Back to Main Menu")
    print("-" * 60)

def run_tool_logic(category_id, tool_id):
    """Handles input and output for a specific tool."""
    tool_data = TOOLS[category_id]['tools'][tool_id]
    print_styled(f"{tool_data['name']}", "subheader")
    print_styled(tool_data['desc'], "info")

    if tool_id == "websiteList": # Special case for OSINT Websites
        print_styled("\nHere are the recommended OSINT websites:", "info")
        for site in tool_data['urls']:
            print(f"  - {site['name']}: {site['url']}")
        print_styled("\nCopy and paste these URLs into your browser.", "warning")
        return

    query_input = input(f"{tool_data['prompt']} ").strip()
    if not query_input and tool_data['prompt'] != "N/A (Press Enter to get local IP):" and tool_data['prompt'] != "N/A (Press Enter to generate):":
        print_styled("Input cannot be empty. Returning to menu.", "warning")
        return

    results = perform_osint_lookup(tool_id, query_input)

    print_styled("\n--- Results ---", "subheader")
    if results.get("error"):
        print_styled(f"Error: {results['error']}", "error")
    else:
        # Determine if real data was used
        if results.get("real_data"):
            print_styled("Data Source: REAL API", "success")
        else:
            print_styled("Data Source: SIMULATED", "warning")
            print_styled("For real data, ensure API keys are set and tool is fully integrated.", "warning")

        for key, value in results.items():
            if key not in ["query", "simulated", "real_data"]: # Don't print internal keys
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, list):
                    print(f"  - {formatted_key}:")
                    if value:
                        for item in value:
                            if isinstance(item, dict): # For nested structures like profiles
                                for sub_key, sub_value in item.items():
                                    print(f"    - {sub_key.replace('_', ' ').title()}: {sub_value}")
                            else:
                                print(f"    - {item}")
                    else:
                        print("    None")
                elif isinstance(value, dict):
                    print(f"  - {formatted_key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    - {sub_key.replace('_', ' ').title()}: {sub_value}")
                else:
                    print(f"  - {formatted_key}: {value if value is not None else 'N/A'}")
    print_styled("--- End Results ---", "subheader")

# --- Main Loop ---
def main():
    # Check for requests library
    try:
        import requests
    except ImportError:
        print_styled("The 'requests' library is not installed.", "error")
        print_styled("Please install it using: pip install requests", "error")
        pause()
        sys.exit(1)

    while True:
        display_main_menu()
        main_choice = input("Enter your choice: ").strip()

        if main_choice == '0':
            print_styled("Exiting Ultimate OSINT Tool. Stay safe!", "info")
            break

        try:
            main_choice_idx = int(main_choice) - 1
            category_ids = list(TOOLS.keys())
            if 0 <= main_choice_idx < len(category_ids):
                selected_category_id = category_ids[main_choice_idx]

                while True:
                    display_category_menu(selected_category_id)
                    tool_choice = input("Enter your tool choice: ").strip()

                    if tool_choice == '0':
                        break # Back to main menu

                    tools_list = list(TOOLS[selected_category_id]['tools'].items())
                    try:
                        tool_choice_idx = int(tool_choice) - 1
                        if 0 <= tool_choice_idx < len(tools_list):
                            selected_tool_id, _ = tools_list[tool_choice_idx]
                            run_tool_logic(selected_category_id, selected_tool_id)
                            pause()
                        else:
                            print_styled("Invalid tool choice. Please try again.", "error")
                            pause()
                    except ValueError:
                        print_styled("Invalid input. Please enter a number.", "error")
                        pause()
            else:
                print_styled("Invalid category choice. Please try again.", "error")
                pause()
        except ValueError:
            print_styled("Invalid input. Please enter a number.", "error")
            pause()

if __name__ == "__main__":
    main()
