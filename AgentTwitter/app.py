import streamlit as st
from state_manager import load_existing_tweets, update_tweet_status, add_reply_to_tweet
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
pending = [t for t in all_tweets if t.get("status") == "pending"]
pending_by_account = {}

# 🔄 Group by Twitter account
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

# 📈 Display each account in a separate visual card with scrollable tweet section
for account, data in pending_by_account.items():
    with st.container():
        st.markdown("""
            <div style='border: 2px solid #ccc; border-radius: 12px; padding: 16px; margin-bottom: 32px; background-color: #f9f9f9;'>
        """, unsafe_allow_html=True)

        st.markdown(f"### 🔗 [{data['url']}]({data['url']})")
        st.markdown(f"📄 **{len(data['tweets'])} tweeturi noi**")

        try:
            from generate_summary import generate_summary
            summary = generate_summary([t["text"] for t in data["tweets"]])
            st.caption(f"🧠 *{summary}*")
        except:
            st.caption("(Sumar AI indisponibil)")

        # Scrollable tweet zone
        st.markdown("""
            <div style='max-height: 400px; overflow-y: auto; padding-right: 8px;'>
        """, unsafe_allow_html=True)

        for tweet in data["tweets"]:
            st.markdown(f"**📝 Tweet:** {tweet['text']}")

            if "reply" in tweet:
                st.markdown("**🗣️ Răspuns generat:**")
                st.code(tweet["reply"])

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📤 Postează răspunsul", key="post_" + tweet["id"]):
                        rezultat = post_reply(tweet["url"], tweet["reply"])
                        update_tweet_status(tweet["id"], "posted")
                        st.success(rezultat)
                        st.rerun()
                with col2:
                    if st.button("❌ Nu mai vreau să răspund", key="reject_after_reply_" + tweet["id"]):
                        update_tweet_status(tweet["id"], "rejected")
                        st.warning("Tweet respins.")
                        st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🧠 Generează răspuns GPT", key="gen_" + tweet["id"]):
                        reply = generate_reply(tweet["text"])
                        add_reply_to_tweet(tweet["id"], reply)
                        st.success("Răspuns generat.")
                        st.rerun()
                with col2:
                    if st.button("❌ Nu răspund la acest tweet", key="reject_" + tweet["id"]):
                        update_tweet_status(tweet["id"], "rejected")
                        st.warning("Tweet respins.")
                        st.rerun()

        st.markdown("""</div>""", unsafe_allow_html=True)
        st.markdown("""</div>""", unsafe_allow_html=True)
