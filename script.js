/* ══════════════════════════════════════════════════════
   LIC AGENT PORTFOLIO — script.js
   Sarita Pandey | LIC Mitra AI Chatbot + Site Logic
   ══════════════════════════════════════════════════════ */

/* ─── Cursor Glow ─── */
const cursorGlow = document.getElementById('cursor-glow');
document.addEventListener('mousemove', e => {
    cursorGlow.style.left = e.clientX + 'px';
    cursorGlow.style.top = e.clientY + 'px';
});

/* ─── Navbar Scroll ─── */
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
    updateActiveLink();
});

/* ─── Hamburger Menu ─── */
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('nav-links');
hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    navLinks.classList.toggle('mobile-open');
});
navLinks.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        navLinks.classList.remove('mobile-open');
    });
});

/* --- Enquiry Form --- */
const enquiryForm = document.getElementById('enquiry-form');
const formSuccess = document.getElementById('form-success');

if (enquiryForm) {
    enquiryForm.addEventListener('submit', event => {
        event.preventDefault();

        if (!enquiryForm.reportValidity()) return;

        const formData = new FormData(enquiryForm);
        const message = [
            'Namaste Sarita ji,',
            '',
            'I would like to enquire about an LIC plan.',
            `Name: ${formData.get('name')}`,
            `Phone: ${formData.get('phone')}`,
            `Email: ${formData.get('email') || 'Not provided'}`,
            `Interested in: ${formData.get('plan')}`,
            `Message: ${formData.get('message') || 'No additional message'}`,
        ].join('\n');

        formSuccess.classList.add('show');
        window.open(`https://wa.me/917007629909?text=${encodeURIComponent(message)}`, '_blank', 'noopener');
    });
}

/* ─── Active Nav Link ─── */
function updateActiveLink() {
    const sections = document.querySelectorAll('section[id]');
    const scrollY = window.scrollY + 120;
    sections.forEach(sec => {
        const link = document.querySelector(`.nav-link[href="#${sec.id}"]`);
        if (link) link.classList.toggle('active', scrollY >= sec.offsetTop && scrollY < sec.offsetTop + sec.offsetHeight);
    });
}

/* ─── Typewriter Effect ─── */
const phrases = [
    'LIC Insurance Agent',
    'Your Financial Guardian',
    'Certified Insurance Advisor',
    'Life & Health Insurance Expert',
    'Trusted Since 2014',
    'Your Retirement Planning Partner',
];
let phraseIdx = 0, charIdx = 0, isDeleting = false;
const typerEl = document.getElementById('typewriter');

function type() {
    const phrase = phrases[phraseIdx];
    if (!isDeleting) {
        typerEl.textContent = phrase.slice(0, ++charIdx);
        if (charIdx === phrase.length) { isDeleting = true; return setTimeout(type, 2200); }
    } else {
        typerEl.textContent = phrase.slice(0, --charIdx);
        if (charIdx === 0) { isDeleting = false; phraseIdx = (phraseIdx + 1) % phrases.length; }
    }
    setTimeout(type, isDeleting ? 55 : 95);
}
type();

/* ─── Particle Canvas ─── */
const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');
const particles = [];

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

class Particle {
    constructor() { this.reset(); }
    reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * 0.35;
        this.vy = (Math.random() - 0.5) * 0.35;
        this.r = Math.random() * 1.4 + 0.4;
        this.alpha = Math.random() * 0.35 + 0.08;
        const palette = ['201,145,26', '245,200,66', '30,64,175', '96,165,250'];
        this.color = palette[Math.floor(Math.random() * palette.length)];
    }
    update() {
        this.x += this.vx; this.y += this.vy;
        if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) this.reset();
    }
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${this.color},${this.alpha})`;
        ctx.fill();
    }
}

for (let i = 0; i < 90; i++) particles.push(new Particle());

function drawLines() {
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const d = Math.sqrt(dx * dx + dy * dy);
            if (d < 90) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.strokeStyle = `rgba(201,145,26,${0.07 * (1 - d / 90)})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        }
    }
}

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => { p.update(); p.draw(); });
    drawLines();
    requestAnimationFrame(animateParticles);
}
animateParticles();

/* ─── Scroll Reveal ─── */
const revealEls = document.querySelectorAll('.reveal, .reveal-right');
const revealObs = new IntersectionObserver(entries => {
    entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
            setTimeout(() => entry.target.classList.add('visible'), i * 80);
            revealObs.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });
revealEls.forEach(el => revealObs.observe(el));

/* ─── Animated Counter ─── */
const statObs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target;
            const target = parseInt(el.dataset.target);
            const step = target / (1800 / 16);
            let cur = 0;
            const timer = setInterval(() => {
                cur = Math.min(cur + step, target);
                el.textContent = Math.floor(cur);
                if (cur >= target) clearInterval(timer);
            }, 16);
            statObs.unobserve(el);
        }
    });
}, { threshold: 0.5 });
document.querySelectorAll('.stat-number').forEach(el => statObs.observe(el));

/* ─── Plan Filter ─── */
const filterBtns = document.querySelectorAll('.filter-btn');
const planCards = document.querySelectorAll('.plan-card');

filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;
        planCards.forEach(card => {
            const match = filter === 'all' || card.dataset.category === filter;
            card.style.display = match ? 'flex' : 'none';
            if (match) {
                card.style.animation = 'fadeUp 0.4s both';
                setTimeout(() => card.style.animation = '', 500);
            }
        });
    });
});

/* ─── Testimonials Carousel ─── */
const track = document.getElementById('testimonials-track');
const cards = track.querySelectorAll('.testimonial-card');
const dotsWrap = document.getElementById('testi-dots');
const prevBtn = document.getElementById('testi-prev');
const nextBtn = document.getElementById('testi-next');
let current = 0;
const perPage = window.innerWidth < 768 ? 1 : 2;
const total = Math.ceil(cards.length / perPage);

for (let i = 0; i < total; i++) {
    const dot = document.createElement('div');
    dot.className = 'testi-dot' + (i === 0 ? ' active' : '');
    dot.addEventListener('click', () => goTo(i));
    dotsWrap.appendChild(dot);
}

function goTo(idx) {
    current = (idx + total) % total;
    const offset = current * (100 / perPage);
    track.style.transform = `translateX(-${offset}%)`;
    track.style.transition = 'transform 0.5s cubic-bezier(0.4,0,0.2,1)';
    dotsWrap.querySelectorAll('.testi-dot').forEach((d, i) => d.classList.toggle('active', i === current));
    cards.forEach((c, i) => c.classList.toggle('active', Math.floor(i / perPage) === current));
}

prevBtn.addEventListener('click', () => goTo(current - 1));
nextBtn.addEventListener('click', () => goTo(current + 1));

let autoSlide = setInterval(() => goTo(current + 1), 5000);
track.addEventListener('mouseenter', () => clearInterval(autoSlide));
track.addEventListener('mouseleave', () => { autoSlide = setInterval(() => goTo(current + 1), 5000); });

track.style.display = 'flex';
track.style.width = `${(cards.length / perPage) * 100}%`;
cards.forEach(card => { card.style.flex = `0 0 calc(${100 / cards.length}%)`; });
goTo(0);

/* ─── 3D Tilt on Plan / Service Cards ─── */
document.querySelectorAll('.plan-card, .service-card').forEach(card => {
    card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        card.style.transform = `translateY(-6px) perspective(600px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg)`;
    });
    card.addEventListener('mouseleave', () => {
        card.style.transform = '';
        card.style.transition = 'transform 0.5s';
    });
});

/* ══════════════════════════════════════════════════════
   🤖 LIC MITRA AI CHATBOT
   Python Flask backend: http://localhost:5000/chat
   Falls back to local KB if server is offline
   ══════════════════════════════════════════════════════ */

const PYTHON_API = 'http://localhost:5000/chat';
let pythonOnline = false;

async function checkPythonServer() {
    try {
        const res = await fetch('http://localhost:5000/health', { signal: AbortSignal.timeout(2000) });
        if (res.ok) {
            pythonOnline = true;
            console.log('✅ LIC Mitra Python server is ONLINE!');
            const onlineEl = document.querySelector('.chat-online');
            if (onlineEl) onlineEl.innerHTML = '<span class="chat-online-dot"></span> LIC Mitra AI — Online 🤖';
        }
    } catch {
        pythonOnline = false;
        console.log('⚠️ Python server offline — using local fallback.');
    }
}

/* ─── DOM refs ─── */
const chatLauncher = document.getElementById('chatbot-launcher');
const chatWindow = document.getElementById('chatbot-window');
const chatCloseBtn = document.getElementById('chatbot-close');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send');

if (chatLauncher && chatWindow) {
    checkPythonServer();

    chatLauncher.addEventListener('click', () => {
        chatWindow.classList.toggle('open');
        if (chatWindow.classList.contains('open')) {
            chatInput.focus();
            if (!chatWindow.dataset.greeted) {
                chatWindow.dataset.greeted = '1';
                setTimeout(() => {
                    showTyping();
                    setTimeout(() => {
                        removeTyping();
                        const msgs = LOCAL_KB.greeting;
                        addBotMessage(msgs[Math.floor(Math.random() * msgs.length)]);
                    }, 900);
                }, 300);
            }
        }
    });

    chatCloseBtn.addEventListener('click', () => chatWindow.classList.remove('open'));

    document.addEventListener('click', e => {
        if (e.target.classList.contains('qr-btn')) {
            const q = e.target.dataset.q;
            addUserMessage(q);
            showTyping();
            const qrEl = document.getElementById('quick-replies');
            if (qrEl) qrEl.style.display = 'none';
            getBotReply(q);
        }
    });

    chatSendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keydown', e => { if (e.key === 'Enter') sendChatMessage(); });
}

function sendChatMessage() {
    const msg = chatInput.value.trim();
    if (!msg) return;
    addUserMessage(msg);
    chatInput.value = '';
    showTyping();
    getBotReply(msg);
}

async function getBotReply(message) {
    if (pythonOnline) {
        try {
            const res = await fetch(PYTHON_API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
                signal: AbortSignal.timeout(5000),
            });
            if (res.ok) {
                const data = await res.json();
                removeTyping();
                addBotMessage(data.reply);
                return;
            }
        } catch {
            pythonOnline = false;
        }
    }
    setTimeout(() => { removeTyping(); respondLocal(message); }, 700 + Math.random() * 600);
}

/* ─── Local Fallback KB ─── */
const LOCAL_KB = {
    greeting: [
        `🙏 <b>Namaste ji!</b> Main hoon <b>LIC Mitra</b> — Sarita Pandey ji ka smart digital dost! 😄<br><br>
Life Insurance? Health? Pension? Child Plan? Tax saving? Ya sirf ek joke? 😂<br><br>
Bataiye — main ready hoon!`,
        `🤩 Hello! <b>LIC Mitra</b> yahan hai — बिना boring lecture ke, seedha kaam ki baat! 🚀<br><br>
Aaj main aapki kya madad kar sakta hoon?`,
    ],
    about_sarita: [
        `👩‍💼 <b>Sarita Pandey ji:</b><br><br>
📍 Sathiaon, Azamgarh, Uttar Pradesh 276406 | Code: LIC-2014-SP007<br>
🏆 MDRT Qualifier · Star Agent · Top 1% 2023<br>
✅ IRDAI Certified | Since 2014<br>
📊 500+ clients · 1200+ policies · 98% claims settled<br><br>
<i>Ek baat seedhi — Sarita ji sirf policy nahi bechti, rishta banati hain! ❤️</i>`,
    ],
    life_insurance: [
        `🛡️ <b>Life Insurance Plans:</b><br><br>
🔹 <b>LIC Tech Term</b> — ₹50L+ cover, sirf ₹700/month se! Age 18-65<br>
🔹 <b>Jeevan Anand</b> — Savings + Cover + Bonus! Best combo<br>
🔹 <b>New Jeevan Labh</b> — Limited pay, zyada faayda!<br><br>
Sab plans mein <b>80C tax benefit!</b><br>
📞 <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a>`,
    ],
    health_insurance: [
        `❤️ <b>Health Insurance:</b><br><br>
🏥 Arogya Rakshak — Individual + Family cover<br>
🩺 Critical Illness Rider — 15+ serious diseases<br>
👨‍👩‍👧 Family Floater — Ghar ke sabko ek policy!<br><br>
<b>80D</b> mein ₹25,000 tak tax savings! 💰<br><br>
<i>Hospital bill se mat daro — LIC hai na! 😄</i>`,
    ],
    pension: [
        `🏖️ <b>Retire in Style!</b><br><br>
🌟 <b>Jeevan Shanti</b> — Ek baar invest → jeevan bhar income!<br>
🌟 <b>New Jeevan Nidhi</b> — Pension + life cover dono!<br>
🌟 <b>PM Vaya Vandana</b> — Senior 60+ ke liye special!<br><br>
<i>Budhape mein beta nahi — apna plan karega! 😄</i>`,
    ],
    child_plan: [
        `👶 <b>Bacche ke Sapne = Aapka Plan!</b><br><br>
🎓 <b>Jeevan Tarun</b> — Entry 0-12 yr, money-back 20-24 yr!<br>
💍 <b>Children's Money Back</b> — Education + Marriage payouts<br>
🌟 <b>Bima Jyoti</b> — Guaranteed additions + life cover<br><br>
Premium Waiver if parent passes away 💙 — bacche ka future safe!`,
    ],
    ulip: [
        `📈 <b>ULIP — Insurance + Investment! Double Dhamaka!</b><br><br>
<b>LIC SIIP</b> — Market-linked returns + life cover<br>
Min ₹40,000/year | Age 18-50 | Term 10-25 yrs<br><br>
Maturity amount 100% <b>tax-free!</b> 🎉`,
    ],
    tax: [
        `💼 <b>Tax Bachao — Poori Legal tarike se! 😏</b><br><br>
1️⃣ <b>80C</b> — Premium par ₹1.5L deduction<br>
2️⃣ <b>10(10D)</b> — Maturity amount ZERO tax! 🎉<br>
3️⃣ <b>80D</b> — Health rider ₹25,000 extra deduction<br><br>
<i>CA bhi bolega — "LIC lo bhai!" 😂</i>`,
    ],
    claim: [
        `📋 <b>LIC Claim — Fast & Tension-Free!</b><br><br>
1️⃣ Sarita ji ko immediately inform karo<br>
2️⃣ Form + policy bond + documents submit karo<br>
3️⃣ LIC 30 days mein settle karta hai<br>
4️⃣ Amount nominee ke account mein! 💰<br><br>
LIC claim settlement: <b>98.58%</b> — India ka sabse high! 🏆`,
    ],
    contact: [
        `📞 <b>Sarita Pandey ji se milna?</b><br><br>
📱 <a href="https://wa.me/917007629909" target="_blank" rel="noopener" style="color:#25d366">WhatsApp par chat karein</a><br>
📧 saritapandey7007629@gmail.com<br>
🏢 Sathiaon, Azamgarh, Uttar Pradesh 276406<br>
🕐 Mon-Sat: 9:30 AM — 6:00 PM<br><br>
<i>Pehli consultation bilkul FREE! ☕😄</i>`,
    ],
    premium: [
        `💰 <b>Premium kitna hoga?</b><br><br>
Depend karta hai:<br>
📅 Age (jawan = sasta!)<br>
💵 Sum Assured amount<br>
📆 Policy term<br><br>
<b>Example:</b> 30 saal | ₹1 Crore term cover = ~<b>₹700-900/month!</b><br><br>
📞 <a href="tel:+917007629909" style="color:#f5c842">Free quote ke liye call karo!</a>`,
    ],
    joke: [
        `😂 <b>Ek LIC Joke!</b><br><br>
Ek banda agent se mila: "₹2 Crore insurance chahiye!"<br>
Agent: "Nomination kaun hoga?"<br>
Banda: "Wife."<br>
Agent: "Thoda premium zyada hoga — <i>kyunki company ne bhi unhe dekha hai!</i>" 😅<br><br>
<i>Jokes aside — seriously aaj hi lo!<br>
📞 <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a></i>`,
        `😄 <b>Kal ki tension?</b><br><br>
Log kal ki fikar karte hain par insurance nahi lete — that's the real joke! 😅<br><br>
Ek achhe LIC plan se:<br>
✅ Kal ki chinta khatam<br>
✅ Family secure<br>
✅ Tax bhi bacha<br>
✅ Savings bhi badi<br><br>
<a href="#contact" style="color:#f5c842">Free consultation aaj hi book karo! →</a>`,
    ],
    lic: [
        `🏛️ <b>LIC — India ka Sabse Trusted Naam!</b><br><br>
🗓️ Founded 1956 | 68+ saal ka track record!<br>
🇮🇳 100% Government of India backed<br>
💰 ₹40+ Lakh Crore assets managed<br>
✅ 98.58% claim settlement ratio<br>
👥 30 Crore+ policyholders!<br><br>
<i>"Phir bhi koi 'LIC safe nahi' bolta hai? 😂 Unhe yeh stats dikha do!"</i>`,
    ],
    thanks: [
        `😊 <b>Bahut shukriya!</b><br><br>
Aap smart hain — insurance ke baare mein seriously socha! 🧠<br>
Ab ek step aur — Sarita ji se baat karo!<br>📞 <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a> FREE consultation! 🌟`,
    ],
    bye: [
        `👋 <b>Alvida!</b> Seedha baat — Sarita ji ka number save karo!<br><br>
📱 <b>+91 70076 29909</b><br><br>
<i>Raat 2 baje insurance ka khayal aaye toh subah call karna! 😂</i><br>LIC Mitra always here! 🤖💛`,
    ],
    default: [
        `🤔 <b>Hmm, samjha nahi!</b><br><br>
Ye puchho:<br>
🛡️ "life insurance" | ❤️ "health"<br>
🏖️ "pension" | 👶 "child plan"<br>
💼 "tax" | 📞 "contact"<br>
💰 "premium" | 😂 "joke"<br>
👩‍💼 "about sarita" | 🏛️ "about lic"<br><br>
Ya seedha call: 📞 <a href="tel:+917007629909" style="color:#f5c842">+91 70076 29909</a>`,
    ],
};

const LOCAL_PATTERNS = [
    ['greeting', /\b(hi|hello|hii|hey|namaste|namaskar|good\s*(morning|evening|afternoon|night)|hai|hy|salaam)\b/i],
    ['joke', /\b(joke|funny|hasa|mazak|entertain|boring|fun|comedy|hasao)\b/i],
    ['about_sarita', /\b(sarita|pandey|about\s*you|agent|who|introduce|profile|mdrt|experience|awards)\b/i],
    ['life_insurance', /\b(life|term\s*plan|jeevan\s*anand|jeevan\s*labh|tech\s*term|endowment|death\s*cover|sum\s*assured)\b/i],
    ['health_insurance', /\b(health|medical|hospital|critical|mediclaim|family\s*floater|bimari|arogya|disease)\b/i],
    ['pension', /\b(pension|retire|retirement|annuity|jeevan\s*shanti|old\s*age|nidhi|budhapa|senior)\b/i],
    ['child_plan', /\b(child|children|baccha|bacche|kid|son|daughter|education|padhai|tarun|bimajyoti)\b/i],
    ['ulip', /\b(ulip|siip|invest|market|equity|mutual\s*fund|wealth|returns|growth|stock)\b/i],
    ['tax', /\b(tax|80c|80d|deduction|save\s*tax|income\s*tax|itr|exemption|section)\b/i],
    ['claim', /\b(claim|settle|process|nominee|accident|how\s*claim|documents\s*claim)\b/i],
    ['contact', /\b(contact|phone|call|whatsapp|email|reach|office|address|location|hours|milna)\b/i],
    ['premium', /\b(premium|cost|price|kitna|how\s*much|rate|monthly|afford|cheap|expensive)\b/i],
    ['lic', /\b(about\s*lic|lic\s*india|lic\s*history|government\s*insurance|safe\s*investment|trusted)\b/i],
    ['thanks', /\b(thank|thanks|shukriya|dhanyawad|great|helpful|amazing|awesome|excellent|superb)\b/i],
    ['bye', /\b(bye|goodbye|alvida|chalta|later|ok\s*bye|see\s*you|farewell|going)\b/i],
];

function respondLocal(message) {
    const q = message.toLowerCase();
    for (const [intent, pattern] of LOCAL_PATTERNS) {
        if (pattern.test(q)) {
            const options = LOCAL_KB[intent] || LOCAL_KB.default;
            addBotMessage(options[Math.floor(Math.random() * options.length)]);
            return;
        }
    }
    addBotMessage(LOCAL_KB.default[0]);
}

/* ─── Shared Chat Helpers ─── */
function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'chat-msg user';
    div.innerHTML = `<div class="chat-bubble">${escHtml(text)}</div>`;
    chatMessages.appendChild(div);
    scrollChat();
}

function addBotMessage(html) {
    const div = document.createElement('div');
    div.className = 'chat-msg bot';
    div.innerHTML = `<div class="chat-bubble">${html}</div>`;
    chatMessages.appendChild(div);
    scrollChat();
}

function showTyping() {
    const t = document.createElement('div');
    t.className = 'chat-msg bot';
    t.id = 'typing-indicator';
    t.innerHTML = `<div class="chat-typing"><span></span><span></span><span></span></div>`;
    chatMessages.appendChild(t);
    scrollChat();
}
function removeTyping() { const el = document.getElementById('typing-indicator'); if (el) el.remove(); }
function scrollChat() { chatMessages.scrollTop = chatMessages.scrollHeight; }
function escHtml(str) { return str.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
