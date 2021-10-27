import io
from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import JSONResponse

from src import services

app = FastAPI(
    title="File Conversion API",
    description="A very simple API converts between different file formats such as csv, json, etc.",
    version=1.0,
)


@app.post("/csv_to_json/")
def create_archive(file: bytes = File(...), email: str = Body(...)):
    buffer = io.BytesIO(file)
    blob_uri = services.ProcessCsvToJson(buffer, email).process()
    return JSONResponse(content=None, status_code=201, headers={"Location": blob_uri})
