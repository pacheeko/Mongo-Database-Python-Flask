import pymongo
from pymongo import MongoClient
import ast

cluster = MongoClient(
    "mongodb+srv://Sean:XI8C0a174x0IbIG3@cluster0.ejiha.mongodb.net/Degree_Builder?retryWrites=true&w=majority")
db = cluster["Degree_Builder"]
# !!! <-- attempt to insert into Test_Course collection; once compilation is successful, then...
collection = db["Test_Course"]
# collection = db["Course"]                 # <-- run with Course collection

f = open("BraydonCourseListComplete.txt")   # import course list .txt

for line in f:
    course = ast.literal_eval(line)         # converts text to dictionary
    collection.insert_one(course)           # inserts each line of the course
