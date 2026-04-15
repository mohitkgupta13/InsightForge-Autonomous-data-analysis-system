from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.data_cleaner import clean_data
from services.analyzer import extract_insights

app = FastAPI(title="InsightForge Data Phase 1 API")

# Update CORS to allow any origin for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "InsightForge API is running"}

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        # Read the uploaded file into memory
        contents = await file.read()
        
        # 1. Clean Data
        df_cleaned = clean_data(contents)
        
        # 2. Extract Insights
        insights = extract_insights(df_cleaned)
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
