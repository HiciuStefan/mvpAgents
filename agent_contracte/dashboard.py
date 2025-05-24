import pandas as pd
import streamlit as st
from main import get_all
import json
from google_3 import main

main()

# Run the workflow
results = get_all()

# Streamlit App UI
st.title("Contract Processor")

# Display total classified emails
st.metric(f"Total contracts processed: {len(results)}", "")

contracts = [json.loads(c) for c in results]

flat_contracts = []
for c in contracts:
	flat_contracts.append({
		"Firma": c["nume_firma"],
		"CUI": c["cui"],
		"Adresa": c["adresa_sediu"],
		"Reprezentant": c["reprezentant_legal"],
		"Start": c["data_semnare"]["start_date"],
		"End": c["data_semnare"]["end_date"],
		"Durata": c["data_semnare"]["length"],
		"Tip": c["contract_value"]["type"],
		"Valoare": c["contract_value"]["value"],
		"Monedă": c["contract_value"]["currency"],
	})

# Convert to DataFrame
df = pd.DataFrame(flat_contracts)

# Show in Streamlit
st.dataframe(df, use_container_width=True)