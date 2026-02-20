# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 14:35:13 2025

@author: robert.hardin

Add following functionality:
1. Folder and file selection for output file- added 02/19/2026 RGH
2. Entry of Assignment name and ID for output file- added 02/18/2026 RGH
3. List and choose LLM
4. Allow for cut and paste of question and answer text and editing - added 02/19/2026 RGH
5. Upload materials to use RAG with AI Chat
6. Generate and select question/solution from uploaded materials
7. Multiple questions on an assessment- added 02/18/2026 RGH
8. Better error handling

"""

import requests
import streamlit as st
from io import StringIO
import pandas as pd
import csv

def call_models_api():
    url = "https://chat-api.tamu.ai/openai/models"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer sk-819211e660ad48b79c96110ac57bd0c0"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an exception for bad status codes
    
    return response.json()

def interact_with_model(chosen_model, my_query):
    url = "https://chat-api.tamu.ai/openai/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": chosen_model,
        "messages": [{"role": "user", "content": my_query}],
        "stream": False
    }
    response = requests.post(url, headers=headers, json=payload)  
    return response.json() #Returns LLM response as a json object
    
st.title("Formative Assessment Feedback Using TAMU AI Chat")

api_key = st.text_input("TAMU API Key", type="password")

#question_file = st.file_uploader("Choose the question file", type="txt")
#if question_file is not None:
    #question_IO = StringIO(question_file.getvalue().decode("utf-8"))
    #question_string = question_IO.read()
    #st.write(question_string) 

# Use a radio button to select the input method for solution- text entry or file upload
input_method = st.radio("Select your input method for the assessment solution:", ("Enter Text", "Upload File"))
if input_method == "Enter Text":
    solution_string = st.text_area("Enter solution here:", height=200)
elif input_method == "Upload File":
    solution_file = st.file_uploader("Choose the solution file", type=["txt","csv"])
    if solution_file is not None:
        solution_IO = StringIO(solution_file.getvalue().decode("utf-8"))
        solution_string = solution_IO.read()
        st.write(solution_string)

# Upload assessment quiz student analysis report file from Canvas
studentresponses_file = st.file_uploader("Choose the file exported from Canvas with student responses", type="csv")
if studentresponses_file is not None:
    df=pd.read_csv(studentresponses_file)
    st.dataframe(df)
    idlist = df.iloc[:,2].tolist()
    column_names = df.columns
    number_questions = round((len(column_names)-11)/2)
    questionlist = []
    answerlist = []
    for j in range(number_questions):
        #Remove question number from Canvas export
        first_space = column_names[8+j*2].find(" ")
        question = column_names[8+j*2][first_space+1:]
        #Create a list of questions and a nested list of answers to each question for each student
        questionlist.append(question)
        answerlist.append(df.iloc[:,8+j*2].tolist())
     
assignment_name = st.text_input("Canvas assignment name and ID, format needs to match name and number in gradebook export")
default_filename = assignmentname + ".csv"
comments_filename = st.text_input("Enter the file name to save the csv file with comments. To save to a specific folder, enable \"Ask where to save each file before downloading\" in your browser settings.", value=default_filename)

if st.button("Provide Feedback"):    
    feedback_bar = st.progress(0, text=f"Processing feedback for {str(len(df))} students.")
    for i in range(len(df)):
        feedback_bar.progress(i/len(df), text=f"Processing feedback for {str(len(df))} students.")
        prompt = "The following formative assessment was given to students:\n" 
        for j in range(number_questions):
            prompt = prompt + str(j+1) + "." + questionlist[j] + "\n"
        prompt = prompt + "A thorough and accurate response is given by:\n" + solution_string + "\nThe student's answer was:\n" 
        for j in range(number_questions):
            prompt = prompt + str(j+1) + "." + str(answerlist[j][i]) + "\n"
        prompt = prompt + "Please provide feedback to the student."
        
        result=interact_with_model("protected.gpt-5", prompt)
        idlist[i]=[idlist[i], result['choices'][0]['message']['content']]
        
    outputdf = pd.DataFrame(idlist, columns=['ID',assignment_name]) 
    st.dataframe(outputdf, hide_index=True)
    outputcsv = outputdf.to_csv(index=False).encode("utf-8")
    st.download_button(label="Download comment file", data=outputcsv, file_name=comments_filename,  mime="text/csv", icon=":material/download:")
