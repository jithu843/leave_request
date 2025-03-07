import datetime
from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel,Field
from requests import Session
from sqlalchemy import Column, Date, Integer, String, create_engine, func
from sqlalchemy.orm import create_session,sessionmaker,declarative_base

#Database Configuration
DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(DATABASE_URL,connect_args={"check same thread": False},echo=True)
engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit= False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#Models
print("hello")
class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    print("welcome model")
    id = Column(Integer,primary_key = True,index=True)
    employee_id = Column(String,index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    leave_type = Column(String)
    reason = Column(String)
    status = Column(String,default="Pending")
    created_at = Column(Date,default=datetime.date.today())
    working_days = Column(Integer)
    print("working")
# try:
Base.metadata.create_all(bind = engine)
print("Hi")

#Pydantic Schema
class LeaveRequestCreate(BaseModel):
    employee_id: str
    start_date: datetime.date
    end_date: datetime.date
    leave_type: str = Field(...,pattern=r"^(ANNUAL|SICK|PERSONAL)$")
    reason: str = Field(...,min_length=10)

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Utility Function
def calculate_working_days(start_date,end_date):
    days = (end_date - start_date).days + 1
    weekdays = sum(1 for day in range(days) if (start_date + datetime.timedelta(days=day)).weekday()<5)
    return weekdays

#FastAPI App
app = FastAPI()
@app.post("/api/v1/leave_requests")
def create_leave_request(request:LeaveRequestCreate,db:Session = Depends(get_db)):
    if request.end_date <= request.start_date:
        raise HTTPException(status_code=400,detail="end date must after start date is 14.")
    working_days = calculate_working_days(request.start_date,request.end_date)
    if working_days > 14:
        raise HTTPException(status_code=400, detail= "Maximum consecutive leave days is 14.")
    overlap = db.query(LeaveRequest).filter(LeaveRequest.employee_id == request.employee_id,
                                            LeaveRequest.start_date <= request.end_date,
                                            LeaveRequest.end_date >= request.start_date).first()
    if overlap:
        raise HTTPException(status_code=400,detail="Overlapping leave request exists")
    leave = LeaveRequest(employee_id = request.employee_id,
                         start_date = request.start_date,
                         end_date = request.end_date,
                         leave_type = request.leave_type,
                         reason = request.reason,
                         working_days = working_days)    
    db.add(leave)
    db.commit()
    db.refresh(leave)
    print(leave.created_at)
    return leave

@app.get("/api/v1/leave_requests/{employee_id}")
def get_leave_requests(employee_id:str,db: Session = Depends(get_db)):
    leaves = db.query(LeaveRequest).filter(LeaveRequest.employee_id == employee_id).all 
    # print(leaves)
    if not leaves:
        raise HTTPException(status_code=404,detail="No leave requests found")
    return leaves
