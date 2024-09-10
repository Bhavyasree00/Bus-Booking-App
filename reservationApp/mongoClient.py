import pymongo
from datetime import datetime


client = pymongo.MongoClient("mongodb+srv://defensics:defensics&stack@cluster0.w4oeelf.mongodb.net/troven?retryWrites=true&w=majority")
# client = pymongo.MongoClient("mongodb+srv://vikas05:VikasKushwaha123@cluster0.w4oeelf.mongodb.net/troven?retryWrites=true&w=majority")
mongoDBClient = client["busTicket"]


busColl=mongoDBClient['bus_collection']
categoriesColl=mongoDBClient['category_collection']
tripsColl=mongoDBClient['trips_collection']
locationCOll=mongoDBClient['locations']
schedulesColl=mongoDBClient['schedules']
bookingsColl=mongoDBClient['booking_collection']

categoryData={
    "name":"sleeper",
    "description":"TS 28 WS 2387",
    "date_created":datetime.now(),
    "date_updated":datetime.now(),
    "status":1

}
tripData={
    "code":23455,
    "bus":"Volve",
    "deprt":"sleeper",
    "destination":"Delhi",
    "schedule":datetime.now(),
    "fare":876,
    "status":1,
    "date_created":datetime.now(),
    "date_updated":datetime.now()


}

# categoriesColl.insert_one(categoryData)
# tripsColl.insert_one(tripData)


# busColl.insert_one(data)

print("Database created")


