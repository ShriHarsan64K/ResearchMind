# 🧠 ResearchMind
### AI-Powered Research Assistant — Offline, Private, Free

> *Built by students, for students. No internet. No subscription. No data leaks.*

[![AMD Ryzen AI](https://img.shields.io/badge/AMD-Ryzen%20AI%20NPU-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://www.amd.com/en/processors/ryzen-ai)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LLaMA 3](https://img.shields.io/badge/LLaMA-3%20INT4-7C3AED?style=for-the-badge)](https://ollama.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🔥 What is ResearchMind?

ResearchMind is an **on-device AI research assistant** that helps students and researchers actually *understand* research papers — not just skim them.

Upload a PDF. Get structured insights, knowledge gaps, and "what to research next" — all in under 60 seconds. Everything runs **100% locally** on your laptop using AMD Ryzen AI NPU. No cloud. No API keys. No subscriptions.

---

## 😤 The Problem We're Solving

Every day, millions of students in India sit with a folder full of downloaded PDFs and no idea where to start. The average researcher spends **50%+ of their time** just reading and searching literature — that's not research, that's manual labour.

Existing tools like Elicit and Research Rabbit:
- 💸 Cost $20+/month
- 🌐 Require constant internet
- ☁️ Upload your private research to foreign servers
- 🚫 Are inaccessible to students in Tier 2 & Tier 3 cities

**ResearchMind is free, offline, and private — built for every student, on every laptop, in every corner of India.**

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **PDF Analysis** | Upload any research paper and extract key insights instantly |
| 🎯 **Knowledge Gap Detection** | Find exactly what problems are unsolved and what you can research next |
| 🔑 **Key Contributions** | Extract novelty, methodology, domain, and keywords automatically |
| 💬 **Paper Q&A** | Ask natural language questions — *"What methodology did they use?"* |
| 🔍 **Paper Search** | Search arXiv, Semantic Scholar, CrossRef, and CORE in one place |
| 🗂️ **Research Library** | Build a local vector database of all your papers |
| 🔒 **100% Offline** | Everything runs on your device — zero data sent to any server |

---

## 🏗️ Architecture

```
ResearchMind/
├── app.py                  # Streamlit UI — main entry point
├── utils/
│   ├── ai_engine.py        # LLaMA 3 inference via Ollama
│   ├── pdf_engine.py       # PDF text extraction (PyMuPDF + Tesseract OCR)
│   ├── paper_fetcher.py    # Online paper search (arXiv, S2, CrossRef, CORE)
│   └── vector_store.py     # ChromaDB local vector database
├── data/
│   └── vectordb/           # Your personal research library (local only)
├── requirements.txt
└── .env                    # Environment config (never committed)
```

---

## ⚙️ Hardware Support

ResearchMind runs on **any laptop** via ONNX Runtime:

| Hardware | Status |
|---|---|
| 🔴 AMD Ryzen AI NPU | ✅ Primary target — AMD Slingshot 2026 |
| 🟢 NVIDIA CUDA GPU | ✅ Supported |
| 🔵 Snapdragon X NPU | ✅ Supported |
| ⚪ CPU (any laptop) | ✅ Fallback — works everywhere |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running
- LLaMA 3 model pulled

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/ShriHarsan64K/ResearchMind.git
cd ResearchMind

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull LLaMA 3 model (one-time setup)
ollama pull llama3

# 5. Run the app
streamlit run app.py
```

### Environment Setup

Copy `.env.example` to `.env` and configure:

```env
# No API keys required for core features
# Optional: Add keys for extended paper search
CORE_API_KEY=your_key_here   # optional — CORE works without it too
```

---

## 🧪 Tech Stack

| Layer | Technology |
|---|---|
| **AI Inference** | LLaMA 3 INT4 via Ollama |
| **LLM Orchestration** | LangChain |
| **PDF Processing** | PyMuPDF (fitz) + Tesseract OCR |
| **Embeddings** | all-MiniLM-L6-v2 (HuggingFace, local) |
| **Vector Database** | ChromaDB (local persistent) |
| **UI** | Streamlit |
| **Runtime** | ONNX Runtime (cross-platform NPU/GPU/CPU) |
| **OS** | Windows, Linux |

---

## 📊 Impact

- ⏱️ Reduces paper reading time from **4-5 hours → under 60 seconds**
- 🎓 Targets **1.5 million+** engineering graduates produced in India annually
- 🏙️ First tool designed for **Tier 2 & Tier 3 city students** with no institutional access
- 🔐 Zero privacy risk — unpublished thesis and sensitive research stays **on your device**
- 💰 **Completely free** — no subscriptions, no paywalls, no hidden costs

---

## 🏆 Competition

Built for **AMD Slingshot 2026** by **Team NextStrike**

*Strike Fast. Think Next.*

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

```bash
git checkout -b feature/your-feature
git commit -m "Add: your feature description"
git push origin feature/your-feature
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <strong>Built with ❤️ by Team NextStrike</strong><br>
  AMD Ryzen AI · Slingshot 2026 · 3 Members
</div>
