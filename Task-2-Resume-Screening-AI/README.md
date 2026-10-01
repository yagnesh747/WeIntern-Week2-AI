# WeIntern Pvt Ltd — AI Internship: Week 2
## Task 2: AI-Powered Resume Screening & Candidate Ranking System

A production-ready, lightweight, offline **Resume Screening & Candidate Ranking** application built using **Python, Streamlit, PyPDF2 / pdfplumber, and scikit-learn (TF-IDF + Cosine Similarity)**.

This system empowers recruiters and hiring managers to automatically screen dozens of candidate PDF resumes against any target Job Description (JD), extract contact information, education, experience, and technical skills, rank candidates with transparent similarity scoring, and export formatted reports as CSV.

---

## 🌟 Key Features

1. **Multi-PDF Resume Ingestion**: Supports concurrent batch upload of PDF resumes or loading pre-configured sample candidate profiles with 1 click.
2. **Robust Entity & Text Extraction**:
   - **Candidate Name**: Multi-heuristic detection from header lines or sanitized filenames.
   - **Contact Information**: Regex extraction for email addresses and international/domestic telephone numbers.
   - **Skills Detection**: Boundary-aware keyword matching powered by an extensible `skills.json` taxonomy.
   - **Education**: Automatic degree recognition (B.Tech, M.S., Ph.D., MBA, MCA, BCA, etc.).
   - **Experience**: Detection of explicit tenure mentions (e.g. `5+ years`) and chronological date-range calculations.
3. **TF-IDF + Cosine Similarity Matcher**:
   - Transparent vector space model matching without any paid API dependencies.
   - Calculates candidate match percentages from 0.0% to 100.0%.
4. **Skill Gap Analytics**:
   - Identifies **Matching Skills** (intersection between JD and resume).
   - Flags **Missing Skills** (critical requirements in JD absent from candidate resume).
5. **Leaderboard & Candidate Dashboard**:
   - Interactive ranking table sorted from highest to lowest fit.
   - Expandable candidate deep-dive cards with visual progress bars and color-coded skill chips.
   - Batch analytics (Strong Fits, Potential Matches, Low Matches, and most commonly missing skills across candidate pool).
6. **One-Click CSV Export**:
   - Generates downloadable CSV reports containing full rankings, contact info, matching/missing skills, and credentials.
7. **Comprehensive Error & Edge Case Handling**:
   - Gracefully handles empty job descriptions, scanned image PDFs without selectable text, malformed files, and non-technical resumes.

---

## 🏗️ Architecture & Component Design

```
Resume_Screening_AI/
├── app.py                     # Streamlit interactive web dashboard
├── resume_parser.py           # PDF text extraction & entity parser (Name, Email, Phone, Edu, Exp)
├── matcher.py                 # TF-IDF vectorizer, cosine similarity engine & ranking
├── skill_extractor.py         # Keyword matching, boundary handling & alias normalization
├── skills.json                # Categorized tech skills taxonomy (Languages, Web, DB, ML, Cloud, CS)
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive system documentation
├── sample_data/
│   ├── sample_job_description.txt    # Senior AI/ML Engineer target role
│   └── sample_resumes/               # 5 realistic, pre-generated PDF resumes
│       ├── Alex_Morgan_Senior_AI_Engineer.pdf
│       ├── Priya_Sharma_Data_Scientist.pdf
│       ├── Liam_Chen_FullStack_Developer.pdf
│       ├── Sarah_Jenkins_Junior_Software_Dev.pdf
│       └── David_Miller_Digital_Marketing.pdf
└── tests/
    └── test_screening.py      # Automated unittest suite (10 test cases)
```

---

## 🔬 Mathematical & Algorithmic Foundations

### 1. TF-IDF (Term Frequency – Inverse Document Frequency)
TF-IDF reflects how important a word or n-gram is to a specific document within a collection.

$$\text{TF}(t, d) = \frac{f_{t, d}}{\sum_{t' \in d} f_{t', d}}$$

$$\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$

- **N-gram Range (1, 2)**: Captures both unigrams (`python`, `docker`) and key bigrams (`machine learning`, `deep learning`, `rest api`).
- **Sublinear Term Frequency Scaling**: Replaces $\text{TF}$ with $1 + \ln(\text{TF})$ to prevent frequent buzzwords from dominating the score.
- **Stopwords**: Standard English stopwords are removed to eliminate noise words (`and`, `the`, `is`, `with`).

### 2. Cosine Similarity
Cosine similarity evaluates the orientation angle $\theta$ between the Job Description vector $\mathbf{u}$ and each Candidate Resume vector $\mathbf{v}$:

$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum_{i=1}^{n} u_i v_i}{\sqrt{\sum_{i=1}^{n} u_i^2} \sqrt{\sum_{i=1}^{n} v_i^2}}$$

- **Range**: Normalized between $0.0$ (no overlap) and $1.0$ (identical vocabulary distribution).
- **Match Percentage**: $\text{Match \%} = \text{Cosine Similarity} \times 100$.

### 3. Skill Overlap Rate
Calculates direct overlap between skills required in the Job Description ($S_{\text{JD}}$) and skills present in the Candidate Resume ($S_{\text{Resume}}$):

$$\text{Skill Match Rate} = \frac{|S_{\text{JD}} \cap S_{\text{Resume}}|}{|S_{\text{JD}}|}$$

### 4. Transparent 4-Factor Weighted Match Formula
To prevent single-metric distortion, the final **Match %** is calculated as a multi-factor transparent weighted score with all components normalized to $0 - 100$:

$$\text{Final Match \%} = 0.50 \times \text{Semantic} + 0.35 \times \text{Skills} + 0.10 \times \text{Education} + 0.05 \times \text{Experience}$$

- **50% Semantic / Text Similarity**: TF-IDF cosine similarity between the full JD and candidate resume.
- **35% Required Skill Match**: Ratio of JD technical skills successfully matched in candidate's resume.
- **10% Education Relevance**: Alignment of degree qualifications (e.g. Master's/Ph.D. = 100, B.Tech/B.S. in CS = 85, General degree = 60).
- **5% Experience Relevance**: Candidate professional tenure compared to experience requirements specified in the JD.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.9+ (Python 3.11 recommended)
- `pip` package manager

### 2. Install Dependencies
Navigate into the `Resume_Screening_AI` folder and install the required packages:

```bash
cd "Resume_Screening_AI"
pip install -r requirements.txt
```

---

## 🚀 Running the Application

Launch the Streamlit web application:

```bash
streamlit run app.py
```

The application will launch in your browser at:
`http://localhost:8501`

---

## 🧪 Automated Testing

A complete automated unit testing suite is provided in `tests/test_screening.py`:

```bash
python tests/test_screening.py
```

### Test Coverage:
- `test_load_skills`: Verifies `skills.json` integrity and category loading.
- `test_skill_extraction_standard`: Validates detection of core programming skills.
- `test_skill_extraction_symbols`: Tests boundary handling for `C++`, `C#`, `.NET`, `CI/CD`.
- `test_skill_alias_normalization`: Tests alias mapping (`sklearn` → `Scikit-Learn`, `k8s` → `Kubernetes`).
- `test_compare_skills`: Tests matching, missing, and additional skill separation.
- `test_parse_sample_pdf`: Tests PDF extraction and entity discovery on generated resumes.
- `test_entity_regex_detection`: Verifies name, email, phone, degree, and tenure extraction.
- `test_invalid_file_handling`: Ensures non-existent or corrupted files do not crash the parser.
- `test_matching_and_ranking`: Asserts that an AI Engineer ranks significantly higher than a Marketing applicant for an AI Engineer role.
- `test_empty_job_description`: Asserts proper `ValueError` handling on blank input.

---

## 📊 Sample Test Run & Expected Output

Target Job Description: **Senior AI / Machine Learning Engineer**

| Rank | Candidate Name | Match % | Skill Coverage | Key Matching Skills | Missing Skills | Experience | Education |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| **#1** | **Alex Morgan** | **82.4%** | 88.5% | Python, PyTorch, TensorFlow, NLP, Docker, AWS, FastAPI, Transformers | Neo4j | ~5.0 yrs | MS in CS (Stanford) |
| **#2** | **Priya Sharma** | **68.7%** | 65.4% | Python, Machine Learning, Scikit-Learn, Pandas, SQL, Flask | PyTorch, AWS, Kubernetes | ~3.0 yrs | B.Tech in CSE (NIT) |
| **#3** | **Liam Chen** | **48.2%** | 42.3% | Python, Docker, AWS, Git, REST API | PyTorch, Deep Learning, NLP | ~3.0 yrs | B.S. in Software Eng |
| **#4** | **Sarah Jenkins** | **37.6%** | 30.8% | Python, SQL, Git, Linux, Unit Testing | PyTorch, Docker, Kubernetes, AWS | ~1.0 yr | B.Tech in CS (UT Austin) |
| **#5** | **David Miller** | **14.2%** | 3.8% | Agile | Python, Machine Learning, Docker, SQL, etc. | ~5.0 yrs | MBA in Marketing |

---

## 🛡️ Limitations & Future Improvements

### Limitations
1. **Keyword-Dependent Skills**: While alias-mapped, novel skill abbreviations not present in `skills.json` require periodic additions to the dictionary.
2. **Unstructured Resume Formats**: Extremely creative or graphic-heavy resumes (e.g. multi-layer Photoshop designs exported as flat images) require OCR pre-processing.

### Future Roadmap
1. **Semantic Embeddings**: Integrate local open-source transformer embeddings (e.g. `sentence-transformers/all-MiniLM-L6-v2`) for conceptual semantic similarity.
2. **OCR Integration**: Integrate `pytesseract` to scan flattened images and non-selectable PDFs.
3. **Automated Feedback Generator**: Generate personalized candidate rejection or interview preparation emails based on missing skills.

---

## 💻 Technologies Used

- **UI & Presentation**: [Streamlit](https://streamlit.io/)
- **Machine Learning & NLP**: [scikit-learn](https://scikit-learn.org/), [NumPy](https://numpy.org/), [Pandas](https://pandas.pydata.org/)
- **PDF Extraction**: [pdfplumber](https://github.com/jsvine/pdfplumber), [pypdf](https://pypdf.readthedocs.io/), [PyPDF2](https://pypdf2.readthedocs.io/)
- **Dataset Generation**: [ReportLab](https://www.reportlab.com/)
- **Testing**: Python `unittest`

---

*Developed for WeIntern Pvt Ltd Artificial Intelligence Internship — Week 2 Assignment.*
