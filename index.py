from flask import Flask, request, jsonify,render_template
import openai
import re

app = Flask(__name__)
# Set your OpenAI API key
with open('api.txt', 'r') as file:
    apiKey = file.read().strip()
openai.api_key = apiKey

history=[]
prompts=[]
language=""#defining a global variable to use it in any routes
@app.route('/')
def index():
    return render_template('index.html', title='AI Code generator', message='{(Code)}',history=history,prompts=prompts)

@app.route('/language', methods=['POST'])
def languageSelected():
    global language # this is the syntax to use a global variable
    language=request.form['value']
    return language
    
@app.route('/ask', methods=['POST'])
def ask_openai():
    try:
        user_question = request.form['question']
        prompts.insert(0,user_question)
        if language=="python":
            user_question=user_question+" in python language"
        elif language=="c":
            user_question=user_question+" in c language"
        elif language=="java":
            user_question=user_question+" in java language"
        else:
            user_question=user_question+" in python language"
        # print(user_question)
        # user_question="code to print fibonacci series"
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "can you write code for me?"},
                {"role": "assistant", "content": "Of course I can, what code would you like to generate?"},
                {"role": "user", "content": user_question},
            ]
        )
        response = completion.choices[0].message.content
        
        def code(text):
            pattern = r"```(.*?)```"
            matches = re.findall(pattern, text, re.DOTALL)
            return ' '.join(matches)
        if language=="python":
            finalCode=code(response).replace("python","")
        elif language=="c":
            finalCode=code(response).replace("c","")
        elif language=="java":
            finalCode=code(response).replace("java","")
        else:
            finalCode=code(response).replace("python","")
        # print(finalCode)
        # print(response)
        history.insert(0,finalCode)
        # print(history)
        return render_template('index.html', title='AI Code Generator', message=finalCode, history=history,prompts=prompts)
        # return jsonify({'response': "'"+response+"'"})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
