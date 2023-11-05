from flask import Flask, jsonify, request
from typing import Dict, Any
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
import mysql.connector
from langchain.schema import (
    HumanMessage, 
)
from mysql.connector import Error
import openai
import json
import os

load_dotenv()

app = Flask(__name__)

@app.route('/generate_challenges', methods = ['POST'])
def process_request():
    user_data = request.json
    if not user_data or not('data' in user_data and 'user_id' in user_data):
        return jsonify(error="Data should be a JSON Object with a 'data' and 'user_id' key"), 400

    challenge_list = generate_challenges(user_data)
    if not challenge_list:
        return jsonify("Failed to get response from GPT"),500
    
    success = write_challenges_to_database(challenge_list, user_data['user_id'])
    if not success:
        return jsonify("Failed to write challenges to database"), 500
    return jsonify({"success": True, "message": "Challenges created successfully."}), 201

def generate_challenges(user_data: str) ->  Dict[str, Any]:
    openai.api_key = os.getenv("OPEN_AI_API_KEY")
    openai.api_type = "azure"
    model_name = "tiaa-gpt-4-32k"
    gpt4 = AzureChatOpenAI(
        openai_api_base="https://tiaa-openai-azure-sweden.openai.azure.com",
        openai_api_version="2023-07-01-preview",
        deployment_name=model_name,
        openai_api_key="be9bdecc8bf64e85bde69c04b2ad56f8",
        openai_api_type="azure",
        temperature=0
    )
    prompt = HumanMessage(content=f"Given these responses by the user in {user_data}, return 25 short phrases to encourage them regarding investment and retirement. You are speaking to Gen Zers, talk in a Apple-esque professional but laid back tone. Pretend as if you are talking to them personally, don't make vague statements that could be directed at anyone. Format your response as a JSON list. Do not number each entry in this list.")
    output=gpt4(messages=[prompt])
    return json.loads(output.content)

def write_challenges_to_database(challenge_list: list, user_id: int): 
    connection = mysql.connector.connect(
            host = "54.210.73.216",
            user = 'pknadimp',
            password = "1234",
            database = "Money"
        )
    try:
        
        if connection.is_connected():
            cursor = connection.cursor()

            # The query that will be used to insert a sinlge challenge
            insert_query = "INSERT INTO Money.Challenges (user_id, challenge) VALUES (%s, %s)"
            # Compile the data in pairs for each row
            data_to_insert = [(user_id, challenge) for challenge in challenge_list]

            # Execute the SQL query for each user_id-challenge pair
            cursor.executemany(insert_query, data_to_insert)

            #Commit the transaction
            connection.commit()

            print(f"{cursor.rowcount} challenges inserted successfully for user {user_id}")
            return True

    except Error as e:
        print(f"Error while connecting to MySQL, {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    app.run(debug=True)