import streamlit as st
from email_agent import workflow  # Import the workflow
import json

# Run the workflow
result = workflow.invoke({})

# Extract necessary data
emails = result.get("emails", [])
logs = result.get("logs", [])
filtered_emails = result.get("filtered_emails", [])

# Count total categorized emails
total_classified = len(emails)

# Get label statistics
label_counts = {}
for email in emails:
    label = email.get("tag", "Unknown")
    label_counts[label] = label_counts.get(label, 0) + 1

# Streamlit App UI
st.title("📧 Email Classification Dashboard")

# Display total classified emails
st.metric("Total Emails Processed", total_classified)

# Show newly created labels log
if logs:
    st.subheader("🆕 Newly Created Labels")
    for log in logs:
        st.write(log)

# Show emails categorized under labels
st.subheader("📌 Email Categorization Stats")
st.write("Breakdown of emails classified under different labels:")
st.json(label_counts)  # Displays structured data

# Expandable list of categorized emails
st.subheader("📨 Classified Emails")
for label, count in label_counts.items():
    with st.expander(f"📌 {label} ({count} emails)"):
        for email in emails:
            if email.get("tag") == label:
                st.write(f"**Subject:** {email.get('subject', 'No Subject')}")
                st.write(f"**Sender:** {email.get('sender', 'Unknown')}")
                st.write(f"**Snippet:** {email.get('snippet', 'No Preview')}")
                st.divider()

# Show filtered urgent/negative emails
if filtered_emails:
    st.subheader("🚨 Urgent or Negative Emails")
    for email in filtered_emails:
        st.write(f"**Subject:** {email.get('subject', 'No Subject')}")
        st.write(f"**Sender:** {email.get('sender', 'Unknown')}")
        st.write(f"**Sentiment:** {email.get('sentiment', 'Unknown')}")
        st.divider()
