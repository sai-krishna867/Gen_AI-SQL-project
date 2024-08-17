import streamlit as st
import os
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
# Get the API key from environment variables
api_key = st.secrets["api"]
genai.configure(api_key=api_key)

def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content([prompt[0],question])
    return response.text
def read_sql_query(sql,db):
    conn=sqlite3.connect(db)
    cur=conn.cursor()
    cur.execute(sql)
    rows=cur.fetchall()
    conn.commit()
    conn.close()
    results = [row[0] for row in rows]
    return results
prompt=[
    """
    you are an expert in converting English questions to SQL queries!
The SQL database contains the following tables and columns:

Patient: PatientID, Name, Age, Gender, Blood Group
Doctor: DoctorID, Name
Hospital: HospitalID, Name
InsuranceProvider: InsuranceID, Name
Disease: DiseaseID, DiseaseName
Medication: MedicationID, MedicationName
AdmissionType: AdTypeID, Type
Result: ResultID, ResultType
Admission: ID, PatientID, DoctorID, HospitalID, InsuranceID, DiseaseID, MedicationID, AdTypeID, ResultID, DateofAdmission, BillingAmount, RoomNumber, DischargeDate
For example:

How many patients are there?
The SQL command will be something like this: SELECT COUNT(*) FROM Patient;

List all doctors who have worked in a specific hospital.
The SQL command will be something like this: SELECT * FROM Doctor
WHERE DoctorID IN (SELECT DoctorID FROM Admission WHERE HospitalID = [specific_hospital_id]);

Show all admissions for a specific disease type.
The SQL command will be something like this: SELECT * FROM Admission
WHERE DiseaseID = (SELECT DiseaseID FROM Disease WHERE DiseaseName = "[specific_disease_name]");

What is the total billing amount for admissions of a certain type?
The SQL command will be something like this: SELECT SUM(BillingAmount) FROM Admission
WHERE AdTypeID = (SELECT AdTypeID FROM AdmissionType WHERE Type = "[specific_admission_type]");

Also, ensure the SQL code does not include ``` in the beginning or end and the word SQL in the output.
    """
]
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

question=st.text_input("Input: ",key="input")

submit=st.button("Query the Database")

# if submit is clicked
if submit:
    response=get_gemini_response(question,prompt)
    try:
    #print(response)
        if response.split()[0].lower()=='select':
            response=read_sql_query(response,"healthcare.db")
            val = question.split(" ")
            val = val [1:]
            val = " ".join(val)
            st.subheader("")
            st.header(val+ " is/are -")
            for row in response:
                #print(row)
                st.write(row)
        else:
            st.write("Cannot query this from database, kindly Rephrase the statement")
    except:
            st.write("Cannot query this from database, kindly Rephrase the statement.")
    