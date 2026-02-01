import subprocess
import json
import logging
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_subfinder_installed():
    """Check if subfinder is installed"""
    return shutil.which('subfinder') is not None

def scan_subdomains_osint(domain):
    """Execute passive subdomain enumeration via subfinder"""
    subdomains = set()
    
    # Check if subfinder is installed
    if not check_subfinder_installed():
        logging.error("subfinder is not installed. Please install it first:")
        logging.error("go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest")
        return subdomains
    
    logging.info(f"Running subfinder for {domain['name']}")
    
    try:
        # Run subfinder with JSON output
        result = subprocess.run(
            ['subfinder', '-d', domain['name'], '-json', '-silent'],
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes timeout
        )
        
        if result.returncode != 0:
            logging.error(f"subfinder error: {result.stderr}")
            return subdomains
        
        # Parse JSON output (one JSON object per line)
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    subdomain = data.get('host', '').strip().lower()
                    if subdomain:
                        subdomains.add(subdomain)
                except json.JSONDecodeError:
                    continue
        
        logging.info(f"Found {len(subdomains)} subdomains for {domain['name']}")
        
    except subprocess.TimeoutExpired:
        logging.error(f"subfinder timeout for {domain['name']}")
    except Exception as e:
        logging.error(f"subfinder error: {e}")
    
    return subdomains