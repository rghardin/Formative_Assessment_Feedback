# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 14:35:13 2025

@author: robert.hardin

Add following functionality:
1. Folder and file selection for output file
2. Entry of Assignment name and ID for output file
3. List and choose LLM
4. Allow for cut and paste of question and answer text and editing
5. Upload materials to use RAG with AI Chat
6. Generate and select question/solution from uploaded materials
7. Multiple questions on an assessment
8. Better error handling

"""

import requests
import streamlit as st
from io import StringIO
import pandas as pd
import csv

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

question_file = st.file_uploader("Choose the question file", type="txt")
if question_file is not None:
    question_IO = StringIO(question_file.getvalue().decode("utf-8"))
    question_string = question_IO.read()
    st.write(question_string) 
    
solution_file = st.file_uploader("Choose the solution file", type="txt")
if solution_file is not None:
    solution_IO = StringIO(solution_file.getvalue().decode("utf-8"))
    solution_string = solution_IO.read()
    st.write(solution_string)

studentresponses_file = st.file_uploader("Choose the file exported from Canvas with student responses", type="csv")
if studentresponses_file is not None:
    df=pd.read_csv(studentresponses_file)
    st.dataframe(df)
    idlist = df.iloc[:,2].tolist()
    answerlist = df.iloc[:,8].tolist()
    i=0
    
if question_file is not None and solution_file is not None and studentresponses_file is not None:    
    for answer in answerlist:
        prompt = "The following formative assessment question was given to students:\n" + question_string + "\nA thorough and accurate response is given by:\n" + solution_string + "\nThe student's answer was:\n" + answer + "\nPlease provide feedback to the student."
        result=interact_with_model("protected.gpt-5", prompt)
        idlist[i]=[idlist[i], result['choices'][0]['message']['content']]
        i=i+1

    outputdf = pd.DataFrame(idlist, columns=['ID','Lecture 5 (2494906)']) 
    st.dataframe(outputdf)
    outputdf.to_csv(r"C:\Users\robert.hardin\OneDrive - Texas A&M University\BAEN 370 Lectures\Lecture 5 Comments Simulated.csv", index=False)
    #commentfieldnames=['ID', 'Lecture 5 (2494906)']
    #with open(r"C:\Users\robert.hardin\OneDrive - Texas A&M University\BAEN 370 Lectures\Lecture 5 Comments Simulated.csv", 'w', newline='') as csvfile:
        #writer = csv.writer(csvfile)
        #writer.writerow(commentfieldnames)
        #writer.writerows(idlist)
