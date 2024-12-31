import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

# Set your OpenAI API Key
os.environ["OPENAI_API_KEY"] = "put open ai key here"

# Serper API Key
SERP_API_KEY = "put serper api key here"

# Serper search function
def serper_search(query: str):
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': SERP_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": 10}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        results = response.json()
        return [{"title": r["title"], "link": r["link"], "snippet": r["snippet"]} for r in results.get("organic", [])]
    else:
        st.error(f"Search error: {response.status_code} - {response.text}")
        return []

# Research industry or company
def research_industry(company_or_industry: str):
    query = f"{company_or_industry} industry overview"
    return serper_search(query)

# Generate use cases using OpenAI
def generate_use_cases_with_ai(industry_data):
    industry_research_text = "\n".join(
        [f"- {data['title']}:\n  {data['snippet']}" for data in industry_data]
    )
    prompt = (
        f"Based on the following industry research data:\n{industry_research_text}\n\n"
        "Generate a list of innovative and practical AI/ML/Generative AI use cases that can enhance operations, "
        "improve customer satisfaction, and boost efficiency in this industry. Include solutions like:\n"
        "- Document search and retrieval systems\n"
        "- Automated report generation tools\n"
        "- AI-powered chat systems for internal or customer-facing use."
    )
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant skilled in generating AI/ML use cases."},
                {"role": "user", "content": prompt}
            ]
        },
    )
    if response.status_code == 200:
        use_cases_text = response.json()["choices"][0]["message"]["content"]
        return [{"use_case": case.strip()} for case in use_cases_text.split("\n") if case.strip()]
    else:
        st.error("Error fetching use cases from OpenAI API.")
        return []

# Find datasets for use cases
def find_datasets_for_use_cases(use_cases):
    datasets = []
    for case in use_cases:
        query = f"dataset for {case['use_case']}"
        results = serper_search(query)
        datasets.append({
            "use_case": case["use_case"],
            "datasets": [{"title": r["title"], "link": r["link"], "snippet": r["snippet"]} for r in results]
        })
    return datasets

# Streamlit app
st.title("Generative AI Use Case Explorer")
st.sidebar.header("Input Parameters")

# User input
company_or_industry = st.sidebar.text_input("Enter Industry or Company", value="Retail Industry")

if st.sidebar.button("Generate Report"):
    st.write(f"## Generative AI Use Cases for {company_or_industry}")
    st.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Research industry
    st.write("### Industry Research")
    industry_data = research_industry(company_or_industry)
    if industry_data:
        for data in industry_data:
            st.write(f"- **{data['title']}**")
            st.write(f"  - {data['snippet']}")
            st.write(f"  - [Read More]({data['link']})")

        # Generate use cases
        st.write("### Proposed Use Cases")
        use_cases = generate_use_cases_with_ai(industry_data)
        for case in use_cases:
            st.write(f"- {case['use_case']}")

        # Find datasets
        st.write("### Relevant Datasets")
        datasets = find_datasets_for_use_cases(use_cases)
        for dataset in datasets:
            st.write(f"- **For Use Case:** {dataset['use_case']}")
            for data in dataset["datasets"]:
                st.write(f"  - **{data['title']}**: {data['snippet']}")
                st.write(f"    - [Dataset Link]({data['link']})")
    else:
        st.error("No industry research data found.")
