from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import Category, Location, Bus, Schedule, Booking

class CategorySchema(BaseModel):
    name :str
    description :str
    status : str
    date_created :datetime =datetime.now
    date_updated : datetime =datetime.now()
 
class LocationSchema(BaseModel):
    Location : str
    status : str
    date_created :datetime =datetime.now
    date_updated : datetime =datetime.now()

class BusSchema(BaseModel):
    bus_number :str
    category : CategorySchema
    seats : str
    status : str
    date_created :datetime =datetime.now
    date_updated : datetime =datetime.now()
    

class ScheduleSchema(BaseModel):
    bus: BusSchema
    depart: LocationSchema
    destination: LocationSchema
    code :str
    schedule :datetime
    fare :float
    status :str
    date_created :datetime =datetime.now
    date_updated :datetime =datetime.now()

class BookingSchema(BaseModel):
    code :str
    name :str
    schedule :str
    seats :int
    status:str


    class Config:
        model = Booking
        exclude = ['date_created', 'date_updated']

class ScheduleSchemaWithMethods(ScheduleSchema):
    count_available: int

    @classmethod
    def from_orm(cls, obj):
        instance = super().from_orm(obj)
        instance.count_available = obj.count_available()
        return instance

class BookingSchemaWithMethods(BookingSchema):
    total_payable: float

    @classmethod
    def from_orm(cls, obj):
        instance = super().from_orm(obj)
        instance.total_payable = obj.total_payable()
        return instance
