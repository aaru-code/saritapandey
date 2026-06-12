"""
╔══════════════════════════════════════════════════════════╗
║   LIC Mitra — AI Chatbot for Sarita Pandey's Website    ║
║   Smart • Friendly • Funny • Client-Attracting 🤖🛡️      ║
╚══════════════════════════════════════════════════════════╝
Run: python chatbot.py
API: http://localhost:5000/chat
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import re
import datetime

app = Flask(__name__)
CORS(app)   # Allow requests from the website

# ──────────────────────────────────────────────
# AGENT KNOWLEDGE BASE
# ──────────────────────────────────────────────
AGENT = {
    "name":       "Sarita Pandey",
    "code":       "LIC-2014-SP007",
    "branch":     "Hazratganj Branch, Lucknow, UP – 226001",
    "phone":      "+91 70076 29909",
    "email":      "saritapandey7007629@gmail.com",
    "since":      "2014",
    "experience": "10+ years",
    "clients":    "500+",
    "policies":   "1200+",
    "settlement": "98%",
    "hours":      "Mon–Sat, 9:30 AM – 6:00 PM",
}

# ──────────────────────────────────────────────
# RESPONSE LIBRARY  (multiple variants per topic)
# ──────────────────────────────────────────────
RESPONSES = {

    "greeting": [
        f"""🙏 <b>Namaste ji!</b> Main hoon <b>LIC Mitra</b> — Sarita Pandey ji ka digital dost! 😄<br><br>
Aap bilkul sahi jagah aaye hain! Yahan insurance se lekar investment tak — sab milega, woh bhi bina kisi confusion ke! 🎯<br><br>
Bataiye, main aapki kya madad kar sakta hoon?""",

        f"""🤩 Arre waah! Aap aa gaye! <b>LIC Mitra</b> yahan hai — ready, set, insure! 🚀<br><br>
Main <b>Sarita Pandey ji</b> ka AI assistant hoon. Yahan koi boring robot nahi milega — seedha dil se baat karte hain! ❤️<br><br>
Kya chahiye aapko? Life cover? Child plan? Ya bas gyaan? Sab milega! 😂""",

        f"""😊 <b>Hello! Sat Sri Akal! Namaste! Salaam!</b><br><br>
Koi bhi bolo — main samjhunga! Main hoon <b>LIC Mitra</b>, Sarita Pandey ji ka ek smart (thoda funny bhi 😄) Assistant.<br><br>
Insurance ki duniya mein aapka swagat hai — yahan aakar aap pehle se zyada samajhdaar ban jaayenge! 🧠✨""",
    ],

    "about_sarita": [
        f"""👩‍💼 <b>Sarita Pandey ji — Ek Introduction!</b><br><br>
📍 Lucknow, Uttar Pradesh<br>
🗓️ LIC Agent since <b>2014</b> | Code: <b>LIC-2014-SP007</b><br>
🏆 MDRT Qualifier · Star Agent · Top 1% (2023)<br>
✅ IRDAI Certified | 10+ years experience<br>
💬 Hindi & English dono mein expert!<br><br>
Unhone <b>500+</b> families ki financial security ke sapne pure kiye hain. 🤝<br><br>
Ek baat seedhi — <b>Sarita ji sirf policy nahi bechti, rishta banati hain!</b> ❤️""",

        f"""🌟 <b>Sarita Pandey ji ke baare mein jaanna chahte ho?</b><br><br>
10 saal pehle unhone ek simple sapna dekha — <i>"Har family ko financial security milni chahiye."</i><br><br>
Aaj tak unhone <b>1200+ policies</b> sell ki hain aur <b>98% claims</b> successful rahi hain!<br><br>
🏆 Awards: MDRT Qualifier, Star Agent, Top 1% in 2023<br>
📞 Direct bat karo: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a><br><br>
<i>Fan following toh film stars ki hoti hai, par Sarita ji ki client following unse zyada hai! 😂</i>""",
    ],

    "life_insurance": [
        """🛡️ <b>Life Insurance — Kyunki Zindagi Precious Hai!</b><br><br>
<b>Mere pas 3 top plans hain:</b><br><br>
🔹 <b>LIC Tech Term</b> — ₹50 Lakh cover, sirf ₹700-800/month se shuru! Age 18-65.<br>
🔹 <b>Jeevan Anand</b> — Savings + Protection ka best combo! Bonus bhi, cover bhi.<br>
🔹 <b>New Jeevan Labh</b> — Kam premium, zyada faayda. Smart log isko lete hain! 😎<br><br>
Sab plans mein <b>Section 80C tax benefit</b> milta hai — matlab sarkar bhi help karti hai!<br><br>
💡 <i>Life insurance lena likhna nahi — yeh apni family ke liye likha hua pyaar hai!</i>""",

        """💙 <b>Life Insurance — Kyunki "Kal Ki Kya Khabar"!</b><br><br>
Dekho bhai, koi nahi chahta ke kuch bura ho — par smart log hamesha prepare rahte hain! 🧠<br><br>
<b>LIC ke top life plans:</b><br>
✅ Tech Term — ₹1 Crore cover bhi ₹1000/month se kam mein!<br>
✅ Jeevan Anand — Death pe full cover + Maturity pe extra bonus!<br>
✅ New Jeevan Labh — 16 saal ke baad lump sum — bacche ki padhai ka tension khatam!<br><br>
<a href="#contact" style="color:#f5c842">📞 Free quote ke liye click karo</a> — ek call mein poora plan ready!""",
    ],

    "health_insurance": [
        """❤️ <b>Health Insurance — "Hospital Bill se Daro Mat!"</b><br><br>
ICU ka bill dekha hai kabhi? 😅 Ek din ₹20,000+ ho jaata hai!<br>
LIC ki Health Plans se yeh tension khatam:<br><br>
🏥 <b>LIC Arogya Rakshak</b> — Individual + Family cover<br>
🩺 <b>Critical Illness Rider</b> — 15+ serious bimariyon mein direct cash!<br>
👨‍👩‍👧 <b>Family Floater</b> — Ek policy mein poora parivaar cover!<br><br>
Plus <b>Section 80D</b> mein ₹25,000 tak tax bachao! 💰<br><br>
<i>Sehat hai toh business hai — yeh ek experienced CA ne bola tha! 😂</i>""",

        """💊 <b>Health is Wealth — toh wealth protect karo!</b><br><br>
Socho agar kal kuch ho jaaye... hospital bill kaun bharega? <br>
Tension mat lo — <b>LIC Health Plans</b> hain na! 😄<br><br>
👉 Family Floater: Ghar ke sabko ek hi policy mein!<br>
👉 Critical Illness Cover: Cancer, Heart Attack, Stroke — sab cover!<br>
👉 <b>Section 80D:</b> Premium par tax deduction!<br><br>
📞 Sarita ji se baat karo: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a>""",
    ],

    "pension": [
        """🏖️ <b>Pension Plan — Retire in Style!</b><br><br>
Budhape mein "Bete par depend rehna" ka zamana gaya — ab apna khud ka income hoga! 💪<br><br>
<b>Top Pension Plans:</b><br>
🌟 <b>Jeevan Shanti</b> — Ek baar paisa daalo, jeevan bhar monthly income lo! Min ₹1.5 Lakh.<br>
🌟 <b>New Jeevan Nidhi</b> — Life cover + pension dono!<br>
🌟 <b>PM Vaya Vandana Yojana</b> — 60+ ke liye special scheme!<br><br>
💡 <i>Retirement ki planning aaj karo — kal ka chai pakoda stress-free hoga! ☕😂</i><br><br>
<a href="#contact" style="color:#f5c842">Sarita ji se free consultation lo →</a>""",

        """✈️ <b>Retire Rich — Sirf LIC ke saath!</b><br><br>
Dream: Retire ke baad Goa trip, grandchildren ke saath time, tension-free zindagi! 😎<br>
Plan: LIC Pension Plans!<br><br>
💰 <b>Jeevan Shanti</b>: ₹5 Lakh daalo → ₹3,000–4,000/month mil sakta hai jeevan bhar!<br>
📈 <b>Jeevan Nidhi</b>: Market se zyada stable returns, life cover included!<br><br>
Jitna jaldi shuru karo, utna zyada milega — yeh toh maths hai! 🧮<br><br>
📞 Call: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a>""",
    ],

    "child_plan": [
        """👶 <b>Child Plans — Bacche ke Sapne, Aapka Plan!</b><br><br>
IIT, UK padhai, dream wedding — yeh sab expensive hai!<br>
Par Sarita ji ke paas solution hai! 😄<br><br>
🎓 <b>Jeevan Tarun</b> — 0-12 saal tak policy lo, 20-24 saal mein money-back lo! Perfect for education!<br>
💍 <b>Children's Money Back</b> — Periodic payouts for milestones!<br>
🌟 <b>Bima Jyoti</b> — Guaranteed additions + life cover<br><br>
🔐 <b>Waiver of Premium:</b> Agar aapko kuch ho jaaye — premium maafi! Bacche ka future protected!<br><br>
<i>"Bacche ke liye sirf toys mat kharido — unka future bhi kharido!" 😊</i>""",

        """🌱 <b>Bacche ka Kal = Aaj Ki Planning!</b><br><br>
Aaj ₹2000/month invest karo → 18 saal baad ₹8-10 Lakh ready!<br>
Yeh magic nahi — yeh <b>LIC Jeevan Tarun</b> hai! 🎩✨<br><br>
Key Benefits:<br>
✅ Entry age: 0-12 years (nawjaat bacche bhi!)<br>
✅ 20-24 saal ki umra mein money-back milti hai<br>
✅ Section 80C mein tax benefit<br>
✅ Premium Waiver if parent passes away (heart touching feature 💙)<br><br>
📞 Aaj hi Sarita ji se baat karo: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a>""",
    ],

    "ulip_investment": [
        """📈 <b>ULIP — Insurance bhi, Investment bhi! Double Dhamaka!</b><br><br>
Ye kya jadoo hai? 🪄<br>
ULIP = Life Cover + Market Returns = <b>Best of Both Worlds!</b><br><br>
🚀 <b>LIC SIIP</b> — Systematic Investment Insurance Plan<br>
📌 Min ₹40,000/year | Age 18-50 | Term 10-25 years<br>
📌 Market-linked returns (equity + debt funds)<br>
📌 Maturity amount <b>100% tax-free</b> under 10(10D)!<br><br>
<i>Stock market ka thrill + Insurance ka security = Perfect combo! Market down ho ya up — cover toh rahega! 😄</i><br><br>
<a href="#contact" style="color:#f5c842">Free consultation book karo →</a>""",

        """💹 <b>Invest Smart with LIC ULIP!</b><br><br>
Mutual fund mein invest karte ho? Good!<br>
Par kya life cover bhi hai saath mein? 🤔<br><br>
<b>LIC SIIP</b> mein dono milta hai — ek hi plan mein!<br><br>
Why ULIP over regular MF?<br>
✅ Life cover included (family ka suraksha)<br>
✅ Maturity amount tax-free (10(10D))<br>
✅ Government-backed, safe & trusted<br>
✅ Lock-in period ke baad liquidity bhi<br><br>
📞 Smart investor bano: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a>""",
    ],

    "tax_saving": [
        """💼 <b>Tax Bachao — Poora Legal Tarike Se! 😏</b><br><br>
March end mein "Tax kaise bachaaoon?!" stress — who's been there? 🙋<br><br>
LIC ke saath <b>triple tax benefit:</b><br><br>
1️⃣ <b>Section 80C</b> — Premium par ₹1.5 Lakh tak deduction!<br>
2️⃣ <b>Section 10(10D)</b> — Maturity amount <b>ZERO tax!</b> 🎉<br>
3️⃣ <b>Section 80D</b> — Health rider premium par ₹25,000 extra deduction!<br><br>
Total possible saving: <b>₹45,000+ tax annually!</b> 💰<br><br>
<i>CA bhi bolega — "LIC lo bhai!" 😂</i>""",

        """📊 <b>Tax = Stress? LIC = Solution!</b><br><br>
Income ₹10 Lakh hai? Normal tax: ~₹1.12 Lakh<br>
LIC premium invest karo: Tax 50-60% tak kam ho sakti hai! 🤯<br><br>
<b>How?</b><br>
📌 80C: LIC premium — Max ₹1.5 Lakh exemption<br>
📌 80D: Health premium — ₹25,000 more<br>
📌 10(10D): Maturity pe NO TAX at all!<br><br>
Yeh ek investment hai jo protect bhi karta hai aur tax bhi bachata hai! 🌟<br><br>
<a href="#contact" style="color:#f5c842">Sarita ji se free tax planning consultation lo →</a>""",
    ],

    "claim": [
        """📋 <b>LIC Claim — Fast & Tension-Free!</b><br><br>
Darna nahi hai! Sarita ji personally help karti hain claim mein! 🤝<br><br>
<b>Simple 4-step process:</b><br>
1️⃣ Sarita ji ko immediately inform karo: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a><br>
2️⃣ Claim form + policy documents submit karo<br>
3️⃣ LIC verification (generally 7-30 days)<br>
4️⃣ 💰 Amount directly nominee ke account mein!<br><br>
📊 LIC ka claim settlement ratio: <b>98.58%</b> — India mein sabse high!<br><br>
<i>"Mushkil waqt mein Sarita ji ka support — ek call pe!" 🙏</i>""",

        """🏥 <b>Claim karna hai? Fikar mat karo!</b><br><br>
Honestly, claim process log se log zyada darte hain. But reality mein it's simple!<br><br>
Sarita ji ne 100s clients ki claim processing mein help ki hai — <b>ek bhi claim process mein problem nahi aayi!</b> 💪<br><br>
Documents needed:<br>
📄 Original policy bond<br>
📄 Claim form (Sarita ji fill karne mein help karti hain!)<br>
📄 Death certificate / medical papers (as applicable)<br>
📄 Bank passbook copy<br><br>
📞 Call first: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a> — baki sab woh sambhal lengi!""",
    ],

    "contact": [
        f"""📞 <b>Sarita Pandey ji se Milna Hai? Easy!</b><br><br>
📱 <b>WhatsApp:</b> <a href="https://wa.me/917007629909" target="_blank" rel="noopener" style="color:#25d366">Sarita ji se chat karein</a><br>
📧 <b>Email:</b> saritapandey7007629@gmail.com<br>
🏢 <b>Office:</b> Hazratganj Branch, Lucknow, UP – 226001<br>
🕐 <b>Hours:</b> Mon–Sat, 9:30 AM – 6:00 PM<br><br>
Ya <b>Contact Form</b> bhar do — 24 ghante mein call aayega! 📲<br><br>
<i>First consultation bilkul FREE hai — ek cup chai ki bhi zaroorat nahi! 😄☕</i>""",

        f"""🤝 <b>Baat Karte Hain!</b><br><br>
Sarita ji bahut friendly hain — koi bhi sawaal chota ya bada nahi hota unke liye!<br><br>
📱 WhatsApp: <a href="https://wa.me/917007629909" target="_blank" rel="noopener" style="color:#25d366">Sarita ji se chat karein</a> (quick reply guaranteed!)<br>
📧 Email: saritapandey7007629@gmail.com<br>
📍 Location: Hazratganj, Lucknow (Google Maps pe bhi milenge!)<br>
⏰ Office: Mon-Sat, 9:30 AM - 6:00 PM<br><br>
<b>First meeting:</b> Free consultation — no pressure, no sales pitch — sirf clear guidance! 🌟""",
    ],

    "premium": [
        """💰 <b>Premium Kitna Hoga? Sab Depend Karta Hai!</b><br><br>
3 main factors:<br>
📅 <b>Age</b> — Jawan ho = Kam premium (Aaj lo bhai! 😄)<br>
💵 <b>Sum Assured</b> — Jitna cover utna premium<br>
📆 <b>Policy Term</b> — Lamba term = Thoda zyada premium<br><br>
<b>Real examples:</b><br>
🔹 30 saal | ₹1 Crore Term Cover | ~₹700-900/month<br>
🔹 35 saal | ₹50L Jeevan Anand | ~₹4,000-5,000/month<br>
🔹 Pension ₹5L lump sum → ₹3,500/month lifetime!<br><br>
<i>Aur haan — jitni jaldi loge, utna sasta padega! 😉</i><br><br>
📞 Exact quote ke liye: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a>""",
    ],

    "lic_info": [
        """🏛️ <b>LIC — India ka Sabse Trusted Naam!</b><br><br>
Kuch facts jo aapko wow kar dengi:<br><br>
🗓️ Founded: <b>1956</b> — 68+ saal ka experience!<br>
🇮🇳 100% <b>Government of India</b> backed<br>
💰 <b>₹40+ Lakh Crore</b> assets under management<br>
✅ <b>98.58%</b> claim settlement ratio (2022-23)<br>
🏢 <b>2,900+</b> branch offices across India<br>
👥 <b>30 Crore+</b> policyholders!<br><br>
<i>Phir bhi koi "LIC safe nahi hai" bolta hai? 😂 Unhe yeh stats dikha do!</i><br><br>
<b>"Zindagi ke saath bhi, zindagi ke baad bhi"</b> 🌟""",
    ],

    "joke": [
        """😂 <b>Ek Chhota LIC Joke!</b><br><br>
Ek banda LIC agent se mila aur bola:<br>
"Bhai, meri life insurance leni hai. 2 crore ki!"<br><br>
Agent: "Koi baat nahi! Nominee kaun hoga?"<br><br>
Banda: "Meri wife."<br><br>
Agent: "Premium thoda zyada hoga — because <b>insurance company ne bhi unhe dekha hai!</b>" 😅😂<br><br>
<i>Joke aside — seriously, aaj hi apna plan lo. Kabhi late nahi hota!<br>
📞 <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a></i>""",

        """😄 <b>Kal ki tension? Insurance ka tension se zyada?</b><br><br>
Log kal ki fikar karte hain par aaj insurance nahi lete — that's the real joke! 😅<br><br>
But seriously — <b>ek ache LIC plan se:</b><br>
✅ Kal ki chinta khatam<br>
✅ Family secure<br>
✅ Tax bhi bacha<br>
✅ Saving bhi badi<br><br>
Itna sab ek plan mein — Sarita ji ka kya jawab! 🌟<br><br>
<a href="#contact" style="color:#f5c842">Free consultation book karo aaj!</a>""",

        """🎭 <b>Sunta hoon, pareshaan ho?</b><br><br>
"Main insurance agent se milta hoon toh woh policy thoop deta hai!"<br><br>
Yeh Sarita ji ke saath NAHI hoga! 😊<br><br>
Unka style hai:<br>
1. Sunna 👂<br>
2. Samajhna 🧠<br>
3. Sahi plan suggest karna 📋<br>
4. Aapko decide karne dena 🤝<br><br>
<b>No pressure. No jargon. Just honest advice.</b><br><br>
📞 Try karo: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a> — promise, thopa nahi jaayega! 😄""",
    ],

    "thanks": [
        """😊 <b>Shukriya! Bahut Bahut Dhanyawad!</b><br><br>
Aapki madad karna mujhe bahut accha laga! Yeh toh mera kaam hai — aur mujhe pasand bhi hai! 🤖❤️<br><br>
Ek free tip: Aaj hi Sarita ji ko call karo — pehli meeting bilkul FREE hai!<br>
📞 <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a><br><br>
<i>Aur haan — dobaara koi sawaal ho toh main yahaan hoon! LIC Mitra kabhi thakta nahi! 😄</i>""",

        """🌟 <b>Thank you bhi aapko!</b><br><br>
Waise, jo log insurance ke baare mein seriously sochte hain — woh sach mein smart hote hain! 🧠<br><br>
Aap bhi unhi mein se ek hain — isliye <b>Congratulations!</b> 🎉<br><br>
Kuch aur jaanna ho toh pucho — main yahaan hoon!<br>
Ya Sarita ji se seedha baat karo: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a> 📞""",
    ],

    "bye": [
        """👋 <b>Alvida! Take Care!</b><br><br>
Aapka din bahut achha jaaye! ☀️<br><br>
Yaad rakhna — <b>Sarita Pandey ji hamesha available hain:</b><br>
📞 <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a><br><br>
<i>Aur agar kabhi raat ko 2 baje "Mujhe insurance chahiye!" ka khayal aaye — toh subah call karna! 😂 Sarita ji ke office hours hain! 🕘</i>""",

        """🙏 <b>Namaste! Phir Milenge!</b><br><br>
Gaye toh nahi sach mein? 🥺 Theek hai — jaao, par Sarita ji ka number save karna mat bhoolo!<br><br>
📱 <a href="https://wa.me/917007629909" target="_blank" rel="noopener" style="color:#25d366"><b>WhatsApp par chat karein</b></a><br><br>
<b>LIC Mitra always here for you! 🤖💛</b>""",
    ],

    "default": [
        """🤔 <b>Hmm, samjha nahi main!</b><br><br>
Kachhwa bhi thoda tez hota hai mujhse aaj! 🐢😂<br><br>
Par fikar mat karo — ye topics pe puccho, sab pata hai mujhe:<br>
🛡️ "Life insurance" | ❤️ "Health plans"<br>
🏖️ "Pension" | 👶 "Child plan"<br>
💼 "Tax saving" | 📞 "Contact"<br>
💰 "Premium" | 📋 "Claim"<br>
😂 "Joke" (haan, jokes bhi hai!)| 👩‍💼 "About Sarita"<br><br>
Ya seedha baat karo Sarita ji se: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a>""",

        """😅 <b>Yeh meri understanding se thoda bahar hai!</b><br><br>
Main AI hoon — sab nahi jaanta, par yeh jaanta hoon:<br><br>
👩‍💼 Sarita Pandey ji <b>sab kuch jaanti hain!</b><br>
📞 Call: <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a><br>
💬 WhatsApp: <a href="https://wa.me/917007629909" target="_blank" rel="noopener" style="color:#25d366">Sarita ji se chat karein</a><br><br>
Tumhara sawaal unhe bataao — woh ek minute mein clear kar dengi! 🌟""",
    ],
}

# ──────────────────────────────────────────────
# INTENT DETECTION
# ──────────────────────────────────────────────
INTENT_PATTERNS = [
    ("greeting",       r"\b(hi|hello|hii|hey|namaste|namaskar|good\s*morning|good\s*evening|good\s*afternoon|helo|hai|hy|howdy|sup|wassup|salaam|vandemataram|jai hind)\b"),
    ("joke",           r"\b(joke|funny|hasa|mazak|humor|hasao|entertain|boring|timepass|fun)\b"),
    ("about_sarita",   r"\b(sarita|pandey|agent|who are you|introduce|profile|about you|kaun|kon|apke baare|experience|awards|mdrt|irdai)\b"),
    ("life_insurance", r"\b(life\s*insurance|term|jeevan\s*anand|jeevan\s*labh|tech\s*term|whole\s*life|endowment|coverage|cover|sum\s*assured|death\s*benefit|term\s*plan)\b"),
    ("health_insurance",r"\b(health|medical|hospital|critical|mediclaim|family\s*floater|bimari|dawai|doctor|arogya|illness|sick|disease)\b"),
    ("pension",        r"\b(pension|retire|retirement|annuity|jeevan\s*shanti|old\s*age|senior|nidhi|budhapa|60|65)\b"),
    ("child_plan",     r"\b(child|children|baccha|bacche|beti|beta|son|daughter|kid|education|padhai|school|college|wedding|shaadi|tarun)\b"),
    ("ulip_investment",r"\b(ulip|siip|invest|market|equity|mutual\s*fund|wealth|returns|growth|stock|nifty|sensex)\b"),
    ("tax_saving",     r"\b(tax|80c|80d|deduction|save\s*tax|income\s*tax|itr|exemption|section|rebate|tds)\b"),
    ("claim",          r"\b(claim|settle|process|nominee|death\s*claim|accident|hospital\s*claim|how\s*to\s*claim|documents)\b"),
    ("contact",        r"\b(contact|phone|call|whatsapp|email|number|reach|office|address|location|hours|kahan|milna|visit)\b"),
    ("premium",        r"\b(premium|cost|price|kitna|how\s*much|rate|monthly|afford|cheap|expensive|amount|pay)\b"),
    ("lic_info",       r"\b(lic|about\s*lic|insurance\s*company|india|government|safe|secure|trusted|best\s*insurance|why\s*lic)\b"),
    ("thanks",         r"\b(thank|thanks|shukriya|dhanyawad|shukar|bahut\s*accha|great|helpful|amazing|superb|awesome|excellent|wonderful)\b"),
    ("bye",            r"\b(bye|goodbye|alvida|chalta|badme|later|ok\s*bye|see\s*you|take\s*care|farewell|going)\b"),
]

def detect_intent(text: str) -> str:
    text_lower = text.lower().strip()
    for intent, pattern in INTENT_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return intent
    return "default"

def get_response(intent: str) -> str:
    options = RESPONSES.get(intent, RESPONSES["default"])
    return random.choice(options)

def get_time_greeting() -> str:
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning! Subah ki namaskar! 🌅"
    elif 12 <= hour < 17:
        return "Good Afternoon! Dopahar ki namaskar! ☀️"
    elif 17 <= hour < 21:
        return "Good Evening! Shaam ki namaskar! 🌆"
    else:
        return "Good Night! Raat ko insurance ke sapne dekho! 😂🌙"

# ──────────────────────────────────────────────
# API ENDPOINTS
# ──────────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    data    = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Bolo bhai, kya puchna hai? 😄"})

    intent  = detect_intent(message)
    reply   = get_response(intent)

    return jsonify({
        "reply":  reply,
        "intent": intent,
    })

@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint."""
    return jsonify({
        "status":  "online",
        "bot":     "LIC Mitra",
        "agent":   AGENT["name"],
        "time":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "greeting": get_time_greeting(),
    })

@app.route("/", methods=["GET"])
def index():
    return """
    <html><body style="font-family:sans-serif;background:#060810;color:#f8fafc;text-align:center;padding:60px">
    <h1 style="color:#f5c842">🤖 LIC Mitra Chatbot</h1>
    <p>Smart AI Chatbot for Sarita Pandey — LIC Insurance Agent</p>
    <p style="color:#94a3b8">POST to <code style="color:#f5c842">/chat</code> with JSON: <code>{"message": "namaste"}</code></p>
    <p style="color:#10b981">✅ Server is running!</p>
    </body></html>
    """

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print("\n" + "="*55)
    print("  LIC Mitra Chatbot Server Starting...")
    print("  Agent: Sarita Pandey | LIC-2014-SP007")
    print("  URL:   http://localhost:5000")
    print("  Chat:  http://localhost:5000/chat  (POST)")
    print("  Check: http://localhost:5000/health (GET)")
    print("="*55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)

