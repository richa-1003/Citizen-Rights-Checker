

import streamlit as st
import streamlit.components.v1 as components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Citizen Rights Checker",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');

#MainMenu,header,footer,.stDeployButton{visibility:hidden;display:none !important;}
[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none !important;}

html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}

.stApp{
    background:#F7F3ED;
    min-height:100vh;
    position:relative;
    overflow-x:hidden;
}

/* falling symbols canvas sits behind everything */
#falling-canvas{
    position:fixed;
    top:0;left:0;
    width:100%;height:100%;
    pointer-events:none;
    z-index:0;
    opacity:0.45;
}

.block-container{
    padding-top:0 !important;
    max-width:700px !important;
    position:relative;
    z-index:1;
}

/* top bar */
.top-bar{
    background:#2C2416;
    margin:-1rem -1rem 0 -1rem;
    padding:10px 2rem;
    display:flex;
    align-items:center;
    justify-content:space-between;
}
.top-bar-left{
    font-family:'Lora',serif;
    font-size:13px;
    color:#C8A96E;
    letter-spacing:0.12em;
    text-transform:uppercase;
}
.top-bar-right{
    font-size:11px;
    color:rgba(200,169,110,0.5);
    letter-spacing:0.06em;
}

/* hero */
.hero-wrap{
    text-align:center;
    padding:3.5rem 1rem 2.5rem;
}
.hero-seal{
    width:68px;height:68px;
    background:#2C2416;
    border-radius:50%;
    display:inline-flex;
    align-items:center;justify-content:center;
    margin-bottom:1.4rem;
    box-shadow:0 0 0 7px rgba(44,36,22,0.09),0 0 0 14px rgba(44,36,22,0.04);
}
.hero-title{
    font-family:'Lora',serif;
    font-size:2.6rem;font-weight:600;
    color:#1C1610;
    margin:0 0 0.5rem;
    letter-spacing:-0.02em;line-height:1.15;
}
.hero-sub{
    font-size:1rem;color:#6B5C45;
    max-width:460px;margin:0 auto 0.5rem;
    line-height:1.65;font-weight:300;
}
.hero-note{font-size:11px;color:#A89070;letter-spacing:0.04em;}

/* input card */
.input-card{
    background:rgba(253,250,246,0.92);
    border:1px solid rgba(44,36,22,0.12);
    border-radius:16px;
    padding:1.5rem 1.5rem 1rem;
    margin-bottom:1rem;
    box-shadow:0 1px 3px rgba(44,36,22,0.06);
    backdrop-filter:blur(4px);
}
.input-label{
    font-family:'Lora',serif;
    font-size:13px;font-weight:500;
    color:#3D2F1E;margin-bottom:10px;
    display:block;letter-spacing:0.02em;
}
.examples-label{
    font-size:11px;color:#A89070;
    text-transform:uppercase;letter-spacing:0.08em;
    margin:1rem 0 6px;
}

/* buttons */
.stButton > button{
    background:#2C2416 !important;
    color:#C8A96E !important;
    border:1px solid #2C2416 !important;
    border-radius:10px !important;
    padding:0.6rem 1.5rem !important;
    font-family:'DM Sans',sans-serif !important;
    font-size:14px !important;font-weight:500 !important;
    width:100% !important;letter-spacing:0.02em !important;
}
.stButton > button:hover{
    background:#3D3520 !important;
    border-color:#3D3520 !important;
}

/* textarea */
.stTextArea textarea{
    background:#FDFAF6 !important;
    border:1px solid rgba(44,36,22,0.18) !important;
    border-radius:10px !important;
    font-family:'DM Sans',sans-serif !important;
    font-size:14px !important;color:#1C1610 !important;
    padding:12px 14px !important;resize:none !important;
}
.stTextArea textarea:focus{
    border-color:#8B6B3D !important;
    box-shadow:0 0 0 3px rgba(139,107,61,0.12) !important;
}
.stTextArea textarea::placeholder{color:#B09C82 !important;}

/* divider */
.ruler{
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(44,36,22,0.15),transparent);
    margin:1.8rem 0;
}

/* section label */
.section-label{
    font-family:'Lora',serif;
    font-size:11px;font-weight:500;
    color:#8B6B3D;
    text-transform:uppercase;letter-spacing:0.12em;
    margin:1.6rem 0 0.8rem;
}

/* article card */
.article-card{
    background:rgba(253,250,246,0.95);
    border:1px solid rgba(44,36,22,0.12);
    border-left:3px solid #8B6B3D;
    border-radius:0 12px 12px 0;
    padding:1.1rem 1.3rem;
    margin-bottom:0.7rem;
}
.article-num{
    font-size:10px;font-weight:500;
    color:#8B6B3D;text-transform:uppercase;
    letter-spacing:0.1em;margin:0 0 4px;
}
.article-title{
    font-family:'Lora',serif;
    font-size:15px;font-weight:500;
    color:#1C1610;margin:0 0 6px;
}
.article-exp{
    font-size:13px;color:#6B5C45;
    line-height:1.65;margin:0;
}

/* summary box */
.summary-box{
    background:#F0EBE0;
    border:1px solid rgba(139,107,61,0.2);
    border-radius:12px;
    padding:1rem 1.2rem;margin-bottom:0.8rem;
}
.summary-label{
    font-size:10px;font-weight:500;
    color:#8B6B3D;text-transform:uppercase;
    letter-spacing:0.1em;margin:0 0 6px;
}
.summary-text{
    font-size:13px;color:#3D2F1E;
    line-height:1.7;margin:0;
}

/* actions */
.actions-box{
    background:rgba(253,250,246,0.95);
    border:1px solid rgba(44,36,22,0.12);
    border-radius:12px;
    padding:0.4rem 1.2rem;margin-bottom:0.8rem;
}
.action-row{
    display:flex;align-items:flex-start;
    gap:12px;padding:10px 0;
    border-bottom:1px solid rgba(44,36,22,0.07);
    font-size:13px;color:#4A3B28;line-height:1.55;
}
.action-row:last-child{border-bottom:none;}
.action-num{
    background:#2C2416;color:#C8A96E;
    min-width:22px;height:22px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:10px;font-weight:500;flex-shrink:0;
    margin-top:1px;font-family:'Lora',serif;
}

/* remedy */
.remedy-box{
    background:#2C2416;border-radius:12px;
    padding:1.1rem 1.3rem;margin-bottom:0.8rem;
}
.remedy-label{
    font-size:10px;font-weight:500;color:#C8A96E;
    text-transform:uppercase;letter-spacing:0.1em;margin:0 0 6px;
}
.remedy-text{
    font-size:13px;color:#E8D9BC;
    line-height:1.65;margin:0 0 10px;
}
.writ-badge{
    display:inline-block;
    background:rgba(200,169,110,0.15);
    color:#C8A96E;
    border:1px solid rgba(200,169,110,0.3);
    font-size:11px;font-weight:500;
    padding:4px 12px;border-radius:20px;
    letter-spacing:0.04em;
}

/* source */
.source-row{
    display:inline-flex;align-items:center;gap:6px;
    font-size:11px;color:#A89070;
    margin-top:0.8rem;letter-spacing:0.02em;
}

/* disclaimer */
.disclaimer{
    background:rgba(44,36,22,0.04);
    border:1px solid rgba(44,36,22,0.1);
    border-radius:10px;
    padding:0.9rem 1.1rem;margin-top:1.5rem;
    font-size:12px;color:#7A6650;line-height:1.65;
}

/* empty state */
.empty-state{
    text-align:center;padding:3rem 0 2rem;
    color:rgba(44,36,22,0.2);
}
.empty-text{
    font-size:13px;color:#B09C82;
    margin-top:0.8rem;
    font-style:italic;font-family:'Lora',serif;
}

/* error */
.error-box{
    background:#FDF0F0;
    border:1px solid rgba(163,45,45,0.2);
    border-radius:10px;padding:1rem 1.2rem;
    font-size:13px;color:#7A2020;line-height:1.65;
}

/* footer */
.footer{
    text-align:center;padding:2.5rem 0 1rem;
    font-size:11px;color:#B09C82;
    letter-spacing:0.04em;line-height:1.8;
    position:relative;z-index:1;
}
</style>
""", unsafe_allow_html=True)


# ── Load components ────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_components():
    try:
        from src.retriever import retrieve_rights
        from src.generator import generate_analysis
        return retrieve_rights, generate_analysis, None
    except Exception as e:
        return None, None, str(e)

retrieve_rights, generate_analysis, load_error = load_components()


# ── Top bar ────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <span class="top-bar-left">⚖ Citizen Rights Checker</span>
    <span class="top-bar-right">Constitution of India · RAG Powered</span>
</div>
""", unsafe_allow_html=True)


# ── Falling symbols background — CSS only, no JS needed ──
st.markdown("""
<style>
.symbol {
    position: fixed;
    top: -80px;
    color: rgba(139,107,61,0.35);
    font-size: 22px;
    animation: fall linear infinite;
    pointer-events: none;
    z-index: 0;
    user-select: none;
}
@keyframes fall {
    0%   { transform: translateY(0px) rotate(0deg);   opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 0.7; }
    100% { transform: translateY(110vh) rotate(360deg); opacity: 0; }
}
.s0  { left:4%;   animation-duration:9s;  animation-delay:0s;    font-size:18px; }
.s1  { left:10%;  animation-duration:12s; animation-delay:1.5s;  font-size:24px; }
.s2  { left:17%;  animation-duration:8s;  animation-delay:0.8s;  font-size:16px; }
.s3  { left:24%;  animation-duration:14s; animation-delay:3s;    font-size:20px; }
.s4  { left:31%;  animation-duration:10s; animation-delay:0.3s;  font-size:26px; }
.s5  { left:38%;  animation-duration:11s; animation-delay:2.2s;  font-size:18px; }
.s6  { left:45%;  animation-duration:7s;  animation-delay:1s;    font-size:22px; }
.s7  { left:52%;  animation-duration:13s; animation-delay:0.5s;  font-size:16px; }
.s8  { left:59%;  animation-duration:9s;  animation-delay:4s;    font-size:24px; }
.s9  { left:66%;  animation-duration:11s; animation-delay:1.8s;  font-size:20px; }
.s10 { left:73%;  animation-duration:8s;  animation-delay:0.2s;  font-size:18px; }
.s11 { left:80%;  animation-duration:15s; animation-delay:2.5s;  font-size:22px; }
.s12 { left:87%;  animation-duration:10s; animation-delay:3.5s;  font-size:16px; }
.s13 { left:93%;  animation-duration:12s; animation-delay:0.7s;  font-size:26px; }
.s14 { left:7%;   animation-duration:16s; animation-delay:5s;    font-size:20px; }
.s15 { left:20%;  animation-duration:9s;  animation-delay:6s;    font-size:18px; }
.s16 { left:35%;  animation-duration:13s; animation-delay:4.5s;  font-size:22px; }
.s17 { left:50%;  animation-duration:8s;  animation-delay:7s;    font-size:24px; }
.s18 { left:65%;  animation-duration:11s; animation-delay:5.5s;  font-size:16px; }
.s19 { left:78%;  animation-duration:14s; animation-delay:2s;    font-size:20px; }
.s20 { left:90%;  animation-duration:10s; animation-delay:8s;    font-size:18px; }
.s21 { left:13%;  animation-duration:12s; animation-delay:6.5s;  font-size:26px; }
.s22 { left:42%;  animation-duration:9s;  animation-delay:3.8s;  font-size:22px; }
.s23 { left:57%;  animation-duration:15s; animation-delay:1.2s;  font-size:18px; }
</style>

<div class="symbol s0">⚖</div>
<div class="symbol s1">🍁</div>
<div class="symbol s2">§</div>
<div class="symbol s3">⚖</div>
<div class="symbol s4">🍁</div>
<div class="symbol s5">¶</div>
<div class="symbol s6">⚖</div>
<div class="symbol s7">§</div>
<div class="symbol s8">🍁</div>
<div class="symbol s9">⚖</div>
<div class="symbol s10">§</div>
<div class="symbol s11">🍁</div>
<div class="symbol s12">⚖</div>
<div class="symbol s13">§</div>
<div class="symbol s14">🍁</div>
<div class="symbol s15">⚖</div>
<div class="symbol s16">§</div>
<div class="symbol s17">🍁</div>
<div class="symbol s18">⚖</div>
<div class="symbol s19">§</div>
<div class="symbol s20">🍁</div>
<div class="symbol s21">⚖</div>
<div class="symbol s22">§</div>
<div class="symbol s23">🍁</div>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-seal">
        <svg width="34" height="34" viewBox="0 0 34 34" fill="none">
            <path d="M17 4L7 9.5v8C7 24 11.8 30 17 31.5
                     C22.2 30 27 24 27 17.5v-8L17 4z"
                  stroke="#C8A96E" stroke-width="1.5"
                  stroke-linejoin="round" fill="none"/>
            <path d="M12 17.5l3.5 3.5L22 14"
                  stroke="#C8A96E" stroke-width="1.5"
                  stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    <h1 class="hero-title">Citizen Rights Checker</h1>
    <p class="hero-sub">
        Describe your situation in plain language.<br>
        Discover which constitutional rights may protect you and what you can do next.
    </p>
    <p class="hero-note">Grounded in the Constitution of India &nbsp;·&nbsp; Not legal advice</p>
</div>
""", unsafe_allow_html=True)


# ── Error state ────────────────────────────────────────────
if load_error:
    st.markdown(f"""
    <div class="error-box">
        <strong>Startup error:</strong> {load_error}<br><br>
        Common fixes:<br>
        &bull; Run <code>python build_kb.py</code> to build the knowledge base<br>
        &bull; Check that <code>data/constitution_of_india.pdf</code> exists<br>
        &bull; Verify your <code>GROQ_API_KEY</code> in the <code>.env</code> file
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Input section ──────────────────────────────────────────
EXAMPLES = [
    "Police arrested me without telling me why",
    "My employer pays women less than men for same work",
    "I was denied school admission due to my caste",
    "Government demolished my house without any notice",
    "I was tortured while in police custody",
    "My employer won't give me maternity leave",
]

if "situation_text" not in st.session_state:
    st.session_state.situation_text = ""

st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown('<span class="input-label">Describe your situation</span>',
            unsafe_allow_html=True)

situation = st.text_area(
    label="situation",
    value=st.session_state.situation_text,
    placeholder="e.g. My employer refuses to pay me for overtime and threatens to fire me if I complain...",
    height=100,
    label_visibility="collapsed"
)

clicked = st.button("Find My Constitutional Rights →")

st.markdown('<p class="examples-label">Or try an example</p>',
            unsafe_allow_html=True)

cols = st.columns(3)
for i, ex in enumerate(EXAMPLES):
    with cols[i % 3]:
        label = ex[:22] + "…" if len(ex) > 22 else ex
        if st.button(label, key=f"ex_{i}", help=ex):
            st.session_state.situation_text = ex
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ── Analysis ───────────────────────────────────────────────
if clicked:
    if not situation or len(situation.strip()) < 10:
        st.warning("Please describe your situation in a few words.")
        st.stop()

    with st.spinner("Searching the Constitution of India..."):
        try:
            retrieved = retrieve_rights(situation.strip())
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <strong>Retrieval error:</strong> {e}<br>
                Make sure <code>python build_kb.py</code> has been run.
            </div>
            """, unsafe_allow_html=True)
            st.stop()

    with st.spinner("Analyzing your rights with Llama 3.1..."):
        try:
            result = generate_analysis(retrieved)
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <strong>Generation error:</strong> {e}<br>
                Check your <code>GROQ_API_KEY</code> in <code>.env</code>
            </div>
            """, unsafe_allow_html=True)
            st.stop()

    st.markdown('<div class="ruler"></div>', unsafe_allow_html=True)

    # Rights
    rights = result.get("rights_violated", [])
    if rights:
        st.markdown(
            '<p class="section-label">Constitutional provisions that may apply</p>',
            unsafe_allow_html=True)
        for r in rights:
            st.markdown(f"""
            <div class="article-card">
                <p class="article-num">{r.get('article','')}</p>
                <p class="article-title">{r.get('title','')}</p>
                <p class="article-exp">{r.get('explanation','')}</p>
            </div>
            """, unsafe_allow_html=True)

    # Plain explanation
    explanation = result.get("plain_explanation", "")
    if explanation:
        st.markdown('<p class="section-label">What this means for you</p>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="summary-box">
            <p class="summary-label">Plain language summary</p>
            <p class="summary-text">{explanation}</p>
        </div>
        """, unsafe_allow_html=True)

    # What to do
    demands = result.get("what_to_demand", [])
    if demands:
        st.markdown('<p class="section-label">Recommended next steps</p>',
                    unsafe_allow_html=True)
        rows = "".join(f"""
        <div class="action-row">
            <div class="action-num">{i}</div>
            <span>{step}</span>
        </div>""" for i, step in enumerate(demands, 1))
        st.markdown(f'<div class="actions-box">{rows}</div>',
                    unsafe_allow_html=True)

    # Remedy
    remedy = result.get("legal_remedy", "")
    writ = result.get("writ_type", "")
    if remedy:
        st.markdown('<p class="section-label">Legal remedy available</p>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="remedy-box">
            <p class="remedy-label">Constitutional remedy</p>
            <p class="remedy-text">{remedy}</p>
            <span class="writ-badge">⚖ {writ}</span>
        </div>
        """, unsafe_allow_html=True)

    # Source
    pages = sorted({
        item.get("page") for item in retrieved.get("fundamental_rights", [])
        if item.get("page")
    })
    page_str = ", ".join(f"p.{p}" for p in pages) if pages else "multiple pages"
    st.markdown(f"""
    <div class="source-row">
        📄 Source: Constitution of India ({page_str})
    </div>
    """, unsafe_allow_html=True)

    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <strong>Disclaimer:</strong> This tool provides general constitutional
        information grounded in the text of the Constitution of India.
        It is <strong>not legal advice</strong>. Rights under Part III generally
        apply against the State, not private individuals — disputes with private
        parties may be better addressed through civil or tenancy law.
        For your specific situation, contact your nearest
        <strong>District Legal Services Authority (DLSA)</strong> for free legal aid.
    </div>
    """, unsafe_allow_html=True)

elif not clicked:
    st.markdown("""
    <div class="empty-state">
        <svg width="52" height="52" viewBox="0 0 52 52" fill="none"
             stroke="currentColor" stroke-width="1.2">
            <path d="M26 48s18-8 18-22V13L26 6 8 13v13c0 14 18 22 18 22z"/>
            <path d="M19 26l6 6 9-11"/>
        </svg>
        <p class="empty-text">Your rights, clearly explained</p>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ──────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Citizen Rights Checker &nbsp;·&nbsp; Agentic RAG over Constitution of India<br>
    InLegalBERT &nbsp;·&nbsp; Llama 3.1 8B via Groq &nbsp;·&nbsp; ChromaDB
</div>
""", unsafe_allow_html=True)