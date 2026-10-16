from fastapi import FastAPI, Path, HTTPException, Query

app = FastAPI()

patients = {}

@app.get("/health")
def health_check():
    return "Heathy server"

@app.get("/")
def health_check2():
    return {"Welcome":'prakhar'}



@app.get('/patient/{patient_id}')
def view_patient(patient_id: int = Path(
    ..., description='ID of the patient inn daatabasse',
    example=32
)):
    if patient_id == 1390:
        raise HTTPException(
            status_code=404,
            detail="Patient nahi hai"
        )
    return f"Patient no. -> {patient_id}, age-> {2*patient_id}"



