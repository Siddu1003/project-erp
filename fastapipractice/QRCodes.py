# student_crud.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.responses import StreamingResponse
import qrcode
import io
import json
from fastapi import FastAPI, File, UploadFile, HTTPException,Query
import cv2
import numpy as np
from io import BytesIO



DATABASE_URL = "mysql+pymysql://root:@localhost/qrstudata"

engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 5})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    course = Column(String(100))



app = FastAPI(title="Student QR Generation API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@app.get("/students/" , tags=["Student Data"])
def Get_all_Students_Data(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return [
        {
            "student_id": student.student_id,
            "name": student.name,
            "course": student.course
        }
        for student in students
    ]



@app.post("/students/" , tags=["Student Data"])
def create_student_Data(student_id: str, name: str, course: str, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.student_id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Student ID: {student_id} already exists.")
                            

    new_student = Student(student_id=student_id, name=name, course=course)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {"message": "Student created successfully", "student": {
        "student_id": new_student.student_id,
        "name": new_student.name,
        "course": new_student.course
    }}


@app.get("/students/{student_id}" , tags=["Student Data"])
def read_student_Data(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"student_id": student.student_id, "name": student.name, "course": student.course}


@app.put("/students/{student_id}" , tags=["Student Data"])
def update_student_Data(student_id: str, name: str = None, course: str = None, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if name:
        student.name = name
    if course:
        student.course = course
    db.commit()
    db.refresh(student)

    return {"message": "Student updated successfully", "student": {
        "student_id": student.student_id,
        "name": student.name,
        "course": student.course
    }}




@app.delete("/students/{student_id}", tags=["Student Data"])
def delete_student_Data(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    return {"message": f"Student {student_id} deleted successfully"}




@app.get("/students/{student_id}/qr", tags=["QR Codes"])
def generate_student_qr(student_id: str, download: bool = Query(False), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student_data = {
        "student_id": student.student_id,
        "name": student.name,
        "course": student.course
    }

    qr_img = qrcode.make(json.dumps(student_data))
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    buf.seek(0)

    if download:
        
        return StreamingResponse(
            buf,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={student.student_id}.png"}
        )

    
    return StreamingResponse(buf, media_type="image/png")






@app.post("/read-qr/", tags=["QR Codes"])
async def QR_Reading(file: UploadFile = File(...)):
   
    image_data = await file.read()
    np_arr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img)

    if not data:
        raise HTTPException(status_code=404, detail="QR code not detected")

    return {"decoded_data": data}
