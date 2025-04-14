import streamlit as st
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import json
from groq import Groq

from dotenv import load_dotenv
load_dotenv()

# Database file
DB_FILE = "techspot_news.db"

def check_language_and_correct_name(company):
    """Correct the company name using Groq API"""
    try:
        client = Groq(api_key=os.getenv("API_KEY"))
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": """You are a highly accurate and intelligent language processing system. Your task is to process a given company name and return a corrected, English-translated version in JSON format.
                Instructions:
                1. The user will input a company name.
                2. If the name is not in English, translate it into English.
                3. If the name has spelling errors (e.g., "Telsa" instead of "Tesla"), correct them.
                4. If everything is perfect just reply the company name back in JSON object.
                5. The response should be formatted strictly as a JSON object:
                {
                    "corrected_company_name": "Tesla"
                }
                6. Do not include any additional text, explanations, or formatting outside the JSON response."""},
                {"role": "user", "content": company}
            ]
        )
        
        # Parse the JSON response
        corrected_name = json.loads(response.choices[0].message.content)['corrected_company_name']
        return corrected_name
    except Exception as e:
        st.error(f"Error in name correction: {e}")
        return company

def create_table():
    """Create the database table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            short_continuation TEXT,
            timestamp TEXT,
            url TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def store_news(title, content, short_continuation, timestamp, url):
    """Store extracted news into the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO news (title, content, short_continuation, timestamp, url)
            VALUES (?, ?, ?, ?, ?)
        """, (title, content, short_continuation, timestamp, url))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        st.error(f"Error inserting into database: {e}")

def scrape_techspot(company, limit=10):
    """Scrape news articles from TechSpot for a given company."""
    url_make = f"https://www.techspot.com/tag/{company.lower().replace(' ', '-')}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url_make, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            articles = soup.select("#news_container article")

            st.write(f"📡 Found {len(articles)} articles for {company}")

            count = 0
            scraped_articles = []
            for article in articles:
                if count >= limit:
                    break

                # Extracting title
                title_element = article.select_one("h2 a")
                title = title_element.get_text(strip=True) if title_element else "No Title"

                # Extracting content
                content_element = article.select_one("div.intro")
                content = content_element.get_text(strip=True) if content_element else "No Content"

                # Extracting timestamp
                timestamp_element = article.select_one("time")
                timestamp = timestamp_element.get_text(strip=True) if timestamp_element else "No Timestamp"

                # Extracting URL
                news_url = title_element["href"] if title_element and "href" in title_element.attrs else "#"
                final_url = f"https://www.techspot.com{news_url}" if news_url.startswith("/") else news_url

                # Store news in database
                store_news(title, content, timestamp, timestamp, final_url)
                
                # Collect articles for summary
                scraped_articles.append({
                    "title": title,
                    "content": content,
                    "timestamp": timestamp,
                    "url": final_url
                })
                
                count += 1

            return scraped_articles
        else:
            st.error(f"Failed to fetch news. Status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"An error occurred while scraping: {e}")
        return []

def generate_news_summary(company, articles):
    """Generate a summary of scraped articles using Groq API."""
    try:
        # Prepare the articles content for summarization
        articles_text = "\n\n".join([
            f"Title: {article['title']}\nContent: {article['content']}\nTimestamp: {article['timestamp']}\nURL: {article['url']}"
            for article in articles
        ])

        # Initialize Groq client
        client = Groq(api_key=os.getenv("API_KEY"))

        # Create the summarization prompt
        summarization_prompt = f"""You are an expert news analyst. Provide a comprehensive, objective summary of the latest news about {company} based on the following articles:

{articles_text}

Summary Guidelines:
1. Synthesize the key information from all articles
2. Highlight the most important themes and developments
3. Provide context and potential implications
4. Be concise but comprehensive
5. Maintain a neutral, professional tone
6. Keep the summary under 100 words
7. Translate the entire generated summary in 100 words to hindi.
8. output should be in hindi."""

        # Generate summary using Groq
        chat_completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are an expert news analyst and summarizer."},
                {"role": "user", "content": summarization_prompt}
            ],
            max_tokens=500
        )

        # Extract and return the summary
        summary = chat_completion.choices[0].message.content
        return summary

    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return "Unable to generate summary due to an error."
    
# def hindi_speech(summary):
    

def main():
    # Set up Streamlit page
    st.set_page_config(page_title="News_Summarizer_TTS", page_icon="📰")
    st.title("🔍 TechSpot News Summarizer")

    # Create input for company name
    original_company_name = st.text_input("Enter the company name:", placeholder="e.g., Tesla, Apple, Google")
    
    # Scrape and summarize button
    if st.button("Scrape and Summarize News"):
        # Validate input
        if not original_company_name:
            st.warning("Please enter a company name")
            return

        # Step 1: Correct the company name
        with st.spinner('Verifying company name...'):
            corrected_company_name = check_language_and_correct_name(original_company_name)

        # Delete existing database
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

        # Create database table
        create_table()

        # Progress indication
        with st.spinner('Scraping articles and generating summary...'):
            # Scrape articles
            scraped_articles = scrape_techspot(corrected_company_name, limit=10)

            # Generate and display summary
            if scraped_articles:
                # Display individual articles
                st.subheader("Scraped Articles")
                for article in scraped_articles:
                    with st.expander(article['title']):
                        st.write(f"**Content:** {article['content']}")
                        st.write(f"**Timestamp:** {article['timestamp']}")
                        st.write(f"**URL:** {article['url']}")

                # Generate and display summary
                st.subheader("News Summary")
                summary = generate_news_summary(corrected_company_name, scraped_articles)
                st.write(summary)
            else:
                st.error("No articles could be retrieved.")

if __name__ == "__main__":
    main()