from flask import Flask, request, jsonify,render_template,session
from flask_session import Session
import openai
import re
import speech_recognition as sr
from playsound import playsound
import psycopg2 

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
# Set your OpenAI API key
with open('api.txt', 'r') as file:
    apiKey = file.read().strip()
openai.api_key = apiKey
r=sr.Recognizer()

global user_id
user_id=[]
global currentUserId
# history=[]
global history
history=[]
global prompts
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

@app.route('/LogIn',methods=['POST'])
def LogIn():
    global currentUserId
    username=[]
    password=[]
    cur.execute('''select id,name,password from users''')
    data=cur.fetchall()
    i=0
    while i<len(data):
        user_id.append(data[i][0])
        username.append(data[i][1])
        password.append(data[i][2])
        i+=1
    i=0
    while i<len(data):
        if request.form['username']==username[i] and request.form['password']==password[i]:
            currentUserId=user_id[i]#here i have assigned value to a global variable which i want to use across the routes
            session['currentUserId'] = currentUserId#so i add the variable to a session for future use 
            cur.execute('''select code from history where user_id=%s''',(currentUserId,))#"," is necessary for system to interpret currnetUserId as a tuple even though it contains only one element as 'currentUserId' is of type int, and we're trying to index it, which is not allowed.
            global history
            history=cur.fetchall()
            cur.execute('''select prompt from history where user_id=%s''',(currentUserId,))
            global prompts
            prompts=cur.fetchall()
            return render_template('index.html', title='AI Code Generator', message="{(code)}", history=history,prompts=prompts)
        i+=1
    return render_template('LogIn.html',flag="true",message="Incorrect Username or Password!")

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
    global currentUserId#as it is a global variable so it is necessary to declare it at module level as well as in every function it is used in
    currentUserId=session.get('currentUserId',None)#here i'm kinda fetching the variable's value from the session in which i registered earlier in the /LogIn route
    user_question=voice_to_text()
    # print(voice_to_text())
    try:
        if language=="python":
            user_question=user_question+" in python language"
        elif language=="c":
            user_question=user_question+" in c language"
        elif language=="java":
            user_question=user_question+" in java language"
        else:
            user_question=user_question+" in python language"
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
        if language=="python":
            user_question=user_question.replace(" in python language","")
        elif language=="c":
            user_question=user_question.replace(" in c language","")
        elif language=="java":
            user_question=user_question.replace(" in java language","")
        else:
            user_question=user_question.replace(" in python language","")
        print(user_question)
        cur.execute('''insert into history (code,prompt,user_id) values(%s,%s,%s)''',(finalCode,user_question,currentUserId))
        conn.commit()
        # print(response)
        # print(history)
        cur.execute('''select code from history where user_id=%s''',(currentUserId,))#"," is necessary for system to interpret currnetUserId as a tuple even though it contains only one element as 'currentUserId' is of type int, and we're trying to index it, which is not allowed.
        global history
        history=cur.fetchall()
        cur.execute('''select prompt from history where user_id=%s''',(currentUserId,))
        global prompts
        prompts=cur.fetchall()
        return render_template('index.html', title='AI Code Generator', message=finalCode, history=history,prompts=prompts)
        # return jsonify({'response': "'"+response+"'"})
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/ask', methods=['POST'])
def ask_openai():
    global user_question
    global currentUserId
    currentUserId=session.get('currentUserId',None)
    try:
        user_question = request.form['question']
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
        if language=="python":
            user_question=user_question.replace(" in python language","")
        elif language=="c":
            user_question=user_question.replace(" in c language","")
        elif language=="java":
            user_question=user_question.replace(" in java language","")
        else:
            user_question=user_question.replace(" in python language","")
        print(user_question)
        cur.execute('''insert into history (code,prompt,user_id) values(%s,%s,%s)''',(finalCode,user_question,currentUserId))
        conn.commit()
        # print(finalCode)
        # print(response)
        # print(history)
        cur.execute('''select code from history where user_id=%s''',(currentUserId,))#"," is necessary for system to interpret currnetUserId as a tuple even though it contains only one element as 'currentUserId' is of type int, and we're trying to index it, which is not allowed.
        global history
        history=cur.fetchall()
        cur.execute('''select prompt from history where user_id=%s''',(currentUserId,))
        global prompts
        prompts=cur.fetchall()
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
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
