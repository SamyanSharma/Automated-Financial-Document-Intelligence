from fastapi import FastAPI

app = FastAPI(
    title="Financial Document Intelligence API"
)


@app.get("/")
def home():
    return {
        "message": "Financial AI Backend Running"
    }