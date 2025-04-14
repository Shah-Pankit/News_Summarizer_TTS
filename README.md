# 📰 News Summarizer TTS (Text-to-Speech) 🗣️

A smart web application that summarizes the latest news about any company and reads it aloud in Hindi. Built using Python, LLMs, web scraping, and Text-to-Speech synthesis — all packed into one sleek, deployable interface.

---

## 🚀 Features

- 🔍 **Company Name Correction**  
  Automatically corrects misspelled company names using LLM-based validation (e.g., "appel" ➝ "Apple").

- 📰 **Live News Scraping**  
  Fetches the latest news articles about the specified company from the web.

- ✂️ **Real-time Summarization**  
  Uses advanced NLP techniques to summarize the content on-the-fly.

- 🗣️ **Hindi Text-to-Speech**  
  Converts summarized content into Hindi audio using TTS models.

- 🌐 **Web Interface**  
  User-friendly web app for entering company names and listening to summaries.

---

## 🧠 Tech Stack

| Layer                 | Technology Used                   |
|-----------------------|-----------------------------------|
| 👨‍💻 Frontend           | Streamlit                        |
| 🧠 NLP + LLMs         |Groq                              |
| 📰 Scraping           | BeautifulSoup / Requests         |
| 🧾 Summarization      | Transformers / LLM-based models  | 
| 🔊 Text-to-Speech     | gTTS / Coqui TTS (Hindi)         |
| 🐳 Deployment         | Docker + Hugging Face Spaces     |

---

## 💡 How It Works

1. User enters a **company name**.
2. The app **validates and corrects** the name using an LLM.
3. It **scrapes recent news articles** about the company.
4. Each article is **summarized** using a pre-trained model.
5. The summary is **converted to Hindi audio** and played for the user.

---
