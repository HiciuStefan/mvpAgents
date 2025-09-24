import streamlit as st
from state_manager import load_existing_tweets, update_tweet_status, update_tweet_category, add_reply_to_tweet, save_new_tweets
from reply_helper import post_reply
from generate_reply import generate_reply
from urllib.parse import urlparse
from main import main as run_scraper

st.set_page_config(page_title="Smart Tweet Responder", layout="wide")
st.title("🤖 Smart Tweet Responder")

# 🔁 Run scraping only once at app launch
if "scraping_done" not in st.session_state:
    with st.spinner("🔁 Se caută tweeturi noi..."):
        run_scraper()
    st.session_state.scraping_done = True

# 📂 Load all tweets
all_tweets = load_existing_tweets()

# 🔃 Organize tweets by account and category
pending = [t for t in all_tweets if t.get("status") == "pending"]
pending_by_account = {}

for tweet in pending:
    account = urlparse(tweet["url"]).path.strip("/").split("/")[0]
    if account not in pending_by_account:
        pending_by_account[account] = {
            "url": f"https://twitter.com/{account}",
            "tweets": []
        }
    pending_by_account[account]["tweets"].append(tweet)

if not pending_by_account:
    st.info("✅ Nu sunt tweeturi noi de procesat.")
    st.stop()

# 🖼️ Display each account with categorized tweets
for account, data in pending_by_account.items():
    with st.container():
        st.markdown("""
            <div style='border: 2px solid #ccc; border-radius: 12px; padding: 16px; margin-bottom: 32px; background-color: #f9f9f9;'>
        """, unsafe_allow_html=True)

        st.markdown(f"### 🔗 [{data['url']}]({data['url']})")

        important = [t for t in data["tweets"] if t.get("category") == "important"]
        neutral = [t for t in data["tweets"] if t.get("category") == "neutral"]

        st.markdown(f"📌 **{len(important)} importante** | 💬 **{len(neutral)} neutre**")

        st.markdown("""
            <div style='max-height: 500px; overflow-y: auto; padding-right: 8px;'>
        """, unsafe_allow_html=True)

        for tweet in data["tweets"]:
            st.markdown(f"**📝 Tweet:** {tweet['text']}")
            st.markdown(f"🔍 Clasificare: `{tweet.get('category', 'unknown')}`")

            col1, col2, col3 = st.columns(3)

            if tweet.get("category") == "neutral":
                with col1:
                    if st.button("✅ Marchează ca important", key=f"cat_imp_{tweet['id']}"):
                        update_tweet_category(tweet["id"], "important")
                        st.rerun()
            elif tweet.get("category") == "important":
                with col1:
                    if st.button("⬅️ Marchează ca neutru", key=f"cat_neu_{tweet['id']}"):
                        update_tweet_category(tweet["id"], "neutral")
                        st.rerun()

            if "reply" not in tweet:
                with col2:
                    if st.button("🧠 Generează răspuns GPT", key="gen_" + tweet["id"]):
                        reply = generate_reply(tweet["text"])
                        add_reply_to_tweet(tweet["id"], reply, category=tweet.get("category", "neutral"))
                        st.success("Răspuns generat.")
                        st.rerun()
                with col3:
                    if st.button("❌ Nu răspund la acest tweet", key="reject_" + tweet["id"]):
                        update_tweet_status(tweet["id"], "rejected")
                        st.warning("Tweet respins.")
                        st.rerun()
            else:
                st.markdown("**🗣️ Răspuns propus:**")
                st.code(tweet["reply"])
                col_post, col_cancel = st.columns(2)
                with col_post:
                    if st.button("📤 Postează răspunsul", key="post_" + tweet["id"]):
                        rezultat = post_reply(tweet["url"], tweet["reply"])
                        update_tweet_status(tweet["id"], "posted")
                        st.success(rezultat)
                        st.rerun()
                
                with col3:
                    if st.button("❌ Nu răspund la acest tweet", key="reject_" + tweet["id"]):
                        update_tweet_status(tweet["id"], "rejected")
                        st.warning("Tweet respins.")
                        st.rerun()
            
                with col_cancel:
                    if st.button("❌ Nu postez răspunsul", key="no_post_" + tweet["id"]):
                        update_tweet_status(tweet["id"], "rejected")
                        st.warning("Postare anulată.")
                        st.rerun()

        st.markdown("""</div></div>""", unsafe_allow_html=True)
