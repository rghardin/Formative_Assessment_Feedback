# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 14:35:13 2025

@author: robert.hardin

Add following functionality:
1. Folder and file selection for output file
2. Entry of Assignment name and ID for output file- added 02/18/2026 RGH
3. List and choose LLM
4. Allow for cut and paste of question and answer text and editing
5. Upload materials to use RAG with AI Chat
6. Generate and select question/solution from uploaded materials
7. Multiple questions on an assessment- added 02/18/2-26 RGH
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

#question_file = st.file_uploader("Choose the question file", type="txt")
#if question_file is not None:
    #question_IO = StringIO(question_file.getvalue().decode("utf-8"))
    #question_string = question_IO.read()
    #st.write(question_string) 
    
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
    column_names = df.columns
    number_questions = (len(column_names)-11)/2
    questionlist = []
    answerlist = []
    for j in range(number_questions):
        questionlist.append(column_names[8+j*2])
        answerlist.append(df.iloc[:,8+j*2].tolist())
st.text(str(number_questions))       
assignmentname = st.text_input("Canvas assignment name and ID, format needs to match name and number in gradebook export")    

if st.button("Provide Feedback"):    
    for i in range(len(df)):
        prompt = "The following formative assessment question was given to students:\n" 
        for j in range(number_questions):
            prompt = prompt + str(j+1) + "." + questionlist[j] + "\n"
        prompt = prompt + "A thorough and accurate response is given by:\n" + solution_string + "\nThe student's answer was:\n" 
        for j in range(number_questions):
            prompt = prompt + str(j+1) + "." + answerlist[j][i] + "\n"
        prompt = prompt + "Please provide feedback to the student."
        
        result=interact_with_model("protected.gpt-5", prompt)
        idlist[i]=[idlist[i], result['choices'][0]['message']['content']]
        
    outputdf = pd.DataFrame(idlist, columns=['ID',assignmentname]) 
    st.dataframe(outputdf)
    outputdf.to_csv().encode("utf-8")

    st.download_button(label="Download comment file", data=outputdf, filename="comments.csv",  mime="text/csv", icon=":material/download:" )
   
    #outputdf.to_csv(r"C:\Users\robert.hardin\OneDrive - Texas A&M University\BAEN 370 Lectures\Lecture 5 Comments Simulated.csv", index=False)
    #commentfieldnames=['ID', 'Lecture 5 (2494906)']
    #with open(r"C:\Users\robert.hardin\OneDrive - Texas A&M University\BAEN 370 Lectures\Lecture 5 Comments Simulated.csv", 'w', newline='') as csvfile:
        #writer = csv.writer(csvfile)
        #writer.writerow(commentfieldnames)
        #writer.writerows(idlist)






