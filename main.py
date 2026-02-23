from fastapi import FastAPI
from routes import router


app = FastAPI()

app.include_router(router)


@app.get("/")
def read_root():
    return {"Message": "Aaja aaja....."}


@app.get("/health")
def health_status():
    return {"status": "ek dum fit bhai!"}
