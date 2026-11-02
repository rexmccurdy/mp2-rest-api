import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, ProcessConfig, setup_logging, ProcessingReport, log_requests
from data_pipeline import create_cleaning_report, process_data, validate_dataframe


setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
app.middleware("http")(log_requests)
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    if Path(file.filename or "").suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
        logger.warning(f"Failed to read CSV file: {file.filename}")
        raise HTTPException(status_code=400, detail="Invalid CSV file.")

    dataset_id = storage.save(df, file.filename)
    return DatasetInfo(
        id=dataset_id,
        filename=file.filename,
        rows=len(df),
        columns=len(df.columns),
        column_names=list(df.columns))
    

@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    df = storage.get(dataset_id)
    if df is None:
        logger.warning(f"Dataset with ID {dataset_id} not found.")
        raise HTTPException(status_code=404, detail="Dataset not found.")

    records = json.loads(df.head(limit).to_json(orient="records"))
    return {"id": dataset_id, "data": records, "total_rows": len(df)}


@app.post(
    "/datasets/{dataset_id}/process",
    response_model=ProcessingReport
)
def process_dataset(dataset_id: int, config: ProcessConfig):
    df = storage.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    config_dict = config.model_dump()
    for col in config_dict["validation"]["required_columns"]:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

    try:
        pre_validation = df.copy()
        validation = config_dict["validation"]
        df = validate_dataframe(df, required_columns=validation["required_columns"], numeric_columns=validation["numeric_columns"])     
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    post_validation = df.copy()
    try:
        df = process_data(df, config_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    cleaning_report = create_cleaning_report(post_validation, df)
    storage.update(dataset_id, df)
    logger.info(f"Dataset {dataset_id} processed. "
                f"{len(post_validation) - len(df)} rows removed. "
                f"Cleaning report: {cleaning_report}")
    return ProcessingReport(
        id=dataset_id,
        validation_rows_removed=len(pre_validation) - len(post_validation),
        cleaning_report=cleaning_report
    )
