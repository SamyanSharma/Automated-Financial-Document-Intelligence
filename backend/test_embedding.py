from services.embedding_service import generate_embedding


text = """
Apple reported strong revenue growth during the financial year.
Total revenue increased compared with the previous year.
"""

embedding = generate_embedding(text)

print("Embedding generated")
print("Dimensions:", len(embedding))
print("First 5 values:", embedding[:5])