import streamlit as st
import pandas as pd
import ollama
import ast
import json
import re
import io
import requests
from PIL import Image
from streamlit_lottie import st_lottie

# Custom CSS for modern UI
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4a90e2;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #357abd;
    }
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Arial', sans-serif;
    }
    .stTextArea>label {
        font-weight: bold;
        color: #34495e;
    }
    .stExpander {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Function to load Lottie animations
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

welcome_animation = load_lottie_url("https://lottie.host/0bd09814-d2ae-4f38-a301-4b1c01d1d778/OWezBSJvFE.json")
congratulations_animation = load_lottie_url("https://lottie.host/768b23c5-2167-45ed-afb0-42f3fc4d7c0c/F40M6pnGsn.json")

# Utility functions
def extract_and_convert_list(text):
    list_match = re.search(r'\[.*?\]', text, re.DOTALL)
    if list_match:
        list_string = list_match.group()
        try:
            python_list = ast.literal_eval(list_string)
            if isinstance(python_list, list):
                return python_list
            return None
        except (SyntaxError, ValueError):
            return None
    return None

def extract_and_parse_json(text):
    start_index = text.find('{')
    end_index = text.rfind('}')
    if start_index == -1 or end_index == -1 or end_index < start_index:
        return None, False
    json_str = text[start_index:end_index + 1]
    try:
        parsed_json = json.loads(json_str)
        return parsed_json, True
    except json.JSONDecodeError:
        return None, False

def validate_and_convert_salary_json(json_input):
    def is_valid_salary_comparison(data):
        return (
            "salary_comparison" in data and
            "philippines" in data["salary_comparison"] and
            "united_states" in data["salary_comparison"]
        )
    
    # Handle case where json_input is already a dict
    if isinstance(json_input, dict):
        data = json_input
        valid = is_valid_salary_comparison(data)
        if valid:
            valid = data["salary_comparison"]["philippines"] < 10000 and data["salary_comparison"]["united_states"] < 10000
        return data, valid
    
    # Handle case where json_input is a string
    try:
        data = json.loads(json_input)
        valid = is_valid_salary_comparison(data)
        if valid:
            valid = data["salary_comparison"]["philippines"] < 10000 and data["salary_comparison"]["united_states"] < 10000
        return data, valid
    except (json.JSONDecodeError, TypeError):
        return None, False

def check_input_specificity(input_text):
    generic_phrases = ["general", "n/a", "not sure", "don't know", "do you", "are you", "you", "Are there"]
    return not any(phrase.lower() in input_text.lower() for phrase in generic_phrases)

def simulate_job_relevance_classification(job_list, company_needs_description):
    if not job_list:
        return [], []
    relevant_roles = [role for role in job_list if role.lower() not in company_needs_description.lower()]
    irrelevant_roles = [role for role in job_list if role.lower() in company_needs_description.lower()]
    return relevant_roles, irrelevant_roles

def input_is_out_of_context(input_text):
    irrelevant_keywords = ["unrelated", "out of context", "irrelevant"]
    return any(phrase.lower() in input_text.lower() for phrase in irrelevant_keywords)

def is_relevant_to_jobs_and_business(input_text):
    relevant_keywords = ["job", "hire", "business", "project", "team", "staff", "company", "role", "position", "expertise"]
    return any(keyword.lower() in input_text.lower() for keyword in relevant_keywords)

def analyze_url_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            text = response.text
            about_us_start = text.lower().find('about us') or text.lower().find('our company')
            if about_us_start != -1:
                about_us_end = text.lower().find('</div>', about_us_start)
                about_us_content = text[about_us_start:about_us_end]
                return about_us_content
        return None
    except Exception:
        return None

# Main app logic
def main():
    st_lottie(welcome_animation, height=200, key="welcome_animation")
    
    st.markdown("<h1 style='text-align: center;'>Team Builder</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #7f8c8d;'>
            <p>Build your dream team with tailored job role recommendations and salary insights.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<h3>Describe Your Company's Needs</h3>", unsafe_allow_html=True)
        st.markdown("""
            <p style='color: #7f8c8d;'>Tell us about your challenges, goals, or specific expertise needs. For example:</p>
            <ul style='color: #7f8c8d;'>
                <li>Specific project bottlenecks</li>
                <li>New initiatives requiring talent</li>
                <li>Job roles to enhance your team</li>
            </ul>
        """, unsafe_allow_html=True)
        company_needs_description = st.text_area("Enter Description or Paste Company URL/About Us Page:", height=150)

    # Session state initialization
    if 'main_response' not in st.session_state:
        st.session_state.main_response = ""
    if "job_list" not in st.session_state:
        st.session_state.job_list = []
    if "relevant_job_list" not in st.session_state:
        st.session_state.relevant_job_list = []
    if "irrelevant_job_list" not in st.session_state:
        st.session_state.irrelevant_job_list = []
    if "job_list_salary" not in st.session_state:
        st.session_state.job_list_salary = []
    if 'additional_info' not in st.session_state:
        st.session_state.additional_info = ""
    if 'show_job_list' not in st.session_state:
        st.session_state.show_job_list = False

    if st.button("Analyze"):
        is_url_provided = company_needs_description.startswith("http")
        if is_url_provided:
            about_us_content = analyze_url_content(company_needs_description)
            if about_us_content:
                company_needs_description = about_us_content
            else:
                st.session_state['job_list'] = []
                st.session_state.show_job_list = False

        if not is_url_provided and (not check_input_specificity(company_needs_description) or input_is_out_of_context(company_needs_description) or not is_relevant_to_jobs_and_business(company_needs_description)):
            st.warning("Please provide specific details related to jobs or business needs.")
            st.session_state['job_list'] = []
            st.session_state.show_job_list = False
        else:
            with st.spinner("Analyzing your needs..."):
                chat_log = [
                    {"role": "system", "content": "You are an expert HR analyst tasked with identifying precise job roles based on a company’s needs description. Provide a detailed response with specific job titles relevant to the input."},
                    {"role": "user", "content": f"Analyze the following company needs and suggest specific job roles: {company_needs_description}"}
                ]
                result = ollama.chat(model="llama3.2", messages=chat_log)
                response = result["message"]["content"]
                st.session_state.main_response = response

                if "job roles" in response.lower() or "positions" in response.lower():
                    prompt = """
                        Extract all job roles mentioned in the previous response and format them as a Python list of strings. Ensure accuracy and relevance to the company needs. Example: ["Web Developer", "Accountant", "3D Graphic Artist"]
                    """
                    chat_log.append({"role": "assistant", "content": response})
                    chat_log.append({"role": "user", "content": prompt})
                    result = ollama.chat(model="llama3.2", messages=chat_log)
                    job_list_response = result["message"]["content"]
                    job_list = extract_and_convert_list(job_list_response)
                    if job_list:
                        st.session_state['job_list'] = job_list
                        st.session_state.relevant_job_list, st.session_state.irrelevant_job_list = simulate_job_relevance_classification(job_list, company_needs_description)
                        st.session_state.show_job_list = True
                    else:
                        st.warning("Could not extract job roles. Please refine your description.")
                        st.session_state.show_job_list = False
                else:
                    st.warning("No job roles identified. Please provide more detailed needs.")
                    st.session_state['job_list'] = []
                    st.session_state.show_job_list = False

    if st.session_state.main_response:
        with st.expander("View Analysis Response"):
            st.write(st.session_state.main_response)
        
        additional_info = st.text_area("Add More Details (Optional):", height=100)
        st.session_state.additional_info = additional_info

        if st.button("Submit Additional Info"):
            if additional_info.lower() in ["n/a", "not sure", "don't know", "general", "none"] or not is_relevant_to_jobs_and_business(additional_info):
                st.warning("Please provide specific, relevant additional details.")
            else:
                with st.spinner("Processing additional info..."):
                    full_description = f"{company_needs_description}\n\nAdditional Info: {additional_info}"
                    chat_log = [
                        {"role": "system", "content": "You are an expert HR analyst tasked with identifying precise job roles based on a company’s needs description. Provide a detailed response with specific job titles relevant to the input."},
                        {"role": "user", "content": f"Analyze the following company needs and suggest specific job roles: {full_description}"}
                    ]
                    result = ollama.chat(model="llama3.2", messages=chat_log)
                    response = result["message"]["content"]
                    st.session_state.main_response = response

                    if "job roles" in response.lower() or "positions" in response.lower():
                        prompt = """
                            Extract all job roles mentioned in the previous response and format them as a Python list of strings. Ensure accuracy and relevance to the company needs. Example: ["Web Developer", "Accountant", "3D Graphic Artist"]
                        """
                        chat_log.append({"role": "assistant", "content": response})
                        chat_log.append({"role": "user", "content": prompt})
                        result = ollama.chat(model="llama3.2", messages=chat_log)
                        job_list_response = result["message"]["content"]
                        job_list = extract_and_convert_list(job_list_response)
                        if job_list:
                            st.session_state['job_list'] = job_list
                            st.session_state.relevant_job_list, st.session_state.irrelevant_job_list = simulate_job_relevance_classification(job_list, full_description)
                            st.session_state.show_job_list = True
                        else:
                            st.warning("Could not extract job roles. Please refine your description.")
                            st.session_state.show_job_list = False
                    else:
                        st.session_state['job_list'] = []
                        st.session_state.show_job_list = False

    if st.session_state.show_job_list and st.session_state['job_list']:
        st.markdown("### Suggested Job Roles")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Relevant Roles")
            relevant_roles_str = ', '.join(st.session_state.relevant_job_list)
            relevant_roles_input = st.text_area("Edit Relevant Roles (comma-separated):", value=relevant_roles_str, height=100)
            st.session_state.relevant_job_list = [role.strip() for role in relevant_roles_input.split(',') if role.strip()]
        with col2:
            st.markdown("#### Irrelevant Roles")
            irrelevant_roles_str = ', '.join(st.session_state.irrelevant_job_list)
            irrelevant_roles_input = st.text_area("Edit Irrelevant Roles (comma-separated):", value=irrelevant_roles_str, height=100)
            st.session_state.irrelevant_job_list = [role.strip() for role in irrelevant_roles_input.split(',') if role.strip()]

        if st.button("Proceed"):
            st.session_state.show_job_list = False

    if st.session_state.relevant_job_list:
        job_list_salary = []
        for job in st.session_state["relevant_job_list"]:
            job_not_parsed_successfully = True
            while job_not_parsed_successfully:
                prompt = f"""
                    Generate a JSON object with realistic monthly median salaries in USD for the job role '{job}' based on current market data for the Philippines and the United States as of April 2025. Ensure salaries are accurate, whole numbers below 10,000 USD, and reflect typical differences (US salaries significantly higher). Format as follows:
                    {{
                        "salary_comparison": {{
                            "philippines": <number>,
                            "united_states": <number>
                        }}
                    }}
                """
                chat_log = [
                    {"role": "system", "content": "You are an expert in labor market analysis providing accurate salary data based on current trends."},
                    {"role": "user", "content": prompt}
                ]
                result = ollama.chat(model="llama3.2", messages=chat_log)
                job_salary_comparison = result["message"]["content"]

                salary_comparison_json, parsed_successfully = extract_and_parse_json(job_salary_comparison)
                if not parsed_successfully:
                    continue

                salary_json_cleaned, valid_json = validate_and_convert_salary_json(salary_comparison_json)
                if not valid_json:
                    continue

                job_not_parsed_successfully = False

            job_salary = {
                "job_role": job,
                "currency": "USD",
                "salary_comparison": salary_json_cleaned['salary_comparison']
            }
            job_list_salary.append(job_salary)
        st.session_state["job_list_salary"] = job_list_salary

        df = pd.DataFrame(job_list_salary)
        df = pd.concat([df.drop(['salary_comparison'], axis=1), df['salary_comparison'].apply(pd.Series)], axis=1)
        st.markdown("### Salary Comparison")
        st.dataframe(df)

    if st.session_state['job_list_salary']:
        st.markdown("##### Number of Employees")
        total_jobs = len(st.session_state['job_list_salary'])
        cols = st.columns(2)
        for i, job in enumerate(st.session_state['job_list_salary']):
            with cols[i % 2]:
                st.session_state['job_list_salary'][i]["no of employees"] = st.number_input(f"{job['job_role']}:", min_value=0, key=f"num_{job['job_role']}")

        if st.button("Calculate Cost"):
            st.markdown("### Cost Breakdown")
            for i in range(total_jobs):
                job = st.session_state['job_list_salary'][i]
                job["philippines_total_cost"] = job["no of employees"] * job["salary_comparison"]["philippines"]
                job["united_states_total_cost"] = job["no of employees"] * job["salary_comparison"]["united_states"]
                job["total_savings"] = job["united_states_total_cost"] - job["philippines_total_cost"]
                job["currency_symbol"] = "$"

            df = pd.DataFrame(st.session_state['job_list_salary'])
            df = pd.concat([df.drop(['salary_comparison'], axis=1), df['salary_comparison'].apply(pd.Series)], axis=1)
            st.dataframe(df)

            buffer = io.BytesIO()
            df.to_csv(buffer, index=False)
            st.download_button(label="Download Full Report", data=buffer, file_name='team_builder_report.csv', mime='text/csv')

            philippines_total = df["philippines_total_cost"].sum()
            us_total = df["united_states_total_cost"].sum()
            savings = df["total_savings"].sum()

            st.markdown(f"**Philippines Total Cost:** ${philippines_total:,.2f}")
            st.markdown(f"**United States Total Cost:** ${us_total:,.2f}")
            st.markdown(f"**Total Savings:** ${savings:,.2f}")

            st.markdown("### Refined Job Role Insights")
            refined_df = df[["job_role", "philippines_total_cost", "united_states_total_cost", "total_savings"]]
            st.write(refined_df)

            buffer = io.BytesIO()
            refined_df.to_csv(buffer, index=False)
            st.download_button(label="Download Refined Report", data=buffer, file_name='refined_team_builder_report.csv', mime='text/csv')
            st.markdown("By hiring in the Philippines, you can save significantly on labor costs while maintaining high-quality talent.")
            
        

            st_lottie(congratulations_animation, height=200, key="congratulations_animation")

if __name__ == "__main__":
    main()