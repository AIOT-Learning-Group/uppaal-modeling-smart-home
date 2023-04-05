import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from service.simulation import router as sim_router
from service.resource import router as res_router
from service.synthesization import router as syn_router

app = FastAPI()
app.include_router(res_router)
app.include_router(syn_router)
app.include_router(sim_router)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
