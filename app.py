import os
import re
import openai
from auth import User
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session

load_dotenv()
openai.api_key = os.environ.get('GPT_TOKEN')

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_TOKEN')

gpt_r_list = []
gpt_q_list = []
gpt_role = ''
history = []

def split_response_into_blocks(response):
    languages = ['python', 'java', 'sql', 'javascript', 'html', 'css']
    blocks = []
    pattern = r'```(\w+)\n(.*?)```'
    matches = list(re.finditer(pattern, response, re.DOTALL))

    last_index = 0
    for match in matches:
        lang = match.group(1)
        code = match.group(2)
        start, end = match.span()

        # Add any text before the code block
        if start > last_index:
            text_part = response[last_index:start]
            blocks.append({'type': 'text', 'value': text_part})

        blocks.append({'type': 'code', 'lang': lang, 'value': code})
        last_index = end

    # Add any text remaining after last code block
    if last_index < len(response):
        blocks.append({'type': 'text', 'value': response[last_index:]})

    return blocks

def openai_req(system_content, user_content):
    global history

    if history:
        messages = [{"role": "system", "content": system_content}] + history + [{"role": "user", "content": user_content}]
    else:
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )

    content = completion.choices[0].message.content
    history = [
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": content}
    ]
    return split_response_into_blocks(content)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User(username, password)
        if user.check_userid():
            session['username'] = username
            session.permanent = True
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('auth.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    global gpt_role

    if 'username' not in session:
        return redirect(url_for('auth'))

    if request.method == 'POST':
        role = request.form['role']
        question = request.form['question']

        if gpt_role == '' or role:
            gpt_role = role

        gpt_q_list.append(question)
        gpt_r_list.append(openai_req(gpt_role, question))

    return render_template('index.html', gpt_q_list=gpt_q_list, gpt_r_list=gpt_r_list, current_role=gpt_role)

@app.route('/clear')
def clear_lists():
    global gpt_r_list, gpt_q_list, history
    gpt_r_list.clear()
    gpt_q_list.clear()
    history.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
