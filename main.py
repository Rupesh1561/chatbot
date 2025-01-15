#required libraries and consts
import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()


#function to load prompt with dynamic values
def load_prompt(file_path,**query):
    with open(file_path, "r") as file:
        template = file.read()
    return template.format(**query)





#function to interact with hf_api
def hf_api(prompt):
    # Set the API URL and headers
    url = os.getenv("API_URL")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv("API_KEY")}"  # Replace with your actual API key
    }

    # Define the data payload for the request
    payload = {
        "inputs":f"{prompt}"
    }

    # Send the POST request to the API
    response = requests.post(url, headers=headers, json=payload)
    result=response.json()
    if response.status_code==200:
        #extracting exact json data from response
        text=result[0]['generated_text']
        start = text.find("`") + 7
        end = text.find("`",start)
        return text[start:end]
    else:
        return "Failed"



#function to calculate priority scores for each idea
def priority_calculate(relevance, impact, feasibility):
    # Give more priority to relevance, then impact, then feasibility
    score = (0.5 * relevance + 0.3 * impact + 0.2 * feasibility)
    return round(score)


#handle errors while user inputs
def handle_choice():
    try:
        choices = input("Please choose two ideas by typing their numbers (e.g., 1,3) (for exit type quit or q).")
        if choices=="q" or choices=="quit":
            return "quit"
        l=choices.split(",")
        res=[int(i) for i in l]        
        return (res[0],res[1])
    except:
        print("something wrong with your input")
        return handle_choice()



while True:
    print("\n######################## I am your Idea Generator Bot to Help You ############################\n")
    s=input("Ask Me (for exit type quit or q) :")
    if s=="q" or s=="quit":
        break
    loaded_prompt=load_prompt("prompts/idea_gen_prompt.txt",ideas_for=s)

    response=hf_api(loaded_prompt) #call hf_api function to invoke api call to chagpt with the res prompt from above line
    if response=="Failed":
        print("something wrong with the response")
        break
    response=json.loads(response)
    i=1
    for curr in response:
        idea,rel,imp,fea=curr["idea"],curr["relevance"],curr["impact"],curr["feasibility"]
        score=priority_calculate(rel,imp,fea)
        print(f"{i}. {idea} --> {score}")
        i+=1                 #response from the hf_api --> extract ideas and calculate their priority score 1 to 5 and display
    #choice for user to select particular ideas that user likes 
    print("\n")
    choice=handle_choice()
    if choice=="quit":
        break
    x,y=choice
    #call hf_api function to invoke api call to hf_api with description prompt with choose ideas 
    desc=load_prompt("prompts/description.txt",idea1=response[x-1]["idea"],idea2=response[y-1]["idea"])
    response2=hf_api(desc)
    if response2=="Failed":
        print("something wrong with the response")
        break
    
    response2=json.loads(response2)
    idea1,idea2=response2["idea1"],response2["idea2"]
    print(f'\nidea1:  {idea1}\n')
    print(f'idea2:  {idea2}\n')
    break