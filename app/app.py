import fastapi


app = fastapi.FastAPI(
    title = "Library RESTful API",
    version = "0.0.1",
    description = "A RESTful API for managing libraries"
)

@app.get("/")
def root():
    return {"message": "Hello World"}