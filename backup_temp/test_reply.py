from generate_reply import generate_reply

tweet1 = "Just finished my morning trail run in the mountains! 🏃‍♂️⛰️"
tweet2 = "Looking forward to the AI conference next week."

print("Răspunsuri generate:")
print(f"- Tweet: {tweet1}\n  ➤ Reply: {generate_reply(tweet1)}\n")
print(f"- Tweet: {tweet2}\n  ➤ Reply: {generate_reply(tweet2)}")
