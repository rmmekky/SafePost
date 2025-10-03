# app.py
import os
import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime

from imagecaption import ImageCaptioning
from text_classifier import TextClassifier
from database import init_csv, save_to_csv, load_csv, CSV_FILE

# --- Initialize ---
init_csv()
ic = ImageCaptioning()
tc = TextClassifier()
os.makedirs("uploads", exist_ok=True)

# --- Streamlit UI ---
st.set_page_config(page_title="SafePost", page_icon="🛡️", layout="wide")
st.title("🛡️ SafePost – AI Content Safety Checker")

menu = ["Submit Post", "View Database", "Analytics Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

# ------------------- Submit Post -------------------
if choice == "Submit Post":
    st.subheader("✍️ Submit Your Content")
    input_type = st.radio("Choose input type:", ["Text only", "Image only", "Text + Image"])
    user_text = ""
    uploaded_file = None

    if input_type in ["Text only", "Text + Image"]:
        user_text = st.text_area("Write your post here:")

    if input_type in ["Image only", "Text + Image"]:
        uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])

    if st.button("Submit Post"):
        combined_text = ""
        if user_text.strip():
            combined_text += user_text.strip()

        if uploaded_file is not None:
            image_path = os.path.join("uploads", uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.image(Image.open(image_path), caption="Uploaded Image", use_container_width=True)

            caption = ic.generate_caption(image_path)
            st.info(f"Generated Caption: {caption}")

            combined_text = (combined_text + " " + caption).strip() if combined_text else caption

        if combined_text:
            classification = tc.classify(combined_text)
            save_to_csv(combined_text, classification)
            st.success(f"Classification: **{classification}**")
        else:
            st.warning("Please provide text or upload an image to classify.")

# ------------------- View Database -------------------
elif choice == "View Database":
    st.subheader("📊 All Stored Posts & Classifications")
    df = load_csv()

    if not df.empty:
        # تأكد وجود الأعمدة
        for col in ["Input", "Classification", "Timestamp"]:
            if col not in df.columns:
                df[col] = ""

        st.sidebar.subheader("Database Options")

        # --- Search suggestions ---
        all_words = " ".join(df["Input"]).split()
        unique_words = list(set(all_words))
        search_text = st.sidebar.text_input("Search text:", placeholder="Type to search...")
        if search_text:
            suggestions = [w for w in unique_words if w.lower().startswith(search_text.lower())]
            if suggestions:
                st.sidebar.write("Suggestions:", ", ".join(suggestions[:10]))

        # Filter by classification
        filter_class = st.sidebar.selectbox(
            "Filter by classification:",
            options=["All", "Safe to post", "Inappropriate content"]
        )

        # Filter by date
        filter_date = st.sidebar.date_input("Filter by date:")

        # Sorting
        sort_option = st.sidebar.selectbox("Sort by:", ["Timestamp", "Text Length", "Classification"])
        ascending = st.sidebar.checkbox("Ascending order", value=True)

        # Multi-row Delete
        rows_to_delete = st.sidebar.multiselect(
            "Select rows to delete:",
            options=df.index,
            format_func=lambda x: f"{x}: {df.loc[x, 'Input'][:30]}..."
        )
        if rows_to_delete:
            st.sidebar.subheader("Preview Selected Rows for Deletion")
            st.sidebar.write(df.loc[rows_to_delete, ["Input", "Classification"]])

        if st.sidebar.button("Delete Selected Rows") and rows_to_delete:
            df = df.drop(rows_to_delete).reset_index(drop=True)
            df.to_csv(CSV_FILE, index=False)
            st.success(f"{len(rows_to_delete)} rows deleted successfully.")

        # Edit Row
        row_to_edit = st.sidebar.selectbox("Select row to edit:", options=df.index)
        st.sidebar.subheader("Preview Row to Edit")
        st.sidebar.write(df.loc[row_to_edit, ["Input", "Classification"]])

        new_text = st.sidebar.text_area("Edit text:", value=df.loc[row_to_edit, "Input"])
        new_class = st.sidebar.selectbox(
            "Edit classification:",
            options=["Safe to post", "Inappropriate content"],
            index=0 if df.loc[row_to_edit, "Classification"]=="Safe to post" else 1
        )
        if st.sidebar.button("Save Changes"):
            df.loc[row_to_edit, "Input"] = new_text
            df.loc[row_to_edit, "Classification"] = new_class
            df.to_csv(CSV_FILE, index=False)
            st.success(f"Row {row_to_edit} updated successfully.")

        # --- Apply filters and sorting ---
        filtered_df = df.copy()
        if search_text:
            filtered_df = filtered_df[filtered_df["Input"].str.contains(search_text, case=False)]
        if filter_class != "All":
            filtered_df = filtered_df[filtered_df["Classification"] == filter_class]
        if filter_date:
            # تحويل Timestamp بصيغة ISO8601 ديناميكي
            filtered_df['Date'] = pd.to_datetime(filtered_df['Timestamp'], errors='coerce').dt.date
            filtered_df = filtered_df[filtered_df['Date'] == filter_date]

        if sort_option == "Text Length":
            filtered_df["Text Length"] = filtered_df["Input"].apply(len)
            display_df = filtered_df.sort_values("Text Length", ascending=ascending).drop(columns="Text Length")
        else:
            display_df = filtered_df.sort_values(sort_option, ascending=ascending)

        # --- Pagination ---
        rows_per_page = st.sidebar.number_input("Rows per page:", min_value=5, max_value=50, value=10)

        # زرار Reload
        if st.sidebar.button("🔄 Reload Data"):
            st.experimental_rerun()

        total_pages = (len(display_df) - 1) // rows_per_page + 1 if len(display_df) > 0 else 0

        if total_pages > 0:
            page_number = st.sidebar.number_input("Page number:", min_value=1, max_value=total_pages, value=1)
            start_idx = (page_number - 1) * rows_per_page
            end_idx = start_idx + rows_per_page
            st.dataframe(display_df.iloc[start_idx:end_idx], use_container_width=True)
        else:
            st.info(" No data available to display. Please add some posts first.")


# ------------------- Analytics Dashboard -------------------
elif choice == "Analytics Dashboard":
    st.subheader("📊 Analytics Dashboard (Advanced)")

    df = load_csv()
    if not df.empty:
        for col in ["Input", "Classification", "Timestamp"]:
            if col not in df.columns:
                df[col] = ""

        st.sidebar.subheader("Dashboard Filters")
        filter_class = st.sidebar.multiselect(
            "Select Classification:",
            options=["Safe to post", "Inappropriate content"],
            default=["Safe to post", "Inappropriate content"]
        )
        min_conf = st.sidebar.slider("Minimum Confidence (%)", min_value=0, max_value=100, value=0)
        date_range = st.sidebar.date_input("Select Date Range:",
                                           value=[pd.to_datetime(df['Timestamp'], errors='coerce').min(),
                                                  pd.to_datetime(df['Timestamp'], errors='coerce').max()])

        # Apply Filters
        filtered_df = df.copy()
        filtered_df = filtered_df[filtered_df["Classification"].isin(filter_class)]
        filtered_df['Date'] = pd.to_datetime(filtered_df['Timestamp'], errors='coerce').dt.date
        filtered_df = filtered_df[(filtered_df['Date'] >= date_range[0]) & (filtered_df['Date'] <= date_range[1])]

        # --- Overview Metrics ---
        st.write("### Overview Metrics")
        total_posts = len(filtered_df)
        safe_posts = len(filtered_df[filtered_df["Classification"]=="Safe to post"])
        inappropriate_posts = len(filtered_df[filtered_df["Classification"]=="Inappropriate content"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Posts", total_posts)
        col2.metric("Safe Posts", safe_posts)
        col3.metric("Inappropriate Posts", inappropriate_posts)

        # --- Trends Over Time ---
        st.write("### Posts Over Time")
        trend = filtered_df.groupby(['Date', 'Classification']).size().unstack(fill_value=0)
        st.line_chart(trend)

        # --- Word Clouds ---
        st.write("### Top Keywords WordClouds")
        for label in filter_class:
            text = " ".join(filtered_df[filtered_df["Classification"]==label]["Input"])
            if text:
                wc = WordCloud(width=400, height=200, background_color="white").generate(text)
                st.write(label)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)

        # --- Export Filtered Data ---
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="dashboard_filtered_posts.csv",
            mime="text/csv"
        )
    else:
        st.warning("Database is empty.")
