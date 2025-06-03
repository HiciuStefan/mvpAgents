import streamlit as st
import json
import os

PROCESSED_FILE = "processed_articles.json"
SITE_CONFIG_FILE = "site_config.json"

# Încarcă articolele procesate
def load_articles():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Salvează articolele actualizate
def save_articles(articles):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

# Încarcă numele siteurilor
def load_site_names():
    if os.path.exists(SITE_CONFIG_FILE):
        with open(SITE_CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            return {site["base_url"]: site["name"] for site in config}
    return {}

# Extrage clientul din url
def get_client_name(url, base_map):
    for base_url, name in base_map.items():
        if base_url in url:
            return name
    return "Unknown"

def main():
    st.set_page_config(page_title="Client Insights Dashboard", layout="wide")
    st.title("📊 Website Scraper & Opportunity Detector")

    articles = load_articles()
    site_names = load_site_names()

    # Filtrare: doar cele necitite
    articles = [a for a in articles if not a.get("read", False)]

    if not articles:
        st.success("🎉 Toate articolele au fost citite!")
        return

    # Grupăm articolele după client
    grouped = {}
    for article in articles:
        client = get_client_name(article["url"], site_names)
        grouped.setdefault(client, []).append(article)

    for client, items in grouped.items():
        st.markdown("---")
        st.subheader(f"🌐 {client} ({len(items)} articole)")
        cols = st.columns(3)

        for i, art in enumerate(items):
            with cols[i % 3]:
                st.markdown(
                    """
                    <div style='border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 10px; background-color: #f9f9f9;'>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(f"### {art['title']}")
                st.markdown(f"**Summary:** {art.get('summary', '')}")
                st.markdown(f"**Label:** {art.get('label', 'N/A')}")
                st.markdown(f"**Opportunity:** {art.get('opportunity_type', 'N/A')}")
                st.markdown(f"**Suggested Action:** {art.get('suggested_action', 'N/A')}")
                st.markdown(f"🔗 [Open Article]({art['url']})")

                cols_buttons = st.columns(2)
                with cols_buttons[0]:
                    if st.button("🔁 Reclassify", key=f"reclassify_{client}_{i}"):
                        new_label = "Actionable" if art["label"] == "Informational" else "Informational"
                        art["label"] = new_label
                        save_articles(articles)
                        st.rerun()

                with cols_buttons[1]:
                    if st.button("✅ Mark as Read", key=f"markread_{client}_{i}"):
                        art["read"] = True
                        save_articles(articles)
                        st.rerun()

                st.markdown("""</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
