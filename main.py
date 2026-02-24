from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI
from exceptions import (
    integrity_exception_handler,
    global_exception_handler,
    validation_exception_handler,
)
from routes.createadmin import router
from routes.userroutes.postapis import userRouter
from routes.userroutes.getapis import userGetRouter
from routes.tasksroutes.postapis import taskRouter
from routes.tasksroutes.updateapis import taskUpdateRouter
from routes.teamroutes.postapis import teamRouter
from fastapi.exceptions import RequestValidationError

app = FastAPI()


app.add_exception_handler(IntegrityError,integrity_exception_handler)
app.add_exception_handler(Exception,global_exception_handler)
app.add_exception_handler(RequestValidationError,validation_exception_handler)


app.include_router(router)
app.include_router(userRouter,prefix="/api/user")
app.include_router(userGetRouter,prefix="/api/user")
app.include_router(taskRouter,prefix="/api/task")
app.include_router(taskUpdateRouter,prefix="/api/task")
app.include_router(teamRouter,prefix="/api/team")


@app.get("/")
def read_root():
    return {"Message": "Aaja aaja....."}


@app.get("/health")
def health_status():
    return {"status": "ek dum fit bhai!"}
