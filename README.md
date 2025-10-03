# 🛡️ SafePost  

SafePost is a **Streamlit web application** that helps users analyze their text and images before posting online.  
It provides **automatic captions** for images and classifies content into:  
✅ **Safe to post**  
❌ **Inappropriate content**

---

## 🚀 Features
- 📸 **Image Captioning** – Generates descriptions for uploaded images.  
- 📝 **Text Classification** – Detects whether text is safe or inappropriate.  
- 📂 **CSV Database** – Saves all inputs, classifications, and timestamps.  
- 📊 **Statistics & Word Cloud** – Visualizes stored data.  
- 🎨 **Simple & Clean UI** – Built with Streamlit.  

---

## 🛠️ Tech Stack
- **Python 3**  
- **Streamlit** – Frontend & UI  
- **Transformers (Hugging Face)** – Text classification (DistilBERT)  
- **Pandas** – Data storage & handling  
- **Matplotlib / WordCloud** – Visualizations  

---

## 📦 Installation
Clone the repository and install the requirements:  
```bash
git clone https://github.com/rmmekky/SafePost.git
cd SafePost
pip install -r requirements.txt
