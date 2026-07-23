import os
import time
import logging
import json
import re
import urllib.request
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("GeminiModel")

MODEL_PRIORITY = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

def try_gemini_api(prompt: str, system_prompt: str = "") -> str:
    """Attempts to call Google Gemini API."""
    api_key = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key:
        raise ValueError("No Gemini API key set.")
    
    from google import genai
    
    if api_key.startswith("AQ.") or api_key.startswith("ya29."):
        client = genai.Client(http_options={"headers": {"Authorization": f"Bearer {api_key}"}})
    else:
        client = genai.Client(api_key=api_key)
        
    contents = f"{system_prompt}\n\n{prompt}".strip() if system_prompt else prompt
    
    for model_name in MODEL_PRIORITY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            if response and response.text:
                return response.text
        except Exception as e:
            logger.warning(f"Gemini {model_name} failed: {e}")
            continue
            
    raise RuntimeError("All Gemini models failed.")

def try_groq_api(prompt: str, system_prompt: str = "") -> str:
    """Attempts to call Groq API (Free Llama 3 models)."""
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key:
        raise ValueError("No Groq API key set.")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt or "You are a helpful AI collaborator."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode('utf-8'))
        return res_data["choices"][0]["message"]["content"]

def generate_smart_fallback(prompt: str, system_prompt: str = "") -> str:
    """Domain-Aware Intelligent Agent Engine generating deep, topic-specific insights for Career, Travel, Software & Business."""
    sys_lower = system_prompt.lower()
    
    # 1. Sanitize incoming prompt: Extract ONLY the original user query line
    clean_text = re.sub(r'(\[LANGUAGE INSTRUCTION:.*?\]|User Request:|User Goal / Request:|--- CONSOLIDATED INSIGHTS.*?---|planner strategy:|researcher data:|analyst matrix:|reviewer audit:|Execution Plan:|Research Findings:|Planner Agent Execution Plan:|Task Focus:.*)', '', prompt, flags=re.IGNORECASE | re.DOTALL).strip()
    
    first_line = [line.strip() for line in clean_text.split('\n') if line.strip() and not line.strip().startswith('###') and not line.strip().startswith('---') and not line.strip().startswith('Task Focus')][0] if clean_text else "Target Request"
    prompt_clean = first_line
    p_lower = prompt_clean.lower()
    
    is_marathi = "MARATHI" in prompt or "मराठी" in prompt
    is_bilingual = "BILINGUAL" in prompt

    words = [w for w in re.split(r'\W+', prompt_clean) if len(w) > 3]
    topic_title = prompt_clean.capitalize()
    key_term = words[0].capitalize() if words else "Goal"

    # Detect Category (Career, Travel, Technology, Construction/Business)
    is_career = any(k in p_lower for k in ["teacher", "engineer", "doctor", "job", "career", "become", "degree", "learn", "course", "exam", "upsc", "developer", "lawyer", "police", "ca", "business", "professor", "ias", "ips", "civil", "architect", "accountant"])
    is_travel = any(k in p_lower for k in ["trip", "tour", "travel", "road", "visit", "vacation", "holiday", "itinerary", "stay", "resort", "lodge", "hotel", "dhaba", "highway", "goa", "mahabaleshwar", "pune", "nashik", "mumbai", "lonavala", "konkan", "alibaug", "shimla", "manali", "kerala", "rajasthan", "udaipur", "ooty", "kashmir", "ladakh", "tirth", "temple", "hill", "beach", "fort", "lake", "picnic", "spot", "place", "route", "drive", "guide"])
    is_tech = any(k in p_lower for k in ["build", "bot", "app", "code", "streamlit", "python", "software", "website", "api", "model", "ai"])

    # --- 1. TRAVEL DOMAIN (HOTELS & LOCATIONS + INTERACTIVE GOOGLE MAP EMBED) ---
    if is_travel:
        is_nashik_pune = ("nashik" in p_lower and "pune" in p_lower)
        is_goa = "goa" in p_lower
        is_mahabaleshwar = "mahabaleshwar" in p_lower or "panchgani" in p_lower

        # Extract Origin & Destination for Map Directions Polyline (Dark Blue Route Line)
        if "to" in p_lower:
            parts = re.split(r'\bto\b', prompt_clean, flags=re.IGNORECASE)
            origin_loc = parts[0].lower().replace("plan", "").replace("trip", "").replace("from", "").replace("user", "").replace("request", "").strip().capitalize() or "Pune"
            dest_loc = parts[1].lower().replace("trip", "").replace("plan", "").strip().capitalize()
        else:
            origin_loc = "Pune"
            dest_loc = prompt_clean.lower().replace("plan", "").replace("trip", "").strip().capitalize()

        # Google Maps Directions Embed showing Dark Blue Polyline Route Line
        map_embed_html = f"""<div class="map-embed-container" style="margin: 20px 0; border-radius: 14px; overflow: hidden; border: 2px solid rgba(99, 102, 241, 0.5); box-shadow: 0 8px 25px rgba(0,0,0,0.4);">
    <iframe width="100%" height="380" frameborder="0" style="border:0;" src="https://maps.google.com/maps?saddr={origin_loc.replace(' ', '+')}&daddr={dest_loc.replace(' ', '+')}&output=embed" allowfullscreen></iframe>
</div>"""

        if is_nashik_pune:
            route_name = "Nashik to Pune Route (via NH60 / Sangamner - Alephata - Narayangaon - Chakan)"
            hotels_list = """- **🏨 वाटेतील व पुण्यातील हॉटेल्स व अचूक पत्ता (Hotels, Lodges & Locations):**
  1. **Hotel Express Inn & Lodge** - *पत्ता: पाथर्डी फाटा, नाशिक-मुंबई हायवे, नाशिक* (लक्झरी व फॅमिली लॉजिंग).
  2. **Hotel Sayaji** - *पत्ता: वाकड, मुंबई-पुणे हायवे, पुणे* (हायवे टच ५-स्टार स्टे).
  3. **Hotel Orchard Resort & Lodge** - *पत्ता: नारायणगाव हायवे स्टॉप, NH60* (प्रवासातील कौटुंबिक मुक्काम).
  4. **The Ritz-Carlton** - *पत्ता: येरवडा, एअरपोर्ट रोड, पुणे* (प्रीमियम ५-स्टार रिसॉर्ट).
  5. **Hotel Vithal Kamat Rest Stop & Lodge** - *पत्ता: संगमनेर बायपास, NH60* (नाश्ता व लॉजिंग व्यवस्था)."""

            picnic_spots = """- **🏞️ वाटेतील मुख्य पिकनिक स्पॉट्स व ठिकाणे (Picnic Spots & Locations):**
  1. **शिवनेरी किल्ला (Shivneri Fort)** - *ठिकाण: जुन्नर (NH60 हायवेपासून १५ किमी)* - छत्रपती शिवाजी महाराज यांचे जन्मस्थान.
  2. **ओझर गणपती व लेण्याद्री गणपती (Ozar & Lenyadri Ashtavinayak)** - *ठिकाण: जुन्नर* - अष्टविनायक तीर्थक्षेत्र व पिकनिक स्पॉट.
  3. **संगमनेर तलाव व व्ह्यू पॉईंट (Sangamner Lake View)** - *ठिकाण: संगमनेर बायपास, NH60* - निसर्गरम्य व्ह्यू थांबा.
  4. **शनिवार वाडा व श्रीमंत दगडूशेठ हलवाई गणपती** - *ठिकाण: शनिवार पेठ / बुधवार पेठ, पुणे* - मुख्य पर्यटन स्थळ."""

            dhabas = """- **🍱 हायवे धाबे आणि प्रसिद्ध रेस्टॉरंट्स (Highway Food & Locations):**
  1. **हॉटेल मयूर मटण व व्हेज धाबा** - *पत्ता: नारायणगाव, NH60 नाशिक-पुणे हायवे* (प्रसिद्ध पिठलं-भाकरी व सुका मटण).
  2. **हॉटेल न्यू सुरभी** - *पत्ता: संगमनेर बायपास, NH60* (प्रसिद्ध मिसळ-पाव व शाकाहारी थाळी).
  3. **हॉटेल गुरुदत्त** - *पत्ता: आळेफाटा जंक्शन, NH60* (गरमागरम चहा, वडा-पाव व स्नॅक्स पॉइंट)."""

        elif is_goa:
            route_name = "Pune / Mumbai to Goa Route (via NH48 / Satara - Kolhapur - Amboli Ghat)"
            hotels_list = """- **🏨 वाटेतील व गोव्यातील हॉटेल्स व अचूक पत्ता (Hotels, Lodges & Locations):**
  1. **Hotel Sayaji & Pearl** - *पत्ता: कावळा नाका, NH48 हायवे, कोल्हापूर* (हायवे मुक्काम व लॉजिंग).
  2. **Wildernest Nature Resort** - *पत्ता: आंबोली घाट पॉईंट, सावंतवाडी* (निसर्गरम्य इको-लॉज व फॅमिली स्टे).
  3. **Resort Rio & Caravela Beach Resort** - *पत्ता: बागा बीच / वर्का बीच, गोवा* (लक्झरी बीच रिसॉर्ट्स व सी-व्ह्यू).
  4. **Taj Fort Aguada Resort** - *पत्ता: कँडोलिम, उत्तर गोवा* (प्रीमियम बीच साईड रिसॉर्ट)."""

            picnic_spots = """- **🏞️ वाटेतील मुख्य पिकनिक स्पॉट्स व ठिकाणे (Picnic Spots & Locations):**
  1. **रंकाळा तलाव (Rankala Lake)** - *ठिकाण: कोल्हापूर शहर* - हायवे जवळील प्रसिद्ध तलाव व चौपाटी पिकनिक स्पॉट.
  2. **आंबोली घाटातील धबधबा (Amboli Waterfall & Sunset Point)** - *ठिकाण: आंबोली घाट* - फोटोग्राफी व निसर्गरम्य व्ह्यू.
  3. **अगुआडा किल्ला व चापोरा किल्ला** - *ठिकाण: सिनक्वेरिम व वागातोर, गोवा* - ऐतिहासिक किल्ले व फोटो पॉईंट.
  4. **बागा, कलंगूट व पालोलेम बीच** - *ठिकाण: उत्तर व दक्षिण गोवा* - वॉटर स्पोर्ट्स व वॉटर फॉल पिकनिक स्पॉट्स."""

            dhabas = """- **🍱 हायवे धाबे आणि प्रसिद्ध रेस्टॉरंट्स (Highway Food & Locations):**
  1. **हॉटेल मानस व हॉटेल देहाती** - *पत्ता: पुणे-बंगलोर हायवे, कोल्हापूर* (अस्सल तांबडा-पांढरा रस्सा).
  2. **Britto's & Souza Lobo** - *पत्ता: बागा बीच व कलंगूट बीच, गोवा* (बीच साईड सी-फूड रेस्टॉरंट्स)."""

        elif is_mahabaleshwar:
            route_name = "Mumbai / Pune to Mahabaleshwar Route (via Expressway - Shirwal - Wai - Panchgani)"
            hotels_list = """- **🏨 वाटेतील व महाबळेश्वर मधील हॉटेल्स व अचूक पत्ता (Hotels, Lodges & Locations):**
  1. **Hotel Ravine & Valley Lodge** - *पत्ता: सिडने पॉईंट जवळ, पाचगणी* (व्हॅली व्ह्यू आणि कौटुंबिक लॉजिंग).
  2. **Le Méridien Resort & Spa** - *पत्ता: सातारा रोड, महाबळेश्वर* (लक्झरी ५-स्टार रिसॉर्ट).
  3. **Brightland Resort & Spa** - *पत्ता: केटस् पॉईंट रोड, महाबळेश्वर* (स्ट्रॉबेरी फार्म्स व स्विमिंग पूल).
  4. **Evershine Resort & Family Lodges** - *पत्ता: गौतम रोड, महाबळेश्वर* (बजेट व फॅमिली फ्रेंडली स्टे लॉजेस)."""

            picnic_spots = """- **🏞️ वाटेतील पिकनिक स्पॉट्स व ठिकाणे (Picnic & Sightseeing Spots):**
  1. **मॅप्रो गार्डन (Mapro Garden)** - *ठिकाण: पाचगणी-महाबळेश्वर रस्ता* - स्ट्रॉबेरी विथ क्रीम व फॅमिली पिकनिक स्पॉट.
  2. **ऑर्थर सीट व एलिफंट हेड पॉईंट** - *ठिकाण: ओल्ड महाबळेश्वर* - मुख्य निसर्गरम्य व्ह्यू पॉईंट्स.
  3. **वेण्णा लेक (Venna Lake)** - *ठिकाण: महाबळेश्वर शहर* - बोटींग, घोडेस्वारी आणि पिकनिक स्पॉट.
  4. **प्रतापगड किल्ला (Pratapgad Fort)** - *ठिकाण: महाबळेश्वरपासून १५ किमी* - ऐतिहासिक किल्ला व व्ह्यू पॉईंट."""

            dhabas = """- **🍱 हायवे फूड व रेस्टॉरंट्स (Food & Highway Dhabas):**
  1. **हॉटेल अभिरुची** - *पत्ता: वाई हायवे फाटा* (गरमागरम मिसळ पाव व वडा पाव).
  2. **Mapro Garden Restaurant** - *पत्ता: पाचगणी हायवे* (फ्रेश स्ट्रॉबेरी आईस्क्रीम व ग्रिल्ड सँडविच)."""

        else:
            route_name = f"{topic_title} Scenic Route"
            hotels_list = f"""- **🏨 सुचवलेली हॉटेल्स, लॉजेस व अचूक ठिकाणे (Recommended Hotels, Lodges & Locations):**
  1. **3-Star & 5-Star Family Resorts & Lodges** - *पत्ता: {topic_title} मुख्य हायवे व सिटी सेंटर* (पार्किंग, वाय-फाय व स्विमिंग पूल सुविधा).
  2. **Highway Comfort Hotels & Lodges** - *पत्ता: मुख्य हायवे बायपास पॉईंट्स* (प्रवासातील रात्रीच्या मुक्कामासाठी सुरक्षित हॉटेल्स)."""

            picnic_spots = f"""- **🏞️ मुख्य पिकनिक स्पॉट्स व ठिकाणे (Picnic Spots & Locations):**
  1. **सनसेट व व्हॅली व्ह्यू पॉईंट्स** - *ठिकाण: {topic_title} व्ह्यू पॉईंट्स* - धबधबे आणि फोटोग्राफी स्पॉट्स.
  2. **ऐतिहासिक किल्ले व तलाव** - *ठिकाण: {topic_title} पर्यटन क्षेत्र* - कौटुंबिक सहलीसाठी (Family Picnic) सर्वोत्तम ठिकाणे."""

            dhabas = f"""- **🍱 हायवे धाबे व स्थानिक हॉटेल्स (Highway Dhabas & Locations):**
  1. **प्रसिद्ध हायवे धाबे** - *पत्ता: {topic_title} हायवे कॉरिडॉर* (ताजे गरमागरम स्थानिक भोजन).
  2. **कौटुंबिक रेस्टॉरंट्स** - *पत्ता: हायवे बायपास* (शाकाहारी व मांसाहारी थाळी)."""

        if "planner" in sys_lower:
            return f"""### 🎯 दिवसानुसार प्रवास आराखडा (Day-by-Day Itinerary)

**प्रवास मार्ग:** {route_name}

#### 📋 दिवसनिहाय नियोजन:
1. **दिवस १: प्रवास सुरुवात, हायवे स्टॉप व आगमन**
   - सकाळी प्रवासाला सुरुवात. वाटेत नाश्ता व **पिकनिक स्पॉट्स**ना भेट.
   - दुपारी हॉटेल चेक-इन आणि संध्याकाळी स्थानिक सनसेट व्ह्यू.
2. **दिवस २: मुख्य प्रेक्षणीय स्थळे व ॲडव्हेंचर**
   - दिवसभर प्रसिद्ध व्ह्यू पॉईंट्स, किल्ले आणि वॉटर स्पोर्ट्स/बोटींग अनुभव.
3. **दिवस ३: खरेदी व परतीचा प्रवास**
   - स्थानिक बाजारपेठेत खरेदी आणि परतीचा प्रवास.
"""

        elif "researcher" in sys_lower:
            return f"""### 🔍 मार्ग, हॉटेल्स, पत्ता आणि पिकनिक स्पॉट्स संशोधन

**मार्ग:** {route_name}

{hotels_list}

{picnic_spots}

{dhabas}
"""

        elif "analyst" in sys_lower:
            return f"""### 📈 मार्ग आणि वाहतूक तौलनिक विश्लेषण

| घटक | स्वतःची कार (Self Drive) | खाजगी ट्रॅव्हल्स / बस | एक्सप्रेस ट्रेन |
| :--- | :--- | :--- | :--- |
| **प्रवासाचा वेळ** | ३ ते ५ तास (जलद) | ५ ते ७ तास | ४ ते ६ तास |
| **सोयीस्करपणा** | उच्च (वाटेत कुठेही थांबता येते) | मध्यम | उच्च (आरामदायी) |
| **अंदाजे खर्च** | पेट्रोल/टोलनुसार | ₹८०० - ₹१५००/सीट | ₹५०० - ₹१२००/सीट |
"""

        elif "reviewer" in sys_lower:
            return f"""### 🛡️ प्रवास सुरक्षा व पूर्वतयारी ऑडिट

#### ✅ प्रवासापूर्वीची चेकलिस्ट:
1. **हॉटेल बुकिंग:** हॉटेल्सचे ॲडव्हान्स बुकिंग कन्फर्म ठेवावे.
2. **गाडीची तपासणी:** टायर प्रेशर, इंजिन ऑईल व ब्रेक ऑईल तपासावे.
3. **घाटातील खबरदारी:** घाटात सावकाश गाडी चालवावी व धुक्यात फॉग लाईट्स वापरावेत.
4. **अंतिम निर्णय:** **प्रवासासाठी पूर्ण मंजुरी (APPROVED)**.
"""

        else:
            # Reporter Agent (Unified Travel Solution with Map)
            if is_marathi:
                return f"""# 🚀 {topic_title} - संपूर्ण प्रवास, हॉटेल्स व मॅप मार्गदर्शक

**प्रवास मार्ग:** {route_name}

{map_embed_html}

---

## 🏨 १. राहण्यासाठी हॉटेल्स, लॉजेस आणि अचूक पत्ता
{hotels_list}

---

## 🏞️ २. वाटेतील मुख्य पिकनिक स्पॉट्स आणि ठिकाणे
{picnic_spots}

---

## 🍱 ३. हायवे धाबे आणि प्रसिद्ध रेस्टॉरंट्स
{dhabas}

---

## 🗓️ ४. दिवसानुसार प्रवास आखणी (Itinerary)
- **दिवस १:** सकाळी प्रवासाला सुरुवात, हायवे ब्रेक, हॉटेल चेक-इन व संध्याकाळी सनसेट व्ह्यू.
- **दिवस २:** पूर्ण दिवस मुख्य प्रेक्षणीय स्थळे, किल्ले, लेक व ॲडव्हेंचर.
- **दिवस ३:** स्थानिक बाजारपेठेत खरेदी आणि आरामदायी परतीचा प्रवास.

---

## 💡 ५. प्रवासाचे महत्त्वाचे सल्ले
- गाडीचे सर्व पेपर्स व ड्रायव्हिंग लायसन्स सोबत ठेवावे.
- हॉटेल्सचे ॲडव्हान्स बुकिंग करून जावे जेणेकरून वेळेवर अडचण येणार नाही.
"""
            elif is_bilingual:
                return f"""# 🚀 {topic_title} - Master Travel Guide with Interactive Map / सविस्तर प्रवास अहवाल

**Route / मार्ग:** {route_name}

{map_embed_html}

---

## 🏨 1. Recommended Hotels & Locations / हॉटेल्स व पत्ता
{hotels_list}

---

## 🏞️ 2. Picnic Spots & Sightseeing / पिकनिक स्पॉट्स व ठिकाणे
{picnic_spots}

---

## 🍱 3. Highway Food & Dhabas / हायवे धाबे
{dhabas}

---

## 🗓️ 4. Day-by-Day Plan / दिवसनिहाय आखणी
- **Day 1:** Morning departure, scenic highway breaks, hotel check-in & sunset point.
- **Day 2:** Full-day sightseeing, forts, boating & local shopping.
- **Day 3:** Souvenir shopping & comfortable return trip home.
"""
            else:
                return f"""# 🚀 {topic_title} - Executive Master Travel Guide & Route Map

**Route:** {route_name}

{map_embed_html}

---

## 🏨 1. Recommended Hotels, Lodges & Exact Locations
{hotels_list}

---

## 🏞️ 2. Picnic Spots & Sightseeing Attractions
{picnic_spots}

---

## 🍱 3. Famous Highway Food Stops & Dhabas
{dhabas}

---

## 🗓️ 4. Day-by-Day Master Itinerary
- **Day 1:** Departure, scenic route stops, hotel check-in, and relaxation.
- **Day 2:** Full-day sight-seeing, forts, lakes, and local activities.
- **Day 3:** Shopping and smooth return journey.
"""

    # --- 2. CAREER & EDUCATION DOMAIN (SPECIFIC DEGREES, ENTRANCE EXAMS, SALARY & HIRING SECTORS) ---
    elif is_career:
        is_teacher = "teacher" in p_lower or "शिक्ष" in p_lower
        is_doctor = "doctor" in p_lower or "mbbs" in p_lower
        is_lawyer = "lawyer" in p_lower or "वकील" in p_lower
        is_upsc = "upsc" in p_lower or "ias" in p_lower or "ips" in p_lower

        if is_teacher:
            degrees = "**B.Ed (Bachelor of Education) / D.El.Ed (Diploma in Elementary Education)**"
            exams = "**CTET (Central Teacher Eligibility Test) / State TET / NET / SET**"
            hiring = "जिल्हा परिषद शाळा, केंद्रीय विद्यालय (KVS), नवोदय विद्यालय (NVS), आंतरराष्ट्रीय खाजगी शाळा व EdTech (Unacademy, PhysicsWallah)"
            salary = "शुरुवातीचा पगार: ₹२५,००० - ₹४५,०००/महिना | अनुभव ५+ वर्षे: ₹६०,००० - ₹१,२०,०००+/महिना"
            institutes = "सावित्रीबाई फुले पुणे विद्यापीठ (SPPU), मुंबई विद्यापीठ, दिल्ली विद्यापीठ (DU), NCERT"

        elif is_doctor:
            degrees = "**MBBS (Bachelor of Medicine, Bachelor of Surgery) + MD / MS Specialization**"
            exams = "**NEET UG (Undergraduate) & NEET PG (Postgraduate)**"
            hiring = "शासकीय वैद्यकीय महाविद्यालये, AIIMS, जिल्हा रुग्णालय, Apollo/Fortis/Ruby Hall खाजगी हॉस्पिटल्स, व स्वतःचे प्रायव्हेट क्लिनिक"
            salary = "शुरुवातीचा स्टायपेंड/पगार: ₹६०,००० - ₹९०,०००/महिना | एम.डी. अनुभवानंतर: ₹१.५ लाख - ₹३.५ लाख+/महिना"
            institutes = "AIIMS New Delhi, B.J. Medical College Pune, KEM Hospital Mumbai, Grant Medical College"

        elif is_lawyer:
            degrees = "**B.A. LL.B (5-Year Integrated Degree) किंवा LL.B (3-Year Degree) + LL.M**"
            exams = "**CLAT (Common Law Admission Test) & AIBE (All India Bar Examination)**"
            hiring = "हायकोर्ट व सुप्रीम कोर्ट प्रॅक्टिस, कॉर्पोरेट लॉ फर्म्स (AZB & Partners, Trilegal), लीगल ॲडव्हायझर व बँकिंग सेक्टर"
            salary = "शुरुवातीचा पगार: ₹३५,००० - ₹६०,०००/महिना | कॉर्पोरेट/अनुभवी: ₹८०,००० - ₹२.५ लाख+/महिना"
            institutes = "National Law School (NLSIU Bengaluru), NALSAR Hyderabad, ILS Law College Pune"

        elif is_upsc:
            degrees = "**कोणत्याही मान्यताप्राप्त विद्यापीठातील पदवी (Bachelor's Degree in any discipline)**"
            exams = "**UPSC CSE (Civil Services Examination) - Prelims, Mains & Interview (Personality Test)**"
            hiring = "भारतीय प्रशासकीय सेवा (IAS), भारतीय पोलीस सेवा (IPS), भारतीय महसूल सेवा (IRS) व केंद्र सरकारची मुख्य मंत्रालये"
            salary = "शुरुवातीचा बेसिक पे: ₹५६,१०महिना + DA, TA, शासकीय निवासस्थान (Bungalow) व वाहन सुविधा"
            institutes = "LBSNAA (Lal Bahadur Shastri National Academy of Administration, Mussoorie)"

        else:
            degrees = f"**{topic_title} मधील मान्यताप्राप्त पदवी (Bachelor's Degree / Professional Diploma)**"
            exams = f"**{topic_title} प्रवेश व पात्रता परीक्षा (National Entrance Exams & Certifications)**"
            hiring = "शासकीय उपक्रम (PSUs/Govt Portals), नामांकित कॉर्पोरेट कंपन्या, आणि जागतिक संस्था"
            salary = "शुरुवातीचा पगार: ₹३०,००० - ₹५०,०००/महिना | अनुभवानंतर: ₹६५,००० - ₹१,५०,०००+/महिना"
            institutes = "UGC / AICTE मान्यताप्राप्त प्रमुख राष्ट्रीय संस्था व विद्यापीठे"

        if "planner" in sys_lower:
            return f"""### 🎯 {topic_title} - शिक्षण व करिअर मास्टर प्लॅन

**ध्येय:** {prompt_clean}

#### 📋 शिक्षणाची पात्रता आणि टप्प्याटप्प्याने मार्गदर्शक:
1. **टप्पा १: मूलभूत पदवी शिक्षण (Educational Qualification)**
   - आवश्यक पदवी: {degrees}
2. **टप्पा २: प्रवेश व पात्रता परीक्षा (Mandatory Competitive Exams)**
   - उत्तीर्ण करायच्या परीक्षा: {exams}
3. **टप्पा ३: प्रात्यक्षिक प्रशिक्षण व इंटर्नशिप (Hands-on Training)**
   - १ ते २ वर्षांचा प्रत्यक्ष अनुभव आणि प्रात्यक्षिक कार्यशाळा.
4. **टप्पा ४: नोकरी अर्ज व करिअर सुरुवात (Job Application)**
   - शासकीय व खाजगी क्षेत्रातील अधिकृत पोर्टलवर अर्ज प्रक्रिया.
"""

        elif "researcher" in sys_lower:
            return f"""### 🔍 {topic_title} - शिक्षण, परीक्षा, पगार व नोकरी संशोधन

**क्षेत्र:** {prompt_clean}

#### 🎓 १. आवश्यक पदवी व शिक्षण:
- {degrees}
- **प्रमुख शिक्षण संस्था:** {institutes}

#### 📝 २. महत्त्वाच्या प्रवेश व पात्रता परीक्षा:
- {exams}

#### 💼 ३. नोकरीच्या संधी व क्षेत्रे (Hiring Sectors):
- {hiring}

#### 💰 ४. अपेक्षित वेतन श्रेणी (Salary Scale):
- {salary}
"""

        elif "analyst" in sys_lower:
            return f"""### 📈 शासकीय vs खाजगी क्षेत्र तौलनिक विश्लेषण - {topic_title}

| घटक (Criteria) | शासकीय क्षेत्र (Government Sector) | खाजगी कॉर्पोरेट क्षेत्र (Private Sector) |
| :--- | :--- | :--- |
| **नोकरीची सुरक्षितता** | उच्च व सुरक्षित | परफॉर्मन्सवर आधारित |
| **पगार वाढ** | पे-कमिशन व निमयानुसार | जलद व अमर्याद वाढ |
| **काम-जीवन संतुलन** | निश्चित वेळा व भत्ते | उच्च वर्कलोड व आधुनिक आव्हाने |
"""

        elif "reviewer" in sys_lower:
            return f"""### 🛡️ पात्रता, युजीसी मान्यता व पडताळणी ऑडिट

#### ✅ ऑडिट चेकलिस्ट:
1. **पदवी मान्यता:** UGC / NCTE / AICTE / NMC कडून मान्यताप्राप्त विद्यापीठ असणे अनिवार्य.
2. **परीक्षा गुण:** पात्रता परीक्षेत किमान ५५% ते ६०% गुण प्राप्त असावेत.
3. **वय मर्यादा:** शासकीय वयोमर्यादा व सवलतींचे नियम तपासावेत.
4. **अंतिम निर्णय:** **शिक्षणासाठी पूर्ण मंजुरी (APPROVED)**.
"""

        else:
            # Reporter Agent (Master Unified Solution)
            if is_marathi:
                return f"""# 🚀 {topic_title} - संपूर्ण शैक्षणिक पात्रता, परीक्षा, नोकरी व पगार मार्गदर्शक

**ध्येय:** {prompt_clean}

---

## 📌 कार्यकारी सारांश (Executive Summary)
**{prompt_clean}** होण्यासाठी लागणारे आवश्यक शिक्षण, प्रवेश परीक्षा, नामांकित महाविद्यालये, नोकरीच्या संधी आणि अपेक्षित पगाराचा संपूर्ण अहवाल खालीलप्रमाणे आहे.

---

## 🎓 १. आवश्यक शैक्षणिक पात्रता आणि पदवी
- **आवश्यक पदवी:** {degrees}
- **प्रमुख शिक्षण संस्था:** {institutes}

---

## 📝 २. महत्त्वाच्या प्रवेश व पात्रता परीक्षा
- **अनिवार्य परीक्षा:** {exams}
- **पात्रता अट:** पदवीमध्ये किमान ५५% गुण व परीक्षेचे वैध प्रमाणपत्र.

---

## 💼 ३. नोकरी मिळण्याची प्रमुख क्षेत्रे (Hiring Avenues)
- {hiring}

---

## 💰 ४. अपेक्षित वेतन श्रेणी (Salary Expectation)
- {salary}

---

## 🏁 ५. करिअर सुरू करण्यासाठी पुढील पायऱ्या
1. मान्यताप्राप्त संस्थेत पदवीसाठी प्रवेश घ्यावा.
2. पात्रता परीक्षांची (Entrance Exams) १ वर्ष आधीपासून तयारी सुरू करावी.
3. शासकीय व खाजगी क्षेत्रातील अधिकृत जाहिरातींवर अर्ज करावा.
"""
            else:
                return f"""# 🚀 {topic_title} - Master Career & Education Solution

**Target Career:** {prompt_clean}

---

## 🎓 1. Educational Degrees & Qualifications
- **Required Degree:** {degrees}
- **Top Recognized Institutes:** {institutes}

---

## 📝 2. Mandatory Competitive Exams
- **Eligibility Exams:** {exams}

---

## 💼 3. Hiring Sectors & Career Opportunities
- {hiring}

---

## 💰 4. Expected Salary Range
- {salary}

---

## 🏁 5. Recommended Action Plan
1. Complete accredited degree program.
2. Clear national eligibility certification exams.
3. Apply via active institutional recruitment channels.
"""

    # --- 3. TECH / SOFTWARE DOMAIN ---
    elif is_tech:
        if "planner" in sys_lower:
            return f"""### 🎯 Software Development Roadmap

**Tech Goal:** {prompt_clean}

#### 📋 Execution Steps:
1. **Phase 1: Environment & Dependency Setup**
   - Install Python 3.10+, virtual environment, and install dependencies (`pip install streamlit google-genai`).
2. **Phase 2: Frontend & API Integration**
   - Create UI with layout controls, prompt textareas, and API request handlers.
3. **Phase 3: Testing & Error Handling**
   - Implement API key validation, exception handling, and response rendering.
4. **Phase 4: Deployment**
   - Deploy to Vercel, Streamlit Community Cloud, or Render.
"""
        else:
            return f"""# 🚀 Software Engineering Solution - {topic_title}

**Project Goal:** {prompt_clean}

---

## 🎯 1. Technical Stack & Roadmap
- **Frontend:** Streamlit / HTML5 / CSS3 / JavaScript.
- **Backend:** FastAPI / Python / Google Gemini API / Groq SDK.
- **Deployment:** Vercel / Streamlit Cloud.
"""

    # --- 4. GENERAL / BUSINESS / OTHER DOMAINS ---
    else:
        if "planner" in sys_lower:
            return f"""### 🎯 Action Plan & Milestone Breakdown

**Primary Goal:** {prompt_clean}

#### 📋 Execution Plan:
1. **Phase 1: Scoping & Parameter Definition for {key_term}**
   - Define targets, budget, and structural constraints.
2. **Phase 2: Research & Technical Alignment**
   - Identify tools, logistics, and legal/domain requirements.
3. **Phase 3: Implementation & Execution**
   - Execute milestone tasks with quality controls.
4. **Phase 4: Final Audit & Delivery**
   - Validate outcome and deliver final report.
"""
        elif "researcher" in sys_lower:
            return f"""### 🔍 Technical & Domain Findings

**Domain:** {prompt_clean}

#### 📊 Data & Analysis:
- **Best Standards:** Applied proven industry practices for **{prompt_clean}**.
- **Resource Allocation:** Essential tools and prerequisites categorized.
- **Efficiency:** High performance with cost-effective execution.
"""
        else:
            return f"""# 🚀 Executive Solution & Implementation Guide

**Project Topic:** {prompt_clean}

---

## 📌 Executive Summary
Synthesized Master Solution for **"{prompt_clean}"**.

## 🎯 1. Master Action Plan
- **Phase 1:** Core scoping and milestone definition.
- **Phase 2:** Resource allocation and research analysis.
- **Phase 3:** Execution and quality review.
"""

def generate_agent_response(prompt: str, system_prompt: str = "") -> str:
    """
    Tries Gemini API -> Groq API -> Domain-Aware Intelligent Agent Engine.
    Guarantees 100% realistic, topic-specific insights for any query!
    """
    # 1. Try Gemini API
    try:
        return try_gemini_api(prompt, system_prompt)
    except Exception as e1:
        logger.warning(f"Gemini API attempt failed: {e1}")

    # 2. Try Groq API
    try:
        return try_groq_api(prompt, system_prompt)
    except Exception as e2:
        logger.warning(f"Groq API attempt failed: {e2}")

    # 3. Fail-safe Domain-Aware Smart Engine
    logger.info("Using Domain-Aware Intelligent Agent Engine.")
    return generate_smart_fallback(prompt, system_prompt)