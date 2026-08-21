# LeaseOwl v2 — Tenancy Agreement Analyzer with Measured Accuracy

**This repository is a solo v2 effort by Richard Chen (Jui Chia), built on
top of the DS5105 group project LeaseOwl (v1), whose five-member team is
credited below. v1 documentation is preserved further down this page.**

## What v2 changes, and why

v1 worked as a demo but had unmeasured judgment and avoidable latency.
v2 is an audit-and-rebuild pass:

- **Deterministic clause segmentation** (`src/leaseowl/segmenter.py`)
  replaces the v1 parser, which sent the whole agreement to an LLM whose
  structured output re-emitted every clause (the largest latency and cost
  item, with silent clause loss as a failure mode). The v2 segmenter
  slices text locally by numbering pattern with a reconciliation report;
  on all seven sample TAs: 100% coverage, zero sequence flags,
  milliseconds instead of minutes. Six unit tests, including the case
  that matters most: a numbering gap can never pass silently.
- **Expert-labeled evaluation ground truth** (`eval/`): 147 verdicts
  (7 TAs x 21 CEA-referenced checklist items, present / deficient /
  missing with clause-level evidence), labeled blind by a single
  annotator using a documented protocol (`eval/LABELING_GUIDE.md`),
  after a pilot round that caught and fixed an annotation-tooling
  defect. The critique engine (RAG1), which had no evaluation in v1,
  will be scored against these labels: missing-clause detection
  precision and recall, flag agreement, false-flag rate.
- **Hygiene**: v1's requirements.txt was UTF-16 encoded (unusable by
  pip) and its checklist CSV carried encoding damage that was being fed
  into LLM prompts; both fixed. Tests and CI added; binary indexes and
  caches removed from tracking. Requires Python 3.10+.

## Measured results

The critique's checklist-detection capability, evaluated against the 147
expert labels (model `gemini-3.6-flash`, one call per item, provider-
agnostic client with record/replay):

- Exact 3-way accuracy 61.2%, Cohen's kappa 0.44 (moderate).
- Recall 96% on real problems; 50 of 52 "missing" requirements caught,
  with zero missing-called-present.
- **The disagreements are the finding, and they expose the evaluation
  schema, not a model defect.** The model reclassified 43 of 64
  expert-"present" items to "deficient". On manual review of all 43, most
  cite a sub-requirement literally named in the checklist text (who pays
  repair excess, HDB approval for subletting, the deposit refund window).
  The expert judged the clause *substantively present*; the model judged
  it *missing a stated sub-element*. A single per-clause verdict cannot
  hold both readings.
- **Sensitivity to rubric:** the same run reads 61.2% / kappa 0.44 under a
  holistic rubric (expert "present" = gold), or 90.5% / kappa 0.84 if the
  model's sub-element "deficient" calls are credited. The 30-point swing
  shows the whole-clause schema, not model capability, dominates the
  score. Neither endpoint is "the" number (crediting the model against
  itself is circular); the true value sits between. Full bracket and
  caveats in `eval/FINDINGS.md`.
- **Design conclusion:** score each checklist item's sub-elements
  independently and attach a priority/severity to each gap (users want
  every issue surfaced, but ranked; enforceability varies). This would
  make model and expert converge and is the motivated next iteration.

Full analysis in `eval/FINDINGS.md`; auto-generated scorecard in
`eval/eval_report.md`. Reproduce every number with
`python eval/run_eval.py --replay` (no API key needed).

We deliberately did not tune the prompt against these labels: that would
fit the model to its own test set. The honest baseline plus the
disagreement analysis is the deliverable.

See `docs/V2_REVIEW.md` for the full code review and user-risk analysis
that drives this roadmap, and `docs/MIGRATION.md` for what changed from v1.

> LeaseOwl analyses tenancy agreements; it does not provide legal
> advice, and its accuracy is exactly what the evaluation measures, no
> more.

---

# v1 documentation (original group project)

# 🏡 LeaseOwl - Know Your Lease
## [AI Tenancy Agreement Analyzer + Chatbot]
### *Your AI legal co-pilot for fair tenancy agreements*

<p align="center">
  <img src="https://raw.githubusercontent.com/chngzhiquan/DS5105-Project/main/Logo.jpeg" alt="LeaseOwl Logo" width="200"/>
</p>

---

## 📘 Project Overview

**LeaseOwl** is an AI-powered tool designed to help tenants and legal professionals **analyze tenancy agreements efficiently.**  
Main functions include:
- Extracts, compares, and evaluates clauses against an ideal template
- Flags ambiguous, missing, or unfair clauses
- Provides context-aware Q&A via an AI chatbot
- Generates professional summary reports
- Help users understand contracts and make confident decisions in **minutes instead of hours.**

---

## 👤 User Persona

**Richard Chen**, a 28-year-old tech professional new to Singapore, faced challenges such as:
- Spending **6+ hours** researching unclear clauses  
- Unexpected **repair and cleaning costs**  
- Missing **“Quiet Enjoyment”** clauses causing disruptions  

**TA Checker** helps users like Richard understand their contracts and sign confidently — in minutes, not hours.

---

## 💡🚀 Key Features

| **Feature**                           | **Description**                                                                                                                                       |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Clause-by-Clause Critique (RAG 1)** | Thoroughly compares each clause in your TA against an “ideal” clause database; provides **risk ratings, feedback, and suggested edits**.              |
| **Fast Whole-Doc Mode**               | Quick compliance check using a **CSV checklist**, ideal for large documents or rapid insights.                                                         |
| **Thorough Clause Coverage**          | Supports **deep, clause-level analysis** with full risk context; goes beyond basic compliance checks.                                                |
| **Risk Highlighting**                 | Flags ambiguous, missing, or potentially unfair clauses; highlights **critical vs. minor issues**.                                                  |
| **Explainable AI**                    | Provides **clear reasoning** and references to model clauses for every flagged issue.                                                                |
| **Context-Aware Chatbot (RAG 2)**     | Ask general or document-specific questions, e.g., “Why was my deposit clause flagged?”; integrates the analysis report for **relevant answers**.     |
| **Automated Report Generation**       | Summarizes **key findings, risks, and suggestions** into professional reports, ready to share or save.                                               |
| **Multi-Language Support**            | Translates TAs automatically into multiple languages: English, Indonesian, Chinese, French, Spanish, German, Thai, Traditional & Simplified Chinese. |

---

## ⚙️ System Architecture

**TA Checker** uses a **dual-RAG** framework for accurate and context-aware analysis

### 🔹 RAG 1: Clause-by-Clause Critique
- **Source:** ./TA_template/ — ideal tenancy PDFs 
- **Process:** Splits uploaded TA into clauses → queries FAISS vector store → returns **detailed clause critique** with risk scores and suggestions.
- **Output:** Generates detailed clause critiques including **risk level**, **feedback**, and **suggested edits**.

### 🔹 RAG 2: Context-Aware Chatbot
- **Source:** `Database Requirements.xlsx` — general legal Q&A & commentary
- **Process:** Vector retrieval + user report context → answers **general and document-specific queries.**
- **Output:** Provides both **general tenancy guidance** and **document-specific clarifications**.

### 🔹 Fast (Whole-Doc) Mode
- **Source:** CSV checklist (`./checklist/checklist.csv`)  
- **Process:** Skips vector retrieval; compares the entire document against the checklist for **high-level compliance.** 

---

## 💻 Tech Stack

| **Layer**                         | **Technology / Libraries**                                                    |
| --------------------------------- | ----------------------------------------------------------------------------- |
| **Frontend**                      | Streamlit                                                                     |
| **Backend & Orchestration**       | LangChain, LangGraph                                                          |
| **LLM Engine**                    | OpenAI (`gpt-4o-mini`), LangChain `ChatOpenAI` wrapper                        |
| **Embeddings**                    | HuggingFace `sentence-transformers/all-MiniLM-L6-v2`, `HuggingFaceEmbeddings` |
| **Vector Store**                  | FAISS (`langchain_community.vectorstores.FAISS`)                              |
| **Document Loaders**              | `PyPDFLoader`, `DirectoryLoader`, `PdfReader` (`pypdf`), `docx`               |
| **Text Handling & Preprocessing** | `pandas`, `numpy`, `textwrap`, `re`, `RecursiveCharacterTextSplitter`         |
| **Prompts & Parsing**             | `ChatPromptTemplate`, `StrOutputParser`                                       |
| **Async / Utilities**             | `asyncio`, `time`, `os`, `dotenv` (`load_dotenv`)                             |
| **Environment & Configuration**   | Python `.env` with `OPENAI_API_KEY`, `pydantic` for structured configs        |
| **Parallelization**               | `RunnableParallel` (LangChain)                                                |
| **Documents & Types**             | `Document`, `TypedDict`, `BaseModel`, `Field`                                 |

---

## 🚀 Setup and Installation

Follow this quick guide to run **TA Checker** locally.

---

### ⚙️ **1. Environment Setup**

**→ Clone the repository**
git clone https://github.com/chngzhiquan/DS5105-Project.git
cd DS5105-Project

**→ Create & activate virtual environment**
- macOS / Linux
python3 -m venv venv
source venv/bin/activate

- Windows
python -m venv venv
.\venv\Scripts\activate

**→ Install dependencies**
pip install -r requirements.txt

### 🧩 **2. Configure Keys & Files**
**→ Add your OpenAI API key**
Create a .env file in the project root:
OPENAI_API_KEY="sk-your-secret-openai-api-key"

**→ Prepare required folders & files**
| **Component**         | **Folder / File**            | **Purpose**              |
| --------------------- | ---------------------------- | ------------------------ |
| RAG 1 (Ideal Clauses) | `./TA_template/`             | Store ideal tenancy PDFs |
| RAG 2 (Chatbot Q&A)   | `Database Requirements.xlsx` | Legal Q&A source         |
| Fast Mode             | `./checklist/checklist.csv`  | Compliance checklist     |

**📁 Folder Structure Example:**
```
project_root/
├── TA_template/
│   ├── ideal_clause_1.pdf
│   └── ideal_clause_2.pdf
├── checklist/
│   └── checklist.csv (For "Fast" mode)
├── Database Requirements.xlsx (For general Q&A RAG 2)
├── main2.py
├── backend_utils_v2.py
└── .env
```

### 🧠 **3. Build Vector Databases**
**→ Run the notebook**
jupyter notebook test_rag.ipynb

**This will create:**
./faiss_index_ideal_clauses/
./faiss_index_general_qa/

*_Run again only if your data updates._*

### ▶️ **4. Run the App**
streamlit run main_v2.py

**❓ FAQ / Troubleshooting**
- **Q:** Streamlit fails to run  
  **A:** Ensure `.env` contains a valid `OPENAI_API_KEY` and all dependencies are installed. Use `pip install -r requirements.txt`.

- **Q:** FAISS index not found  
  **A:** Run `test_rag.ipynb` to rebuild the vector databases before using RAG queries.

- **Q:** Module import errors  
  **A:** Reinstall dependencies using `pip install -r requirements.txt` and ensure your virtual environment is active.

**✅ Using the App**
- Upload your Tenancy Agreement PDF.
- Click Process Document.
- Select analysis engine → RAG 1 (clause-level) or Whole-Doc.
- Click Analyze Contract.
- View your report & chat with the AI Assistant.

**📊 Example Outputs**
- Detailed clause-level critiques with risk ratings
- Summary report highlighting missing/unfair clauses
- Chatbot Q&A referencing both general knowledge and your uploaded TA
- Multi-language TA translations
- Whole-Doc mode JSON & Markdown summaries

**🛠️ Thorough Mode**
- Compares the entire Tenancy Agreement against a **detailed compliance checklist**.
- Automatically **compresses and summarizes large documents** for clarity.
- Returns **structured JSON and multi-language Markdown reports** highlighting missing or non-compliant clauses.

**⚡ Fast Whole-Doc Mode**
- Performs a quick compliance check using a **CSV checklist**.
- Ideal for **large documents or rapid insights**.
- Skips clause-level vector analysis for faster processing.
- Returns **high-level JSON and Markdown reports** highlighting missing or non-compliant clauses.

**🧩 Multi-Language Support**
- Tenancy Agreement can be translated automatically.
- Default languages:  
  ["English", "Indonesian", "Thai", "Traditional Chinese", "Simplified Chinese", "French", "Spanish", "German"]

**📌 Notes**
- Ensure .env has a valid OPENAI_API_KEY.
- FAISS indexes must be built before running RAG queries.
- Thorough mode works independently of RAG indexes.

**💡 Future Enhancements**
- Integration with local legal databases (e.g., CEA Singapore)
- Enhanced visual reports with clause heatmaps
- Improved OCR for scanned PDFs

**⚡ References**  
- LangChain Documentation
- LangGraph Documentation
- FAISS Vector Store  
- OpenAI GPT API
- HuggingFace Embeddings
- Streamlit Documentation
- Pandas / NumPy Documentation
- PyPDF2/ pypdf

**🧠 Credits**  
Developed as part of the DS5105 Project  
Built with ❤️ using Streamlit, LangChain, and OpenAI GPT models

