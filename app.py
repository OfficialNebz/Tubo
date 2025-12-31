import streamlit as st
import requests
import json
import time
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="TUBO / INTELLIGENCE",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE HIGH-VOLTAGE ENGINE (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Montserrat:wght@300;400;600&display=swap');

    html, body, .stApp { 
        background-color: #000000; 
        font-family: 'Montserrat', sans-serif !important; 
    }

    /* HEADINGS: TUBO MAGENTA */
    h1, h2, h3, h4 { 
        font-family: 'Playfair Display', serif !important; 
        letter-spacing: 1px; 
        color: #E91E63; /* TUBO Signature Pink */
        font-weight: 700;
    }

    /* BUTTONS: UNAPOLOGETIC */
    div.stButton > button {
        width: 100%;
        background-color: transparent;
        color: #E91E63;
        border: 2px solid #E91E63; /* Thicker border */
        padding: 14px 24px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
        transition: all 0.3s ease;
        border-radius: 0px;
    }

    div.stButton > button:hover {
        background-color: #E91E63;
        color: #FFFFFF;
        box-shadow: 0 0 15px rgba(233, 30, 99, 0.5); /* Glow effect */
        transform: scale(1.02);
    }

    /* INPUT FIELDS */
    div[data-baseweb="input"] > div, textarea {
        background-color: #111;
        border: 1px solid #333 !important;
        color: #FFF !important;
        text-align: center;
        border-radius: 0px;
    }

    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #222;
    }

    /* TOASTS */
    div[data-baseweb="toast"] {
        background-color: #E91E63 !important;
        color: #FFFFFF !important;
    }

    header {visibility: visible !important; background-color: transparent !important;}
    [data-testid="stDecoration"] {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION & SECRETS ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "results" not in st.session_state: st.session_state.results = None
if "p_name" not in st.session_state: st.session_state.p_name = ""
if "gen_id" not in st.session_state: st.session_state.gen_id = 0

api_key = st.secrets.get("GEMINI_API_KEY")
notion_token = st.secrets.get("NOTION_TOKEN")
notion_db_id = st.secrets.get("NOTION_DB_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### COMMAND CENTER")
    st.caption("Tubo Intelligence v1.0")
    if st.button("🔄 RESET SYSTEM"):
        st.session_state.clear()
        st.rerun()
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 12px; margin-top: 5px;'><em>Tap to clear cache & start new analysis.</em></div>",
        unsafe_allow_html=True)


# --- 5. AUTHENTICATION ---
def login_screen():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #E91E63;'>TUBO</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; letter-spacing: 3px; color: #888;'>THE ARCHITECT OF CURVES</p>",
                    unsafe_allow_html=True)

        password = st.text_input("PASSWORD", type="password", label_visibility="collapsed", placeholder="ENTER KEY")
        st.write("##")
        if st.button("UNLOCK"):
            if password == "neb123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("⚠️ ACCESS DENIED")


if not st.session_state.authenticated:
    login_screen()
    st.stop()


# --- 6. INTELLIGENCE ENGINE ---

def scrape_website(target_url):
    # Standard Scraper Logic (Optimized)
    headers = {'User-Agent': 'Mozilla/5.0'}
    clean_url = target_url.split('?')[0]
    json_url = f"{clean_url}.json"
    title = "Tubo Piece"
    desc_text = ""

    # Strategy 1: JSON
    try:
        r = requests.get(json_url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json().get('product', {})
            title = data.get('title', title)
            raw_html = data.get('body_html', "")
            soup = BeautifulSoup(raw_html, 'html.parser')
            desc_text = soup.get_text(separator="\n", strip=True)
    except:
        pass

    # Strategy 2: HTML
    if not desc_text:
        try:
            r = requests.get(target_url, headers=headers, timeout=5)
            soup = BeautifulSoup(r.content, 'html.parser')
            if soup.find('h1'): title = soup.find('h1').text.strip()
            # Generic Selectors usually work for Shopify sites like Tubo
            main_block = soup.find('div', class_='product-description') or \
                         soup.find('div', class_='rte') or \
                         soup.find('div', class_='product__description')
            if main_block: desc_text = main_block.get_text(separator="\n", strip=True)
        except Exception as e:
            return None, f"Scrape Error: {str(e)}"

    if not desc_text: return title, "[NO TEXT FOUND]"

    # Clean Text
    clean_lines = []
    for line in desc_text.split('\n'):
        upper = line.upper()
        if any(x in upper for x in ["SHIPPING", "RETURNS", "SIZE", "WHATSAPP", "ADD TO CART"]): continue
        if len(line) > 5: clean_lines.append(line)
    return title, "\n".join(clean_lines[:25])


def generate_campaign(product_name, description, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-flash-latest')

    # --- THE TUBO PROMPT ---
    prompt = f"""
    Role: Brand Voice Director for 'TUBO'.
    Brand Voice: "The Snatched Waist." Unapologetic, High-Voltage, Sculptural, Celebratory.
    Product: {product_name}
    Specs: {description}

    TASK:
    1. Select TOP 3 Personas.
    2. Write 3 Captions.
    3. Write 1 "Tubo Woman Signature".

    PERSONAS:
    1. The Headline Bride (Tone: All eyes on me. The main character energy.)
    2. The Global It-Girl (Tone: Lagos party tonight, Paris fashion week tomorrow.)
    3. The Power Curve (Tone: Executive presence, but make it feminine and bold.)

    CRITICAL INSTRUCTIONS:
    - FOCUS ON THE SILHOUETTE: Use words like 'snatched', 'sculpted', 'corsetry', 'hourglass'.
    - ENERGY: The Tubo woman enters the room and the room stops. Write with that confidence.
    - BANNED WORDS: "Modest", "Subtle", "Relaxed".

    Output JSON ONLY:
    [
        {{"persona": "Persona Name", "post": "Caption text..."}},
        ...
        {{"persona": "Tubo Woman Signature", "post": "The unified caption text..."}}
    ]
    """
    try:
        response = model.generate_content(prompt)
        txt = response.text
        if "```json" in txt: txt = txt.split("```json")[1].split("```")[0]
        return json.loads(txt.strip())
    except Exception as e:
        return [{"persona": "Error", "post": f"AI ERROR: {str(e)}"}]


def save_to_notion(p_name, post, persona, token, db_id):
    if not token or not db_id: return False, "Notion Secrets Missing"

    # AUTO-FIX FOR ID
    clean_db_id = str(db_id).strip().replace("/", "")

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": clean_db_id},
        "properties": {
            "Product Name": {"title": [{"text": {"content": str(p_name)}}]},
            "Persona": {"rich_text": [{"text": {"content": str(persona)}}]},
            "Generated Post": {"rich_text": [{"text": {"content": str(post)[:2000]}}]},
            "Status": {"status": {"name": "Draft"}}
        }
    }

    try:
        response = requests.post(NOTION_API_URL, headers=headers, data=json.dumps(data), timeout=5)
        if response.status_code == 200:
            return True, "Success"
        else:
            return False, f"Notion Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"System Error: {str(e)}"


# --- 7. UI LAYOUT ---
st.markdown("<br>", unsafe_allow_html=True)
st.title("TUBO / INTELLIGENCE")
st.markdown("---")

# --- MANUAL ADDED HERE ---
with st.expander("📖 SYSTEM MANUAL (CLICK TO OPEN)"):
    st.markdown("### OPERATIONAL GUIDE")
    st.markdown("---")

    # Step 1
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.markdown("**STEP 1: SOURCE**\n\nGo to the Tubo Woman site. Open a single product page.")
    with c2:
        try:
            st.image("Screenshot (593).png", use_container_width=True)
        except:
            st.warning("⚠️ Screenshot (593).png not found.")

    st.markdown("---")

    # Step 2
    c3, c4 = st.columns([1, 1.5])
    with c3:
        st.markdown("**STEP 2: ACQUIRE**\n\nCopy the URL from the browser bar.")
    with c4:
        try:
            st.image("Screenshot (594).png", use_container_width=True)
        except:
            st.warning("⚠️ Screenshot (594).png not found.")

    st.markdown("---")

    # Step 3
    c5, c6 = st.columns([1, 1.5])
    with c5:
        st.markdown("**STEP 3: EXECUTE**\n\nPaste the URL below and click 'GENERATE ASSETS'.")
    with c6:
        try:
            st.image("Screenshot (595).png", use_container_width=True)
        except:
            st.warning("⚠️ Screenshot (595).png not found.")

# INPUT
url_input = st.text_input("Product URL", placeholder="Paste TUBO URL...")

if st.button("GENERATE ASSETS", type="primary"):
    if not api_key:
        st.error("API Key Missing.")
    elif not url_input:
        st.error("Paste a URL first.")
    else:
        with st.spinner("Analyzing Silhouette & Structure..."):
            st.session_state.gen_id += 1
            p_name, p_desc = scrape_website(url_input)
            if p_name is None:
                st.error(p_desc)
            else:
                st.session_state.p_name = p_name
                st.session_state.results = generate_campaign(p_name, p_desc, api_key)

# --- 8. RESULTS DASHBOARD ---
if st.session_state.results:
    st.divider()
    st.subheader(st.session_state.p_name.upper())

    # BULK EXPORT
    if st.button("💾 EXPORT CAMPAIGN TO NOTION", type="primary", use_container_width=True):
        if not notion_token:
            st.error("Notion Config Missing")
        else:
            success = 0
            with st.spinner("Syncing to Notion..."):
                bar = st.progress(0)
                for i, item in enumerate(st.session_state.results):
                    p_val = item.get('persona', '')
                    final_post = st.session_state.get(f"editor_{i}_{st.session_state.gen_id}", item.get('post', ''))
                    if p_val and final_post:
                        s, m = save_to_notion(st.session_state.p_name, final_post, p_val, notion_token, notion_db_id)
                        if s: success += 1
                    bar.progress((i + 1) / len(st.session_state.results))

            if success > 0:
                st.success(f"Uploaded {success} Assets.")
                time.sleep(1)
                st.rerun()

    st.markdown("---")

    # EDITORS
    current_gen = st.session_state.gen_id
    for i, item in enumerate(st.session_state.results):
        persona = item.get('persona', 'Unknown')
        post = item.get('post', '')

        with st.container():
            c1, c2 = st.columns([0.75, 0.25])
            with c1:
                st.subheader(persona)
                edited = st.text_area(label=persona, value=post, height=200, key=f"editor_{i}_{current_gen}",
                                      label_visibility="collapsed")
            with c2:
                st.write("##");
                st.write("##")
                if st.button("SAVE", key=f"btn_{i}_{current_gen}"):
                    with st.spinner("Saving..."):
                        s, m = save_to_notion(st.session_state.p_name, edited, persona, notion_token, notion_db_id)
                        if s:
                            st.toast("✅ Saved")
                        else:
                            st.error(m)
        st.divider()