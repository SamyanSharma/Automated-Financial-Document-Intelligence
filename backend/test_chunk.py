from services.chunk_service import split_text


text = """
Apple reported total net sales of approximately 394 billion dollars.
The company operates in several geographic regions and product categories.
Its financial statements include information about revenue, liabilities,
assets, operating expenses and other financial metrics.
""" * 20


chunks = split_text(text)

print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks):

    print("\n--------------------")
    print("CHUNK:", i)
    print("--------------------")

    print(chunk[:300])