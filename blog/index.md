Title : Understanding ehrQL feature usage in the OpenSAFELY for Health Research

date: 2025-08-22

draft: false

Summary: This blog post shares the project I worked on during my summer internship at the Bennett Institute as part of the HDR UK Health Data Science programme. My project explored how ehrQL, is being used across OpenSAFELY repositories. I analysed code from 65 Repositories under the OpenSafely org. and was able to identified which features researchers rely on most, which are less common, and where improvements or additional support could be valuable.

Author: Vivian Okafor

Categories: OpenSafely, ehrQL


---
Vivian Okafor interned this summer at the Bennett Institute as part of the HDRUK Health Data Science Internship program. During her time here, she researched how [ehrQL (the Electronic Health Records Query Language)](https://docs.opensafely.org/ehrql/) is used across OpenSAFELY repositories. In this guest blog, she shares insights about her project and findings.

### Why:
ehrQL is a query language designed to simplify the process of working with health data. Since its release in December 2023, it has been used in around 65 research projects on [OpenSAFELY](https://www.bennett.ox.ac.uk/blog/2020/10/what-is-opensafely/), an open-source platform that securely supports analysis of over 58 million patient records in England.
The aim of this project was to understand how researchers are actually using ehrQL by asking:

- Which features are used most often?
- Which features are rarely or never used?
- Are any outdated or deprecated features still in use?
- Which features appear in code that is actively tested?

Understanding these patterns matters because:

- The tech team can prioritise which features to improve, simplify, or retire
- Researchers can be guided towards newer, more effective tools
- Training and documentation can be tailored to features that researchers find most challenging
- Feature combinations may reveal gaps where new language functions could be developed.

### How?
I developed a Python script to interact with the GitHub REST API to identify and analyse ehrQL usage across the OpenSAFELY organisation. 

#### Step 1: Extracting the Data
The first step was to query the GitHub API using the search `query:ehrQL language: python org:opensafely` to retrieve all repositories under the OpenSAFELY organisation. For each repository, I extracted its name, creation date, and URL. Building on this, I then used the GitHub code search API to locate python files in the repository that contained ehrQL code. 
For each matching file, I recorded its file name, file path, GitHub URL, and raw download link. I also applied filters to exclude certain repositories (e.g., documentation or tutorials) to keep the focus on research code.

All identified files were then downloaded locally, with logging and error handling in place to track issues like possible failed requests or encoding errors.

#### Step 2:  Parsing Files and Counting Features
Once downloaded, I parsed the Python files to count usage of each ehrQL feature. The process involved:
- Reading each file with fallback encoding to handle Unicode errors
- Performing a case-insensitive search for all features listed in a reference text file containing ehrQL features
- Counting every instance of a feature and mapping it to the repositories where it appeared.
Finally, I summarised the results in two CSV files:
- Feature counts – total occurrences of each feature across all repositories.
- Feature-repository map – linking each feature to the repositories where it was used.
  
#### Step 3: Displaying Results on Streamlit
To make the findings more accessible, I built an [interactive dashboard using Streamlit](https://ehrqlanalysis.streamlit.app/). The app provides three main views:

1. **All Repositories**: This page displays metadata about the repositories where ehrQL appears, including creation dates and trends over time
2. **Feature Counts**: Visualising how frequently each ehrQL class or method is used, presented as interactive barcharts
3. **Feature Details**: This page allows users to select an individual feature and see which repositories use it.

### The Results 
In my analysis, I reviewed around 65 repositories and 301 Python files containing ehrQL from across the OpenSAFELY GitHub organisation. I found clear patterns in how ehrQL is being used in practice. This provided a view into  which features researchers use in their code and how these choices shape their workflows.

#### Most Popular Features 
Features like `where()` (used to filter datasets) and `codelist_from_csv()` (used to define patient groups) returned the highest counts. This sjow that they are clearly central to researchers’ work. Temporary ones like `days()`, `months()`, `years()`, `start_date`, and `end_date` were also common, showing how often studies need to look at data over set time periods. The `sort_by()` function also returned one of the highest counts.

#### Rarely Used or Unused Features
Series and frame classes, such as `BoolEventSeries()`, `IntEventSeries()`, `FloatEventSeries()`, `EventFrame()`, and `SortedEventFrame()`, were not returned zero count. This may be  because researchers typically query tables directly from the backend rather than defining their own PatientFrames or EventFrames, and they rarely create series from scratch, as these are usually derived from existing tables. The use of PatientFrame in case-control studies is an exception rather than the norm, since researchers need it to generate control groups.
Helper functions like `as_int()`, `to_first_of_year()`, and `to_first_of_month()` appeared only a few times, indicating that researchers rarely require such fine-grained transformations. 

The `show()` function, designed for debugging and development, was used 17 times. This may be because it is intended as a tool for inspecting code, and researchers are unlikely to make GitHub commits when using it. Similarly, The `test_data` which is used to check weather a project is using the assure feature returned 17 counts across repositories, This may suggest that relatively few researchers are running tests on their code which probably means testing is not widely used yet, rather than the feature not being useful.


### What’s Next?

This project has given a first look at how ehrQL is used in OpenSAFELY repositories, but there’s plenty more to do. Future work could improve the exisiting script to return better feature usage counts and link the analysis with job history to reveal not just which features appear in code, but which ones are actually used when run against patient data. 
This would make it possible to see:

- When a repository first (or last) ran ehrQL code.
- Which features are most used in active jobs.
- Which features are written in code but never run.
- How feature use has changed over time.

A deeper analysis could also help the team spot projects that may need support or are still using deprecated features, while highlighting trends in how ehrQL is adopted and used in resaerch code.

I have created a [public GitHub repo](https://github.com/Veevfor/ehrQL_Analysis) for this project and if anyone is interested in this work, please feel free to contact me at bennett@phc.ox.ac.uk





    





