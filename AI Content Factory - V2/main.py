import pandas as pd
import openai
import streamlit as st
from openai_key import openai_api
from prompt_library import prompt_templates

# Set your OpenAI API key here
openai.api_key = openai_api

st.set_page_config(
    page_title="AI Content Generator", # Set page title
    layout="wide", # Use the wide layout
)

# Create a title for your app
st.title('AI Content Generator')

# Create a description for your app
st.markdown('''
This application generates content using the OpenAI GPT-3 model. 
Upload a CSV file with prompts, select a prompt template, and let the model generate the content. 
You can then download the generated articles as a CSV file.
''')

def load_data(file_path):
    """
    Load CSV data from file_path.
    """
    try:
        df = pd.read_csv(file_path)
        st.write("Data loaded successfully")
        return df
    except Exception as e:
        st.write(f"Error occurred while loading data: {e}")

def parse_data(df):
    """
    Parse DataFrame into a list of articles.
    """
    try:
        articles = {}
        for index, row in df.iterrows():
            keyword = row["keyword"]
            article = {
                "topic": row["topic"],
                "sections": {col: row[col] for col in df.columns[2:] if pd.notnull(row[col])},
            }
            articles[keyword] = article
        return articles
    except Exception as e:
        st.write(f"Error occurred while parsing data: {e}")

def generate_content(keyword, article, system_prompt, user_prompt):
    """
    Generate long-form content for an article.
    """
    try:
        memory = [{"role": "system", "content": system_prompt}]
        generated_content_list = []
        for section, instructions in article["sections"].items():
            prompt = f"{user_prompt} {instructions}"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                max_tokens=800,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                messages=memory + [{"role": "user", "content": prompt}],
            )
            generated_section = response['choices'][0]['message']['content']
            memory.append({"role": "assistant", "content": generated_section})
            generated_content_list.append({"section": section, "content": generated_section})

        return {"keyword": keyword, "content": generated_content_list}
    except Exception as e:
        st.write(f"Error occurred while generating content: {e}")

def construct_html(generated_content):
    """
    Construct the HTML structure for each article.
    """
    try:
        html_article = f"<h1>{generated_content['keyword']}</h1>\n"
        for section_content in generated_content["content"]:
            html_article += f"<h2>{section_content['section']}</h2>\n<p>{section_content['content']}</p>\n"
        return html_article
    except Exception as e:
        st.write(f"Error occurred while constructing HTML: {e}")

def save_articles(articles):
    """
    Save generated articles into a new CSV file.
    """
    try:
        df = pd.DataFrame(articles)
        df.to_csv("Generated_Articles.csv", index=False)
    except Exception as e:
        st.write(f"Error occurred while saving articles: {e}")

def main():
    """
    Main function that will use Streamlit to create an interactive web app.
    """
    # User will upload the data file
    data_file = st.file_uploader("Upload your data file", type=['csv'])
    if data_file is not None:
        st.success("File uploaded successfully!")
        df = load_data(data_file)
        articles = parse_data(df)

        # Select a prompt template
        selected_template = st.sidebar.selectbox('Select a prompt template', list(prompt_templates.keys()))

        # Extract system and user prompts from the selected template
        system_prompt = prompt_templates[selected_template]["system_prompt"]
        user_prompt = prompt_templates[selected_template]["user_prompt"]

        generated_contents = []
        for keyword, article in articles.items():
            # Generate content for the selected article
            generated_content = generate_content(article, system_prompt, user_prompt)
            generated_contents.append(generated_content)

        # Provide an option to save all generated articles
        if st.button('Save Generated Articles'):
            save_articles(generated_contents)
            st.success("Articles saved successfully!")

if __name__ == "__main__":
    main()
