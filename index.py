from flask import Flask, request, jsonify,render_template
import openai
import re
import speech_recognition as sr
from playsound import playsound
import psycopg2 

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
global conn
conn = psycopg2.connect(database="CodeGenerator", user="postgres", 
                        password="aryansaini9999", host="localhost", port="5432") 
global cur
cur = conn.cursor()

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
    return render_template('LogIn.html')

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
    
@app.route('/SignUp',methods=['POST'])
def SignUp():
    global cur
    global conn
    cur.close()
    conn.close()
    conn = psycopg2.connect(database="CodeGenerator", user="postgres",
                    password="aryansaini9999", host="localhost", port="5432") 
    cur = conn.cursor()
    try:
        cur.execute('''insert into users (name,password) values(%s,%s)''',(request.form['username'],request.form['password']))
        conn.commit()
        return render_template('LogIn.html',flag='true',message="You can Log in with your new account now")
    except Exception as e:
        print(e)
        return render_template('SignUp.html',flag='true',message="Username already exists!")

@app.route('/GoToSignUp',methods=['POST'])
def GoToSignUp():
    return render_template('SignUp.html')

@app.route('/GoToLogIn',methods=['POST'])
def GoToLogIn():
    return render_template('LogIn.html')

@app.route('/LogIn',methods=['POST'])
def LogIn():
    username=[]
    password=[]
    cur.execute('''select name,password from users''')
    data=cur.fetchall()
    i=0
    while i<len(data):
        username.append(data[i][0])
        password.append(data[i][1])
        i+=1
    i=0
    while i<len(data):
        if request.form['username']==username[i] and request.form['password']==password[i]:
            return render_template('index.html', title='AI Code Generator', message="{(code)}", history=history,prompts=prompts)
        i+=1
    return render_template('LogIn.html',flag="true",message="Incorrect Username or Password!")
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
