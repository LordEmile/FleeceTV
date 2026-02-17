from fastapi import FastAPI

app = FastAPI()



@app.get("/health")
def chek_health():
    return{"status":"ok"}