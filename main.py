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
from routes.userroutes.updateapis import userUpdateRouter


from routes.tasksroutes.postapis import taskRouter
from routes.tasksroutes.updateapis import taskUpdateRouter
from routes.tasksroutes.bulks import taskBulkRouter
from routes.tasksroutes.deleteapi import deleteTaskRouter
from routes.tasksroutes.getapi import getTaskRouter

from routes.teamroutes.postapis import teamRouter
from routes.teamroutes.updateapis import teamUpdateRouter
from routes.teamroutes.getapis import teamGetRouter
from routes.teamroutes.deleteapis import deleteTeamRouter
from routes.teamroutes.invite_apis import inviteRouter

from fastapi.exceptions import RequestValidationError

app = FastAPI()


app.add_exception_handler(IntegrityError,integrity_exception_handler)
app.add_exception_handler(Exception,global_exception_handler)
# app.add_exception_handler(RequestValidationError,validation_exception_handler)


app.include_router(router)
app.include_router(userRouter,prefix="/api/user")
app.include_router(userGetRouter,prefix="/api/user")
app.include_router(userUpdateRouter,prefix="/api/user")


app.include_router(taskRouter,prefix="/api/task")
app.include_router(taskUpdateRouter,prefix="/api/task")
app.include_router(taskBulkRouter,prefix="/api/task")
app.include_router(deleteTaskRouter,prefix="/api/task")
app.include_router(getTaskRouter,prefix="/api/task")

app.include_router(teamRouter,prefix="/api/team")
app.include_router(inviteRouter,prefix="/api/team")
app.include_router(teamUpdateRouter,prefix="/api/team")
app.include_router(teamGetRouter,prefix="/api/team")
app.include_router(deleteTeamRouter,prefix="/api/team")


@app.get("/")
def read_root():
    return {"Message": "Aaja aaja....."}


@app.get("/health")
def health_status():
    return {"status": "ek dum fit bhai!"}
