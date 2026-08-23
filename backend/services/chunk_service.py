from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str) -> list[str]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )

    chunks = splitter.split_text(text)

    return chunks