# app.py
# -*- coding: utf-8 -*-
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

def extract_code_block(content):
    match = re.search(r"```python(.*?)```", content, re.DOTALL)
    return match.group(1).strip() if match else content.strip()

def openai_req(system_content, user_content):
    global history

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content":  user_content}
        ]
    if history != []:
        messages = [
        {"role": "system", "content": system_content}
        ]
        messages = messages + history
        messages = messages + [{"role": "user", "content":  user_content}]
    else:
        messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content":  user_content}
        ]
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )

    content = completion.choices[0].message.content
    history = [
        {"role": "user", "content":  user_content},
        { "role": "assistant", "content": content }
        ]
    return extract_code_block(content)

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
        if gpt_role == '' or request.form['role']:
            gpt_role = request.form['role']
        gpt_q = request.form['question']
        gpt_q_list.append(gpt_q)
        gpt_r_list.append(openai_req(gpt_role, gpt_q))

    return render_template('index.html', gpt_q_list=gpt_q_list, gpt_r_list=gpt_r_list, current_role=gpt_role)

@app.route('/clear')
def clear_lists():
    global gpt_r_list, gpt_q_list
    gpt_r_list.clear()
    gpt_q_list.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)