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
  Jupyter notebooks for parsing, classifying, annotating, and analysing news data.

---

### 🗳️ elections
  Jupyter notebooks for parsing PDFs, classifying text, and analysing election materials.

---

### 🏛️ tweede_kamer 
  Jupyter notebooks for parsing documents, combining datasets, classification, and analysis.

---

### 🏢 corp_blogs
  Jupyter notebooks for parsing, classification, and analysis of corporate blog data.

---

### 🔧 Shared Components

- `preprocessing/`  
  Shared preprocessing utilities used across all data sources.
- `BERT/`  
  BERT-based models, fine-tuning scripts, and experiments used for classification tasks.


---

## 🧠 Methods Summary

### 1) **Data Parsing & Cleaning**
- Import and convert heterogeneous text sources into standardized DataFrames.
- Normalize encoding, remove duplicates, and extract metadata where possible.

### 2) **AI Relevance Classification**
- Keyword-based classification with logic to:
  - Distinguish AI-as-technology from homonyms (e.g., *Ai Weiwei*, greetings like *ai*).
  - Collapse expressions such as *“kunstmatige intelligentie (AI)”* into single conceptual hits.
  - Require contextual evidence (≥1 hit in the title OR ≥2 hits in the main text).

### 3) **Manual Annotation**
- Manual annotation conducted independently by two researchers to validate classification outputs and support qualitative interpretation.

### 4) **Topic Modeling**
- BERTopic or alternative transformer-based topic clustering.
- Comparative analysis of topic distributions across actor groups and time ranges.

---



