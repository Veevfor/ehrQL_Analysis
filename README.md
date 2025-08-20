 OpenSAFELY `ehrQL` Function Analysis

This project aims to understand what ehrQL features are used  by researchers in the OpenSafely(https://github.com/opensafely) GitHub organization to identify and count the usage of specific `ehrQL` functions. It is designed to provide insight into how commonly certain features of the `ehrQL` library are used across different repositories and projects. What features may not be used at all. 

Some specific questions that we would like to answer:
- What are the most popular ehrQL features?
- What are the least popular ehrQL features? Are any features not used at all?
- erhQL code can be tested using the assure feature, which repos are using this (and therefore testing their code)?
- The show() function is new. It is used for debugging, but might not be present in the code committed to GitHub. Is it used at all?
- Which deprecated ehrQL features are still in use?


## Project Goals

- Search all OpenSAFELY GitHub repositories for Python files containing the keyword `ehrQL`.
- Download and analyse those files.
- Search for specific function usages such as:
  - `show()`
  - `configure_dummy_data`
  - `add_column`
- Count:
  - How many **times each function appears** across all files.
  - How many **repositories** use each function.

---

## Techn Used

- **Python**
- **Jupyter Notebook**
- `pandas`
- `requests`
- `re` (regular expressions)

---

## Files Included

| File | Description |
|------|-------------|
| `opensafely_ehrql_results.xlsx` | Extracted GitHub results including file URLs and repo details. |
| `ehrQL_analysis.py` | Main script for feature search and counting. |
| `README.md` | Documentation. |

---

## What I have done So far?

1. **Search GitHub API**  
   The script queries GitHub’s API for Python files in OpenSAFELY repos containing the `ehrQL` keyword.

2. **Extract Metadata**  
   Saved file names, paths, and raw content URLs to an excel file.

3. **Download and Analyse**  
   Downloaded each Python file and used pattern matching (via `re`) to count specific function usage.

4. **Output**  
   Displayed total counts for each feature searched.

---

## What's Next?

## Example Output

```text
Feature Usage Counts:
show(): 0
configure_dummy_data: 95
add_column: 122



