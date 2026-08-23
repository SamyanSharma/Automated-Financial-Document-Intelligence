from services.chunk_service import split_text


text = """
Apple reported revenue growth.
Operating income increased.
The company invested in AI.
"""


chunks = split_text(text)


for chunk in chunks:
    print("----------------")
    print(chunk)