# ehrQL Usage Analysis in OpenSAFELY

This project analyses how **ehrQL (Electronic Health Records Query Language)** is being used across the OpenSAFELY research ecosystem. The goal is to provide insights into which features are widely used, underutilised, or deprecated, supporting better platform development, training, and documentation.

---

## Project Objective

- Analyse the usage of ehrQL across OpenSAFELY repositories.  
- Identify which features are **most popular**, **rarely used**, or **deprecated**.  
- Provide actionable insights for the tech team, researchers, and documentation teams.  

**Key Questions Addressed:**

- Which ehrQL features are most commonly used?  
- Which features are barely touched?  
- Are deprecated features still in use?  
- How can findings guide platform improvements and training?  

---

## Why This Matters

- **Prioritise Improvements:** Tech team can focus on features most relevant to users.  
- **Guide Researchers:** Encourage adoption of up-to-date features.  
- **Targeted Documentation:** Identify features that need better guidance or tutorials.  
- **Monitor Platform Health:** Spot features that may be underutilised or obsolete.  

---

## Project Workflow

The analysis was carried out in three main stages:

### Stage 1 – Retrieving Repository Metadata
- Used the GitHub REST API (`/orgs/{ORG}/repos`) to retrieve all repositories in the OpenSAFELY GitHub organisation.  
- Authentication via personal access token (up to 5,000 requests/hour).  
- Paginated results to retrieve **100 repositories per request**.  
- Extracted and stored in CSV:  
  - Repository name  
  - Creation date  
  - Repository URL  

### Stage 2 – Identifying Python Files Using ehrQL
- Used GitHub code search API with the query:
  `ehrQL language:python org:opensafely`
- Collected metadata for each matching file:  
- File name & path  
- GitHub file URL  
- Raw file URL for direct download  
- Downloaded all relevant files locally, with **logging and error handling** to track failures.  

### Stage 3 – Parsing Files and Counting Features
- Parsed Python files to count usage of each ehrQL feature:  
- Handled Unicode errors via fallback encoding  
- Case-insensitive search using a reference list of features  
- Counted occurrences and mapped them to repositories  
- Generated CSV outputs:  
- `feature_counts.csv` – total occurrences of each feature  
- `feature_repository_map.csv` – which repositories use each feature  

---

## Interactive Dashboard

To make results more accessible, an **interactive dashboard** was built using **Streamlit**.  

**Dashboard Views:**

1. **All Repositories:** Repository metadata, creation dates, and trends over time  
2. **Feature Counts:** Interactive heatmaps showing feature usage frequency  
3. **Feature Details:** Select a feature to view repositories using it, with charts and tables  

---

## Key Findings

**Most Popular Features:**  
- **where() – 3027 uses:** Central for filtering datasets based on conditions  
- **codelist_from_csv() – 1782 uses:** Commonly used to load code lists for patient cohorts  
- **Temporal Functions:**  
- `days()` – 1162 uses  
- `months()` – 1275 uses  
- `years()` – 336 uses  
- `start_date` – 1448 uses  
- `end_date` – 2693 uses  
- **Conditional & Aggregation Functions:**  
- `case()` – 702 uses  
- `first_for_patient()` – 436 uses  
- `last_for_patient()` – 365 uses  

These findings highlight key workflows, such as **filtering datasets, cohort definitions, date handling, and patient-level calculations**, which are central to reproducible health research.

---

## Collaboration & Remote Work

- Worked mostly remotely, communicating progress through **Slack updates, and quick calls**.  
- Developed skills in **documenting technical decisions clearly** for distributed teams.  

---

## Next Steps

- Integrate **job execution data** to track which features are actually run against patient data, providing insights into real-world feature usage over time.  
- Apply learnings to future projects and continue building **practical software solutions**.  

---

## Tech Stack

- **Languages:** Python, SQL  
- **Libraries:** Pandas, NumPy, Regex, tqdm, Pathlib  
- **Tools:** Git, GitHub REST API, Streamlit, Logging  
- **Data:** CSV exports for repository metadata and feature counts  

---

## Usage

1. Clone the repository:
 `git clone <repository-url>`

2. Install dependencies:
`pip install -r requirements.txt`
3. Run scripts to retrieve repository metadata, parse Python files, and count feature usage.

4. Launch Streamlit dashboard:
`streamlit run dashboard.py`
