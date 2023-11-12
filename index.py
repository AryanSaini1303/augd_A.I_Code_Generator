from flask import Flask, request, jsonify,render_template
import openai
import re
import speech_recognition as sr
from playsound import playsound

app = Flask(__name__)
# Set your OpenAI API key
with open('api.txt', 'r') as file:
    apiKey = file.read().strip()
openai.api_key = apiKey
r=sr.Recognizer()

history=[]
prompts=[]
language=""#defining a global variable to use it in any routes
user_question=""

def voice_to_text():
    while True:
        with sr.Microphone() as source:
            print("\n"+"Say something!")
            playsound("./mixkit-click-error-1110.wav")
            # audio=r.record(source,duration=5)
            r.pause_threshold=0.8#seconds
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio,language='en-IN')
            # print("You said: ", text)
            break
        except sr.UnknownValueError:
            print("Can't understand audio, Try again.")
            continue
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            continue
    return text

@app.route('/')
def index():
    return render_template('index.html', title='AI Code generator', message='{(Code)}',history=history,prompts=prompts)

@app.route('/language', methods=['POST'])
def languageSelected():
    global language # this is the syntax to use a global variable
    language=request.form['value']
    return language

@app.route('/voice',methods=['POST'])
def voice():
    global user_question
    user_question=voice_to_text()
    print(voice_to_text())
    try:
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
    
@app.route('/ask', methods=['POST'])
def ask_openai():
    global user_question
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
