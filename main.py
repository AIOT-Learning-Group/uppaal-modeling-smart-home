
import uvicorn
from fastapi import FastAPI, Body,  Request, Response, status
from starlette.middleware.sessions import SessionMiddleware
from service.simulation import router as sim_router
from service.resource import router as res_router


app = FastAPI()
app.include_router(sim_router)
app.include_router(res_router)
app.add_middleware(SessionMiddleware, secret_key="some-random-string")


@app.post("/api/submit-tap-rules")
async def submit_tap_rules(request: Request, raw_text: str = Body(...)):
    if 'tap-rules' in request.session.keys():
        print("old:", request.session['tap-rules'])
    request.session['tap-rules'] = raw_text
    return {"result": "success"}


@app.post("/api/submit-simulation-params")
async def submit_simulation_params(request: Request):
    data = await request.json()
    print(data)
    request.session['simulation-params'] = str(data)
    return {"result": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
