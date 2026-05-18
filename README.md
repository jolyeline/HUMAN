# HUMAN Project — Part 1
This repository contains the scripts, workflows, and documentation for Part 1 of the **HUMAN** project.

---

## 📌 Overview
This project analyses public discourse around *artificial intelligence* in various Dutch communication outlets.  
The aim is (among others) to identify:

- How often AI is referenced
- In which narrative and discourse contexts
- By which actors (political, media, institutional, etc.)
- And how these patterns change over time

A **mixed-methods** approach is used, combining quantitative text analysis (e.g., keyword classification, topic modeling) with qualitative interpretation.

---

## 📂 Repository Structure

This repository contains scripts and datasets for collecting, parsing, classifying, annotating, and analysing text from multiple data sources. Each source follows a consistent structure with separate directories for data and scripts.

---

### 📰 news
Jupyter notebooks for parsing, classifying, annotating, and analysing news articles.

| Notebook | Description |
|---|---|
| `01_pdf_parser.ipynb` | Parse news PDFs into structured DataFrames |
| `01_pdf_single_file_parser.ipynb` | Single-file variant of the PDF parser |
| `02a_article_classifier_with_working_regex.ipynb` | Keyword-based AI relevance classification |
| `02b_annotating.ipynb` | Manual annotation workflow |
| `02c_inspect_topics.ipynb` | Inspect topic model output |
| `02d_map_topics.ipynb` | Map and label topic clusters |
| `03_filter_noise.ipynb` | Filter irrelevant matches and noise |

#### 📊 news/analysis
Further analyses on the classified news corpus.

| Notebook | Description |
|---|---|
| `01_analyses_prelim.ipynb` | Preliminary corpus statistics and frequency analysis |
| `02_NER.ipynb` | Named Entity Recognition on AI-relevant articles |
| `03_w2v_time.ipynb` | Word2Vec embeddings over time |
| `04_company_inspection.ipynb` | Company-level entity inspection |

---

### 🗳️ elections
Jupyter notebooks for parsing and analysing Dutch party manifestos and election materials.

| Notebook | Description |
|---|---|
| `pdf_parser_from_csv.ipynb` | Parse manifesto PDFs listed in a CSV |
| `dublin_to_json.ipynb` | Convert Dublin-format files to JSON |
| `parse_jsons.ipynb` | Parse and clean JSON election documents |
| `02_article_classifier_party_progams.ipynb` | AI relevance classification of party programs |
| `03_party_programs_analysis.ipynb` | Analysis of AI references in party programs |

---

### 🏛️ tweede_kamer
Jupyter notebooks for parsing and analysing Dutch parliamentary proceedings (Tweede Kamer).

| Notebook | Description |
|---|---|
| `01_parsing_tweede_kamer_api.ipynb` | Retrieve and parse debates via the Tweede Kamer API |
| `02_combining+cleaning.ipynb` | Combine and clean parsed debate datasets |
| `03_analysis.ipynb` | Analysis of AI references in parliamentary debates |
| `04_checking_spans.ipynb` | Validate and inspect annotated text spans |

---

### 🏢 corp_blogs
Jupyter notebooks for parsing and analysing corporate blog posts.

| Notebook | Description |
|---|---|
| `01_parser.ipynb` | Scrape and parse corporate blog articles |
| `02_classifier.ipynb` | AI relevance classification |
| `03_analysis.ipynb` | Analysis of AI references in corporate blogs |

---

### 📺 subtitles
Jupyter notebooks for parsing and analysing Dutch TV broadcast subtitles (STL format).

| Notebook | Description |
|---|---|
| `01_parsing.ipynb` | Convert STL subtitle files and parse into DataFrames |
| `02_classifying.ipynb` | AI relevance classification of subtitle segments |
| `02d_map_topics.ipynb` | Map and label topic clusters |
| `03_inspect_topics.ipynb` | Inspect topic model output |
| `04_relevant_parts.ipynb` | Extract and inspect relevant subtitle spans |

---

### 🔧 Shared Components

- `preprocessing/`  
  Shared preprocessing utilities used across all data sources (`preprocessing.ipynb`).
- `BERT/`  
  BERT-based models, fine-tuning scripts, and experiments used for classification tasks (`03_BERT.ipynb`, `03b_BERT_Ttrial_metrics.ipynb`, `03c_BERT_Trial_label_comparison.ipynb`).

---

## ⚙️ Setup

Install dependencies with:

```bash
pip install -r requirements.txt
```

Key packages: `pandas`, `spacy`, `nltk`, `pdfplumber`, `selenium`, `networkx`, `wordcloud`, `litellm`.

---

## 🧠 Methods Summary

### 1) **Data Parsing & Cleaning**
- Import and convert heterogeneous text sources into standardized DataFrames.
- Normalize encoding, remove duplicates, and extract metadata where possible.

### 2) **AI Relevance Classification**
- Keyword-based classification with logic to:
  - Distinguish AI-as-technology from homonyms (e.g., *Ai Weiwei*, greetings like *ai*).
  - Collapse expressions such as *”kunstmatige intelligentie (AI)”* into single conceptual hits.
  - Require contextual evidence (≥1 hit in the title OR ≥2 hits in the main text).

### 3) **Manual Annotation**
- Manual annotation conducted independently by two researchers to validate classification outputs and support qualitative interpretation.

### 4) **Topic Modeling**
- BERTopic or alternative transformer-based topic clustering.
- Comparative analysis of topic distributions across actor groups and time ranges.

### 5) **Further Analysis**
- Named Entity Recognition (NER) to identify actors, organisations, and locations.
- Word2Vec embeddings over time to track semantic shifts around AI terminology.
- Network analysis of co-occurring entities.

---



