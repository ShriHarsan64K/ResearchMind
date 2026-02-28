import streamlit as st
import os, sys, hashlib, tempfile, re, json
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from utils.pdf_engine import process_pdf
from utils.ai_engine import generate_research_brief, answer_question, ask_llama
from utils.vector_store import add_paper, search_papers, get_all_papers, get_paper_by_id, get_paper_count
from utils.paper_fetcher import fetch_all_sources, check_internet, get_search_links

@st.cache_data(ttl=30, show_spinner=False)
def cached_internet_check():
    try:
        import urllib.request
        urllib.request.urlopen("https://arxiv.org", timeout=2)
        return True
    except:
        return False

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="ResearchMind v2", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
*{font-family:'Inter',sans-serif;}
.stApp{background:#0A0A0F;color:#F0F0F5;}
[data-testid="stSidebar"]{background:#0D0D16;border-right:1px solid #1A1A2E;}
.rm-card{background:#13131E;border:1px solid #1E1E2E;border-radius:12px;padding:22px;margin:8px 0;line-height:1.8;}
.rm-red{background:#13131E;border:1px solid #E8001C;border-left:4px solid #E8001C;border-radius:12px;padding:22px;margin:8px 0;line-height:1.8;}
.rm-gold{background:#13131E;border:1px solid #FFB800;border-left:4px solid #FFB800;border-radius:12px;padding:22px;margin:8px 0;line-height:1.8;}
.rm-green{background:#13131E;border:1px solid #00C864;border-left:4px solid #00C864;border-radius:12px;padding:22px;margin:8px 0;line-height:1.8;}
.rm-blue{background:#13131E;border:1px solid #4A9EFF;border-left:4px solid #4A9EFF;border-radius:12px;padding:22px;margin:8px 0;line-height:1.8;}
.metric-box{background:#13131E;border:1px solid #1E1E2E;border-radius:10px;padding:14px;text-align:center;margin:4px 0;}
.metric-num{font-size:1.8rem;font-weight:900;color:#E8001C;}
.metric-lbl{font-size:0.65rem;color:#7A7A9A;letter-spacing:2px;text-transform:uppercase;margin-top:3px;}
.tag{display:inline-block;background:rgba(232,0,28,0.1);border:1px solid rgba(232,0,28,0.3);color:#E8001C;padding:2px 10px;border-radius:20px;font-size:0.73rem;margin:2px;font-weight:500;}
.tag-blue{display:inline-block;background:rgba(74,158,255,0.1);border:1px solid rgba(74,158,255,0.3);color:#4A9EFF;padding:2px 10px;border-radius:20px;font-size:0.73rem;margin:2px;}
.tag-green{display:inline-block;background:rgba(0,200,100,0.1);border:1px solid rgba(0,200,100,0.3);color:#00C864;padding:2px 10px;border-radius:20px;font-size:0.73rem;margin:2px;}
.tag-gold{display:inline-block;background:rgba(255,184,0,0.1);border:1px solid rgba(255,184,0,0.3);color:#FFB800;padding:2px 10px;border-radius:20px;font-size:0.73rem;margin:2px;}
.explain-box{background:rgba(255,184,0,0.05);border:1px solid rgba(255,184,0,0.2);border-radius:10px;padding:13px 17px;font-size:0.84rem;color:#FFD060;margin:8px 0;}
.explain-blue{background:rgba(74,158,255,0.05);border:1px solid rgba(74,158,255,0.2);border-radius:10px;padding:13px 17px;font-size:0.84rem;color:#7AB8FF;margin:8px 0;}
.privacy-badge{background:rgba(0,200,100,0.06);border:1px solid rgba(0,200,100,0.2);border-radius:8px;padding:10px;font-size:0.76rem;color:#00C864;text-align:center;margin-top:10px;}
.online-badge{background:rgba(74,158,255,0.06);border:1px solid rgba(74,158,255,0.2);border-radius:8px;padding:10px;font-size:0.76rem;color:#4A9EFF;text-align:center;margin-top:6px;}
.paper-result{background:#13131E;border:1px solid #1E1E2E;border-radius:10px;padding:16px;margin:8px 0;}
.step-card{background:#13131E;border:1px solid #1E1E2E;border-radius:10px;padding:14px 18px;margin:6px 0;}
.step-num{background:#E8001C;color:#fff;width:26px;height:26px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:0.82rem;margin-right:10px;}
.chat-user{background:#1A1A2E;border-radius:12px 12px 4px 12px;padding:13px 16px;margin:7px 0;text-align:right;}
.chat-ai{background:#13131E;border:1px solid #1E1E2E;border-radius:12px 12px 12px 4px;padding:13px 16px;margin:7px 0;line-height:1.8;}
.difficulty-school{border-color:#00C864!important;}
.difficulty-college{border-color:#FFB800!important;}
.difficulty-research{border-color:#E8001C!important;}
.stButton>button{background:#E8001C!important;color:#fff!important;border:none!important;border-radius:8px!important;font-weight:600!important;width:100%;}
.stButton>button:hover{background:#FF1A33!important;}
h1,h2,h3{color:#F0F0F5!important;}
hr{border-color:#1E1E2E!important;}
#MainMenu,footer,header{visibility:hidden;}
.stTabs [data-baseweb="tab"]{background:#13131E;color:#7A7A9A;border-radius:8px 8px 0 0;}
.stTabs [aria-selected="true"]{background:#E8001C!important;color:#fff!important;}
.stTextInput>div>div>input{background:#13131E!important;border:1px solid #1E1E2E!important;color:#F0F0F5!important;border-radius:8px!important;}
[data-testid="stFileUploader"]{background:#13131E;border:1px dashed #1E1E2E;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "active_tab": "upload",
    "current_paper": None,
    "current_brief": None,
    "current_sections": None,
    "chat_history": [],
    "batch_results": [],
    "difficulty": "College",
    "online": False,
    "fetch_results": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
DIFFICULTY_PROMPTS = {
    "School": "Explain this simply as if talking to a 14-year-old student. Use very simple words, short sentences, and relatable real-life examples. Avoid all technical jargon.",
    "College": "Explain this for a final-year undergraduate or M.Tech student. Be clear and structured. You can use technical terms but explain them briefly.",
    "Research": "Explain this for a PhD researcher or domain expert. Use precise technical language, reference methodologies, and be comprehensive."
}

def simplify_text(text: str, difficulty: str) -> str:
    if difficulty == "College":
        return text
    prompt = f"{DIFFICULTY_PROMPTS[difficulty]}\n\nRewrite this research content accordingly:\n\n{text[:2000]}"
    return ask_llama(prompt)

def generate_export_text(paper, brief):
    return f"""RESEARCHMIND v2.0 — RESEARCH BRIEF
Generated : {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*60}
PAPER     : {paper.get('title','Unknown')}
AUTHOR    : {paper.get('author','Unknown')}
FILE      : {paper.get('filename','Unknown')}
{'='*60}
SUMMARY
{'='*60}
{brief.get('summary','N/A')}

{'='*60}
KEY CONTRIBUTIONS
{'='*60}
{brief.get('contributions','N/A')}

{'='*60}
KNOWLEDGE GAPS & RESEARCH OPPORTUNITIES
{'='*60}
{brief.get('knowledge_gaps','N/A')}

{'='*60}
ResearchMind v2.0 | Team NextStrike | AMD Slingshot 2026
100% Offline · Private · Free | Also works Online
{'='*60}""".strip()

def generate_mindmap_html(papers_data: list) -> str:
    """Generate unified multi-paper mind map."""
    nodes = []
    edges = []
    node_id = 0

    for p_idx, (paper, brief) in enumerate(papers_data):
        title = paper.get('title','Paper')[:35]
        paper_node_id = f"p_{p_idx}"

        # Paper center node
        nodes.append(f"""{{
            id:"{paper_node_id}",
            label:"{title.replace('"',"'")}",
            color:"#E8001C",
            font:{{color:"#fff",size:14,bold:true}},
            shape:"box", margin:10,
            widthConstraint:{{maximum:200}},
            shadow:{{enabled:true,color:"rgba(232,0,28,0.3)",size:10}}
        }}""")

        # Contribution nodes
        def extract_pts(text, n=3):
            lines = re.findall(r'\d+\.\s+\*?\*?([^*\n]{10,55})', text)
            if not lines:
                lines = [l.strip() for l in text.split('\n') if 12 < len(l.strip()) < 60]
            return lines[:n]

        contribs = extract_pts(brief.get('contributions',''), 3)
        for i, c in enumerate(contribs):
            nid = f"c_{p_idx}_{i}"
            label = (c[:30]+"...") if len(c)>30 else c
            nodes.append(f'{{id:"{nid}",label:"{label.replace(chr(34),chr(39))}",color:"#1A3A1A",font:{{color:"#00C864",size:12}},shape:"box",margin:6,widthConstraint:{{maximum:170}}}}')
            edges.append(f'{{from:"{paper_node_id}",to:"{nid}",color:{{color:"#00C864"}},arrows:"to",width:1.5,dashes:false}}')

        gaps = extract_pts(brief.get('knowledge_gaps',''), 3)
        for i, g in enumerate(gaps):
            nid = f"g_{p_idx}_{i}"
            label = (g[:30]+"...") if len(g)>30 else g
            nodes.append(f'{{id:"{nid}",label:"{label.replace(chr(34),chr(39))}",color:"#3A1A1A",font:{{color:"#FF6B6B",size:12}},shape:"box",margin:6,widthConstraint:{{maximum:170}}}}')
            edges.append(f'{{from:"{paper_node_id}",to:"{nid}",color:{{color:"#E8001C"}},arrows:"to",width:1.5,dashes:true}}')

    # Connect papers to each other if multiple
    for i in range(len(papers_data)-1):
        edges.append(f'{{from:"p_{i}",to:"p_{i+1}",color:{{color:"#FFB800"}},arrows:"to",width:2,dashes:false,label:"related"}}')

    return f"""<!DOCTYPE html><html><head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet"/>
<style>
body{{margin:0;background:#0A0A0F;}}
#net{{width:100%;height:550px;}}
#leg{{position:absolute;bottom:10px;left:10px;background:rgba(13,13,22,0.95);
      border:1px solid #1E1E2E;border-radius:8px;padding:10px 14px;font-size:11px;color:#F0F0F5;}}
.l{{display:flex;align-items:center;gap:8px;margin:3px 0;}}
.d{{width:11px;height:11px;border-radius:50%;flex-shrink:0;}}
</style></head><body>
<div id="net"></div>
<div id="leg">
  <div style="font-weight:700;margin-bottom:6px;color:#E8001C;">LEGEND</div>
  <div class="l"><div class="d" style="background:#E8001C"></div>Paper</div>
  <div class="l"><div class="d" style="background:#00C864"></div>Contributions (done)</div>
  <div class="l"><div class="d" style="background:#FF6B6B"></div>Knowledge Gaps (your opportunity)</div>
  <div class="l"><div class="d" style="background:#FFB800;border-radius:2px;width:18px;height:3px;"></div>Paper connections</div>
</div>
<script>
var nodes=new vis.DataSet([{','.join(nodes)}]);
var edges=new vis.DataSet([{','.join(edges)}]);
var net=new vis.Network(document.getElementById("net"),{{nodes,edges}},{{
  physics:{{enabled:true,stabilization:{{iterations:300}},
    barnesHut:{{gravitationalConstant:-4000,springLength:200,springConstant:0.04}}}},
  interaction:{{hover:true,dragNodes:true,zoomView:true,navigationButtons:true}},
  edges:{{smooth:{{type:"cubicBezier"}}}},
  nodes:{{borderWidth:1}}
}});
</script></body></html>"""

def generate_research_questions(papers_data: list) -> str:
    titles = [p.get('title','') for p, _ in papers_data]
    gaps = [b.get('knowledge_gaps','') for _, b in papers_data]
    combined = "\n".join(titles) + "\n\nKnowledge gaps:\n" + "\n".join(gaps[:3])
    prompt = f"""Based on these research papers and their knowledge gaps, generate 5 specific, 
original research questions that a student could pursue as a thesis or project.
Make each question: specific, feasible, and clearly tied to an existing gap.
Format: numbered list with a one-line explanation for each.

Papers and gaps:
{combined[:2500]}"""
    return ask_llama(prompt)

def generate_timeline_html(papers_data: list) -> str:
    items = []
    for paper, brief in papers_data:
        year = paper.get('year', '2024')
        title = paper.get('title','Paper')[:40]
        summary = brief.get('summary','')[:100]
        items.append(f'{{id:{len(items)+1},content:"<b>{title.replace(chr(34),chr(39))}</b><br><small>{summary.replace(chr(34),chr(39))}</small>",start:"{year}-01-01"}}')

    if not items:
        return "<p style='color:#7A7A9A;text-align:center;padding:40px;'>No papers with year data available</p>"

    return f"""<!DOCTYPE html><html><head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet"/>
<style>
body{{margin:0;background:#0A0A0F;color:#F0F0F5;}}
.vis-timeline{{background:#13131E;border:1px solid #1E1E2E;border-radius:8px;}}
.vis-item{{background:#E8001C;border-color:#E8001C;color:#fff;font-size:12px;border-radius:6px;}}
.vis-item.vis-selected{{background:#FF1A33;border-color:#FFB800;}}
.vis-time-axis .vis-text{{color:#7A7A9A;}}
</style></head><body>
<div id="tl" style="height:220px;"></div>
<script>
var items=new vis.DataSet([{','.join(items)}]);
var tl=new vis.Timeline(document.getElementById("tl"),items,{{
  height:"220px",
  zoomMin:1000*60*60*24*365,
  moveable:true,zoomable:true
}});
</script></body></html>"""

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo SVG — abstract neural network
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px;'>
      <svg width="72" height="72" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg">
        <rect width="72" height="72" rx="12" fill="#0A0A0F"/>
        <line x1="10" y1="24" x2="32" y2="18" stroke="#4A9EFF" stroke-width="1.2" opacity="0.6"/>
        <line x1="10" y1="36" x2="32" y2="18" stroke="#4A9EFF" stroke-width="1.2" opacity="0.4"/>
        <line x1="10" y1="48" x2="32" y2="36" stroke="#4A9EFF" stroke-width="1.2" opacity="0.6"/>
        <line x1="10" y1="36" x2="32" y2="54" stroke="#4A9EFF" stroke-width="1.2" opacity="0.4"/>
        <line x1="10" y1="48" x2="32" y2="54" stroke="#4A9EFF" stroke-width="1.2" opacity="0.6"/>
        <line x1="32" y1="18" x2="54" y2="24" stroke="#E8001C" stroke-width="1.5"/>
        <line x1="32" y1="18" x2="54" y2="48" stroke="#E8001C" stroke-width="1" opacity="0.5"/>
        <line x1="32" y1="36" x2="54" y2="24" stroke="#E8001C" stroke-width="1" opacity="0.5"/>
        <line x1="32" y1="36" x2="54" y2="48" stroke="#E8001C" stroke-width="1.5"/>
        <line x1="32" y1="54" x2="54" y2="48" stroke="#E8001C" stroke-width="1.5"/>
        <line x1="54" y1="24" x2="65" y2="36" stroke="#00C864" stroke-width="1.5"/>
        <line x1="54" y1="48" x2="65" y2="36" stroke="#00C864" stroke-width="1.5"/>
        <circle cx="10" cy="24" r="3.5" fill="#4A9EFF"/>
        <circle cx="10" cy="36" r="3.5" fill="#4A9EFF"/>
        <circle cx="10" cy="48" r="3.5" fill="#4A9EFF"/>
        <circle cx="32" cy="18" r="4" fill="#1E1E2E" stroke="#E8001C" stroke-width="1.5"/>
        <circle cx="32" cy="36" r="5" fill="#E8001C"/>
        <circle cx="32" cy="54" r="4" fill="#1E1E2E" stroke="#E8001C" stroke-width="1.5"/>
        <circle cx="54" cy="24" r="4" fill="#1E1E2E" stroke="#FFB800" stroke-width="1.5"/>
        <circle cx="54" cy="48" r="4" fill="#1E1E2E" stroke="#FFB800" stroke-width="1.5"/>
        <circle cx="65" cy="36" r="4.5" fill="#00C864"/>
        <circle cx="32" cy="18" r="2" fill="#E8001C"/>
        <circle cx="32" cy="54" r="2" fill="#E8001C"/>
        <circle cx="54" cy="24" r="2" fill="#FFB800"/>
        <circle cx="54" cy="48" r="2" fill="#FFB800"/>
      </svg>
      <div style='font-size:1.35rem;font-weight:900;letter-spacing:3px;color:#F0F0F5;margin-top:6px;'>
        RESEARCH<span style='color:#E8001C;'>MIND</span>
      </div>
      <div style='font-size:0.6rem;color:#7A7A9A;letter-spacing:4px;'>v2.0 · NEXTSTRIKE · AMD</div>
    </div><hr>
    """, unsafe_allow_html=True)

    # Online/Offline toggle
    internet = cached_internet_check()
    if internet:
        st.markdown("""<div class='online-badge'>🌐 Online Mode Available<br>
        <small>arXiv · Semantic Scholar · CrossRef · CORE</small></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class='privacy-badge'>🔒 Offline Mode<br>
        <small>All features work without internet</small></div>""", unsafe_allow_html=True)

    # Difficulty
    st.markdown("<br>**🎓 Explanation Level**", unsafe_allow_html=True)
    diff = st.select_slider("Explanation Level", options=["School", "College", "Research"],
                            value=st.session_state.difficulty, label_visibility="collapsed")
    st.session_state.difficulty = diff
    diff_colors = {"School": "#00C864", "College": "#FFB800", "Research": "#E8001C"}
    st.markdown(f"""<div style='background:rgba(255,255,255,0.03);border:1px solid {diff_colors[diff]};
    border-radius:6px;padding:8px;font-size:0.78rem;color:{diff_colors[diff]};text-align:center;'>
    {"📚 Simple language for students" if diff=="School" else "🎓 Technical — M.Tech level" if diff=="College" else "🔬 Expert — PhD level"}
    </div>""", unsafe_allow_html=True)

    # Stats
    paper_count = get_paper_count()
    batch_count = len(st.session_state.batch_results)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='metric-box'><div class='metric-num'>{paper_count}</div><div class='metric-lbl'>In Library</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-box'><div class='metric-num'>{batch_count}</div><div class='metric-lbl'>Batch Loaded</div></div>", unsafe_allow_html=True)

    st.markdown("<br>**📌 Navigation**", unsafe_allow_html=True)
    nav = [("upload","📤 Upload & Analyze"), ("batch","📚 Batch Analyze"),
           ("mindmap","🕸️ Mind Map"), ("library","🗂️ My Library"),
           ("search","🔍 Search"), ("online","🌐 Fetch Papers Online"),
           ("questions","💡 Research Questions"), ("timeline","📊 Timeline")]
    for key, label in nav:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.active_tab = key
            st.rerun()

    st.markdown("""<div class='privacy-badge' style='margin-top:10px;'>
    🔒 Offline-first · Zero cloud<br>Your data never leaves your device<br>
    <span style='color:#E8001C;font-weight:700;'>AMD Ryzen AI</span> Optimized<br>
    NVIDIA · Snapdragon · CPU
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD TAB
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == "upload":
    st.markdown("## 📤 Upload & Analyze Research Paper")
    st.markdown(f"""<div class='explain-box'>
    💡 <b>What happens when you upload?</b><br>
    {"ResearchMind reads the paper and explains everything in simple words — like a smart friend who already read it for you. You will understand it even if it is your first research paper!" if st.session_state.difficulty=="School"
    else "LLaMA 3 (running locally on your GPU) extracts the summary, contributions, knowledge gaps, and next research steps in under 60 seconds. 100% offline."
    if st.session_state.difficulty=="College"
    else "Local LLaMA 3 performs structured information extraction: methodology, contributions, gap analysis, and research direction synthesis. All inference on-device via ONNX Runtime."}
    </div>""", unsafe_allow_html=True)

    cols = st.columns(3)
    steps = [("1","Upload PDF","Drop any research paper PDF from your laptop"),
             ("2","AI Reads It","LLaMA 3 understands the paper on your own GPU — no internet"),
             ("3","Get Everything","Summary · Gaps · Contributions · Mind Map · Q&A")]
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""<div class='step-card'>
            <span class='step-num'>{num}</span><b>{title}</b><br>
            <span style='color:#7A7A9A;font-size:0.82rem;'>{desc}</span></div>""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Drop your PDF here", type=["pdf"])

    if uploaded_file:
        st.markdown(f"""<div class='rm-card'>📄 <b>{uploaded_file.name}</b>
        <span class='tag-blue'>{uploaded_file.size//1024} KB</span><span class='tag'>Ready</span></div>""", unsafe_allow_html=True)

        if st.button("🧠 Analyze with AI", use_container_width=True):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            try:
                paper_id = hashlib.md5(uploaded_file.name.encode()).hexdigest()
                existing = get_paper_by_id(paper_id)
                if existing:
                    st.info("Already in library! Loading...")
                    st.session_state.current_paper = {**existing["metadata"], "id": paper_id}
                    st.session_state.active_tab = "results"
                    st.rerun()

                with st.status("Analyzing paper...", expanded=True) as status:
                    st.write("📄 Extracting text...")
                    result = process_pdf(tmp_path)
                    result["metadata"]["filename"] = uploaded_file.name
                    st.write(f"✅ {result['word_count']:,} words extracted")
                    st.write("🧠 LLaMA 3 analyzing...")
                    brief = generate_research_brief(result["metadata"], result["sections"])
                    st.write("✅ Analysis complete")
                    st.write("💾 Saving to library...")
                    add_paper(paper_id, result["metadata"], result["sections"], brief)
                    st.write("✅ Saved!")
                    status.update(label="✅ Done!", state="complete")

                st.session_state.current_paper = {**result["metadata"], "id": paper_id}
                st.session_state.current_brief = brief
                st.session_state.current_sections = result["sections"]
                st.session_state.chat_history = []
                # Add to batch too
                st.session_state.batch_results.append((result["metadata"], brief))
                st.session_state.active_tab = "results"
                st.rerun()
            finally:
                os.unlink(tmp_path)


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS TAB
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "results":
    if not st.session_state.current_brief:
        st.warning("No paper analyzed yet.")
        st.session_state.active_tab = "upload"
        st.rerun()

    brief = st.session_state.current_brief
    paper = st.session_state.current_paper
    diff = st.session_state.difficulty

    st.markdown(f"## 🔬 {paper.get('title','Research Paper')}")
    st.markdown(f"<span class='tag'>👤 {paper.get('author','Unknown')}</span><span class='tag-blue'>📁 {paper.get('filename','')}</span><span class='tag-gold'>🎓 {diff} Mode</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.download_button("📥 Export Research Brief (.txt)", data=generate_export_text(paper, brief),
        file_name=f"ResearchBrief_{paper.get('title','paper')[:25].replace(' ','_')}.txt",
        mime="text/plain", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Summary","🔬 Gaps","⭐ Contributions","🕸️ Mind Map","💬 Ask AI"])

    with tab1:
        st.markdown(f"""<div class='explain-box'>
        {"📋 <b>What did they do?</b> — Think of this like a book report. ResearchMind read the whole paper and wrote the important parts for you!" if diff=="School"
        else "📋 <b>Paper Summary</b> — Core problem, proposed solution, key results and limitations extracted by LLaMA 3." if diff=="College"
        else "📋 <b>Structured Abstract Decomposition</b> — Problem formulation, methodology, empirical results, and limitation analysis."}
        </div>""", unsafe_allow_html=True)
        text = simplify_text(brief.get('summary',''), diff) if diff == "School" else brief.get('summary','')
        st.markdown(f"<div class='rm-card'>{text.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown(f"""<div class='explain-box'>
        {"🔬 <b>What problems are still unsolved?</b> — These are like puzzle pieces still missing. If you solve one, that is YOUR discovery!" if diff=="School"
        else "🔬 <b>Knowledge Gaps</b> — What the paper could NOT solve. These are your research opportunities. Pick one = thesis topic." if diff=="College"
        else "🔬 <b>Epistemological Gaps</b> — Unresolved problem spaces, methodological limitations, and open research vectors identified from the paper."}
        </div>""", unsafe_allow_html=True)
        text = simplify_text(brief.get('knowledge_gaps',''), diff) if diff == "School" else brief.get('knowledge_gaps','')
        st.markdown(f"<div class='rm-red'>{text.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)
        st.markdown("""<div style='background:rgba(232,0,28,0.05);border-radius:8px;padding:12px;font-size:0.82rem;color:#B0B0C8;'>
        💡 <b>Tip:</b> Pick any "Future Work" point above as your research topic. You already have a reference paper and a defined gap. That is 80% of a thesis proposal done.
        </div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown(f"""<div class='explain-box'>
        {"⭐ <b>What cool new things did they make?</b> — These are the new ideas this paper added to science. Nobody had done this before!" if diff=="School"
        else "⭐ <b>Key Contributions</b> — What is genuinely new in this paper. Understand this before you build on it." if diff=="College"
        else "⭐ <b>Novel Contributions</b> — Original methodological, theoretical, or empirical contributions with technical approach and domain taxonomy."}
        </div>""", unsafe_allow_html=True)
        text = simplify_text(brief.get('contributions',''), diff) if diff == "School" else brief.get('contributions','')
        st.markdown(f"<div class='rm-gold'>{text.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("""<div class='explain-box'>
        🕸️ <b>Knowledge Mind Map</b> — Visual graph of this paper.
        <span style='color:#00C864;'>Green</span> = contributions (already solved).
        <span style='color:#FF6B6B;'>Red</span> = knowledge gaps (your opportunity).
        Drag · Zoom · Explore.
        </div>""", unsafe_allow_html=True)
        st.components.v1.html(generate_mindmap_html([(paper, brief)]), height=520, scrolling=False)

    with tab5:
        st.markdown(f"""<div class='explain-box'>
        {"💬 <b>Ask anything!</b> — Like texting a friend who read the whole paper. Ask in normal words!" if diff=="School"
        else "💬 <b>Ask AI</b> — LLaMA 3 answers from the paper. Runs on your GPU. Nothing leaves your device." if diff=="College"
        else "💬 <b>Contextual Q&A</b> — RAG-based retrieval from paper content via local LLaMA 3 inference."}
        </div>""", unsafe_allow_html=True)

        suggested = ["What dataset did they use?","What are the limitations?","How does it work?","What results did they get?"]
        cols = st.columns(4)
        for i, q in enumerate(suggested):
            with cols[i]:
                if st.button(q, key=f"sq_{i}"):
                    st.session_state._sq = q
                    st.rerun()

        for msg in st.session_state.chat_history:
            cls = "chat-user" if msg["role"]=="user" else "chat-ai"
            icon = "🙋" if msg["role"]=="user" else "🧠"
            st.markdown(f"<div class='{cls}'>{icon} {msg['content'].replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

        question = st.text_input("Your question:", value=getattr(st.session_state,'_sq',''), placeholder="Ask anything about this paper...")
        if st.button("Ask AI 🧠"):
            if question.strip():
                with st.spinner("Thinking..."):
                    answer = answer_question(question, st.session_state.current_sections or {})
                st.session_state.chat_history.extend([{"role":"user","content":question},{"role":"assistant","content":answer}])
                if hasattr(st.session_state,'_sq'): del st.session_state._sq
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📤 Another Paper"): st.session_state.active_tab="upload"; st.session_state.current_brief=None; st.rerun()
    with c2:
        if st.button("🕸️ Full Mind Map"): st.session_state.active_tab="mindmap"; st.rerun()
    with c3:
        if st.button("💡 Generate Research Questions"): st.session_state.active_tab="questions"; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# BATCH ANALYZE TAB
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "batch":
    st.markdown("## 📚 Batch Analyze Multiple Papers")
    st.markdown("""<div class='explain-box'>
    📚 <b>Batch Mode</b> — Upload 5 to 15 papers at once. ResearchMind analyzes all of them simultaneously
    and combines everything into one unified Mind Map showing how all papers connect, what is already solved,
    and where the biggest research gaps are across your entire paper collection.
    </div>""", unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Upload 5–15 research papers", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        count = len(uploaded_files)
        color = "#00C864" if 5 <= count <= 15 else "#FFB800"
        st.markdown(f"""<div class='rm-card'>
        <span class='tag' style='color:{color};border-color:{color};background:rgba(0,200,100,0.1);'>
        {count} papers selected</span>
        {"✅ Perfect batch size!" if 5<=count<=15 else "⚠️ Recommended: 5–15 papers for best results"}
        <br><br>{"<br>".join([f"📄 {f.name} <span class='tag-blue'>{f.size//1024}KB</span>" for f in uploaded_files])}
        </div>""", unsafe_allow_html=True)

        if st.button(f"🧠 Analyze All {count} Papers", use_container_width=True):
            st.session_state.batch_results = []
            progress = st.progress(0, text="Starting batch analysis...")

            for idx, uploaded_file in enumerate(uploaded_files):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                try:
                    progress.progress((idx) / count, text=f"📄 Analyzing {idx+1}/{count}: {uploaded_file.name[:40]}...")
                    paper_id = hashlib.md5(uploaded_file.name.encode()).hexdigest()

                    existing = get_paper_by_id(paper_id)
                    if existing:
                        st.session_state.batch_results.append((existing["metadata"], {
                            "summary": existing["metadata"].get("summary",""),
                            "knowledge_gaps": existing["metadata"].get("gaps",""),
                            "contributions": ""
                        }))
                        continue

                    result = process_pdf(tmp_path)
                    result["metadata"]["filename"] = uploaded_file.name
                    brief = generate_research_brief(result["metadata"], result["sections"])
                    add_paper(paper_id, result["metadata"], result["sections"], brief)
                    st.session_state.batch_results.append((result["metadata"], brief))
                finally:
                    os.unlink(tmp_path)

            progress.progress(1.0, text=f"✅ All {count} papers analyzed!")
            st.success(f"🎉 Done! {count} papers analyzed. Go to Mind Map to see the unified view.")

    if st.session_state.batch_results:
        st.markdown(f"<br>**{len(st.session_state.batch_results)} papers ready** — <span class='tag-green'>Batch loaded</span>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🕸️ View Unified Mind Map"): st.session_state.active_tab="mindmap"; st.rerun()
        with c2:
            if st.button("💡 Generate Research Questions"): st.session_state.active_tab="questions"; st.rerun()
        with c3:
            if st.button("📊 View Timeline"): st.session_state.active_tab="timeline"; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MIND MAP TAB
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "mindmap":
    st.markdown("## 🕸️ Unified Research Knowledge Map")
    diff = st.session_state.difficulty
    st.markdown(f"""<div class='explain-box'>
    {"🕸️ <b>Research Map</b> — Imagine each paper is a city and this map shows roads between them. Green roads = things scientists already built. Red roads = empty spaces where YOU can build something new!" if diff=="School"
    else "🕸️ <b>Knowledge Mind Map</b> — Multi-paper concept graph. Green = contributions. Red dashes = knowledge gaps. Yellow = inter-paper connections. Drag · Zoom · Explore." if diff=="College"
    else "🕸️ <b>Multi-Paper Knowledge Graph</b> — Semantic relationship visualization across paper corpus. Node clusters represent contribution boundaries and epistemological gap spaces."}
    </div>""", unsafe_allow_html=True)

    papers_data = st.session_state.batch_results
    if not papers_data and st.session_state.current_brief:
        papers_data = [(st.session_state.current_paper, st.session_state.current_brief)]

    if not papers_data:
        st.markdown("""<div class='rm-card' style='text-align:center;padding:40px;'>
        <div style='font-size:2.5rem;'>🕸️</div>
        <div style='color:#7A7A9A;margin-top:10px;'>Upload papers first to generate the mind map</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='tag-green'>{len(papers_data)} papers</span> <span class='tag'>in map</span><br>", unsafe_allow_html=True)
        st.markdown("<p style='color:#7A7A9A;font-size:0.83rem;'>🖱️ Drag nodes · Scroll to zoom · Click to explore</p>", unsafe_allow_html=True)
        st.components.v1.html(generate_mindmap_html(papers_data), height=580, scrolling=False)

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-box'><div class='metric-num'>{len(papers_data)}</div><div class='metric-lbl'>Papers Mapped</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-box'><div class='metric-num' style='color:#00C864;'>✓</div><div class='metric-lbl'>Contributions</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-box'><div class='metric-num' style='color:#FF6B6B;'>!</div><div class='metric-lbl'>Research Gaps</div></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LIBRARY TAB
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "library":
    st.markdown("## 🗂️ My Research Library")
    st.markdown("""<div class='explain-box'>
    📚 Every paper you analyze is saved here privately on your device. Your library grows smarter over time.
    </div>""", unsafe_allow_html=True)

    papers = get_all_papers()
    if not papers:
        st.markdown("""<div class='rm-card' style='text-align:center;padding:40px;'>
        <div style='font-size:2.5rem;'>📭</div>
        <div style='color:#7A7A9A;margin-top:10px;'>Upload your first paper to start building your library</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='tag'>{len(papers)} papers</span><br><br>", unsafe_allow_html=True)
        for p in papers:
            meta = p["metadata"]
            c1, c2 = st.columns([5,1])
            with c1:
                st.markdown(f"""<div class='paper-result'>
                <b>📄 {meta.get('title','Unknown')}</b><br>
                <span class='tag'>👤 {meta.get('author','Unknown')}</span>
                <span class='tag-blue'>📅 {meta.get('added_date','')[:10]}</span><br>
                <span style='color:#9090A8;font-size:0.83rem;'>{meta.get('summary','')[:180]}...</span>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("View", key=f"v_{p['id']}"):
                    st.session_state.current_paper = {**meta, "id": p["id"]}
                    st.session_state.current_brief = {"summary":meta.get("summary",""),"knowledge_gaps":meta.get("gaps",""),"contributions":""}
                    st.session_state.current_sections = {}
                    st.session_state.active_tab = "results"
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH TAB
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "search":
    st.markdown("## 🔍 Search Your Library")
    st.markdown("""<div class='explain-box'>
    🔍 <b>Semantic AI Search</b> — Searches by meaning, not just keywords. "image recognition" also finds "visual classification". All local, zero internet needed.
    </div>""", unsafe_allow_html=True)
    query = st.text_input("Search:", placeholder="e.g. deep learning medical imaging")
    if st.button("🔍 Search", use_container_width=True):
        if query.strip():
            with st.spinner("Searching..."):
                results = search_papers(query, 5)
            if results:
                for r in results:
                    meta = r["metadata"]
                    pct = round((1-r["distance"])*100, 1)
                    st.markdown(f"""<div class='paper-result'>
                    <b>📄 {meta.get('title','Unknown')}</b>
                    <span class='tag-gold'>🎯 {pct}% match</span><br>
                    <span class='tag'>👤 {meta.get('author','Unknown')}</span><br>
                    <span style='color:#9090A8;font-size:0.83rem;'>{meta.get('summary','')[:180]}...</span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No papers found. Try different keywords.")


# ══════════════════════════════════════════════════════════════════════════════
# ONLINE FETCH TAB
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "online":
    st.markdown("## 🌐 Fetch Papers Online")
    internet = cached_internet_check()

    if not internet:
        st.markdown("""<div class='rm-red'>
        ❌ <b>No internet connection detected.</b><br>
        ResearchMind works fully offline. Connect to internet to use this feature.
        All other features work without internet.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class='explain-blue'>
        🌐 <b>Online Paper Search</b> — Search across multiple academic databases simultaneously.
        Free sources: <b>arXiv, Semantic Scholar, CrossRef, CORE</b> (direct results).<br>
        Paywalled sources: <b>IEEE, ResearchGate, Science Direct, Google Scholar, PubMed, Springer</b> (direct search links).
        </div>""", unsafe_allow_html=True)

        query = st.text_input("Search for papers:", placeholder="e.g. transformer attention mechanism NLP")

        if st.button("🔍 Search All Sources", use_container_width=True):
            if query.strip():
                with st.spinner("Searching arXiv, Semantic Scholar, CrossRef, CORE..."):
                    st.session_state.fetch_results = fetch_all_sources(query)

        if st.session_state.fetch_results:
            res = st.session_state.fetch_results
            st.markdown(f"**Found {res.get('total_found',0)} papers** across all free sources", unsafe_allow_html=True)

            tab_arxiv, tab_ss, tab_cr, tab_core, tab_links = st.tabs([
                "📄 arXiv", "🔵 Semantic Scholar", "🟠 CrossRef", "🟢 CORE (Open)", "🔗 More Sources"
            ])

            for tab, key, color in [(tab_arxiv,"arxiv","#B31B1B"),(tab_ss,"semantic_scholar","#1857B6"),(tab_cr,"crossref","#FF6B00"),(tab_core,"core","#00A86B")]:
                with tab:
                    papers = [p for p in res.get(key,[]) if "error" not in p]
                    if not papers:
                        st.info("No results from this source.")
                    for p in papers:
                        oa = "<span class='tag-green'>Open Access</span>" if p.get("open_access") else "<span class='tag'>Paywall</span>"
                        st.markdown(f"""<div class='paper-result'>
                        <b>{p.get('title','Unknown')}</b> {oa}<br>
                        <span class='tag'>👤 {p.get('authors','Unknown')}</span>
                        <span class='tag-blue'>📅 {p.get('year','N/A')}</span>
                        <span style='background:rgba(255,255,255,0.05);border-radius:4px;padding:2px 8px;font-size:0.72rem;color:{color};'>{p.get('source','')}</span><br>
                        <span style='color:#9090A8;font-size:0.83rem;margin-top:6px;display:block;'>{p.get('abstract','')[:280]}...</span>
                        {"<a href='"+p['link']+"' target='_blank' style='color:#4A9EFF;font-size:0.8rem;'>📎 View Paper →</a>" if p.get('link') else ''}
                        </div>""", unsafe_allow_html=True)

            with tab_links:
                st.markdown("""<div class='explain-box'>
                🔗 These sources require login or institutional access. Click to search directly on their websites.
                </div>""", unsafe_allow_html=True)
                links = res.get("search_links", [])
                c1, c2 = st.columns(2)
                for i, link in enumerate(links):
                    col = c1 if i % 2 == 0 else c2
                    with col:
                        st.markdown(f"""<div class='paper-result' style='border-color:{link['color']};'>
                        <b style='color:{link['color']};'>{link['name']}</b><br>
                        <span style='color:#7A7A9A;font-size:0.8rem;'>{link['note']}</span><br>
                        <a href='{link['url']}' target='_blank' style='color:{link['color']};font-size:0.82rem;'>🔍 Search on {link['name']} →</a>
                        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTIONS TAB
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "questions":
    st.markdown("## 💡 Auto Research Question Generator")
    diff = st.session_state.difficulty
    st.markdown(f"""<div class='explain-box'>
    {"💡 <b>What is this?</b> — ResearchMind reads all your papers and suggests 5 questions YOU could answer with your own research. These are real research ideas nobody has solved yet!" if diff=="School"
    else "💡 <b>Research Question Generator</b> — AI analyzes all your papers, finds the biggest gaps, and generates 5 specific thesis/project topics you can pursue." if diff=="College"
    else "💡 <b>Automated Research Gap Synthesis</b> — Cross-paper gap analysis generates tractable research hypotheses with methodological grounding."}
    </div>""", unsafe_allow_html=True)

    papers_data = st.session_state.batch_results
    if not papers_data and st.session_state.current_brief:
        papers_data = [(st.session_state.current_paper, st.session_state.current_brief)]

    if not papers_data:
        st.info("Analyze at least one paper first.")
    else:
        st.markdown(f"<span class='tag-green'>{len(papers_data)} papers</span> loaded for analysis<br>", unsafe_allow_html=True)
        if st.button("🧠 Generate 5 Research Questions", use_container_width=True):
            with st.spinner("AI is analyzing all papers and finding your research opportunities..."):
                questions = generate_research_questions(papers_data)
            st.session_state._research_questions = questions

        if hasattr(st.session_state, '_research_questions'):
            st.markdown("### 🎯 Your Research Opportunities:")
            st.markdown(f"<div class='rm-green'>{st.session_state._research_questions.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)
            st.download_button("📥 Save Research Questions",
                data=st.session_state._research_questions,
                file_name="ResearchQuestions_NextStrike.txt",
                mime="text/plain", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TIMELINE TAB
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "timeline":
    st.markdown("## 📊 Research Timeline")
    st.markdown("""<div class='explain-box'>
    📊 <b>Research Timeline</b> — See how research in your area evolved over time.
    Each card on the timeline is a paper you analyzed. Drag to scroll through years. See what was discovered when.
    </div>""", unsafe_allow_html=True)

    papers_data = st.session_state.batch_results
    if not papers_data and st.session_state.current_brief:
        papers_data = [(st.session_state.current_paper, st.session_state.current_brief)]

    if not papers_data:
        st.info("Analyze papers first to see the timeline.")
    else:
        # Add year to papers data
        tl_data = []
        for paper, brief in papers_data:
            year = paper.get('year','2024')
            if not year or year == 'N/A':
                year = '2023'
            tl_data.append((dict(paper, year=year), brief))

        st.components.v1.html(generate_timeline_html(tl_data), height=260, scrolling=False)
        st.markdown("<br>", unsafe_allow_html=True)

        for paper, brief in tl_data:
            st.markdown(f"""<div class='paper-result'>
            <span class='tag'>{paper.get('year','N/A')}</span>
            <b> {paper.get('title','Unknown')[:60]}</b><br>
            <span style='color:#9090A8;font-size:0.83rem;'>{brief.get('summary','')[:150]}...</span>
            </div>""", unsafe_allow_html=True)