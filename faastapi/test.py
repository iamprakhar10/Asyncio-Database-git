from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check():
    return "Heathy server"

@app.get("/")
def health_check2():
    return {"Welcome":'prakhar'}



@app.get('/patient/{patient_id}')
def view_patient(patient_id: int):
    return f"Patient no. -> {patient_id}, age-> {2*patient_id}"
