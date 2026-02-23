from fastapi import FastAPI
from exceptions import integrity_exception_handler, global_exception_handler
from routes import router


app = FastAPI()


app.exception_handler(integrity_exception_handler)
app.exception_handler(global_exception_handler)


app.include_router(router)


@app.get("/")
def read_root():
    return {"Message": "Aaja aaja....."}


@app.get("/health")
def health_status():
    return {"status": "ek dum fit bhai!"}
