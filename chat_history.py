from datetime import datetime
import os
import sys

import context_manager as cm
from openai import OpenAI

api_key = os.environ.get('API_KEY', 'no_key')
base_url = os.environ.get('BASE_URL', 'http://localhost:8080/v1')
client = OpenAI(
  api_key=api_key,
  base_url=base_url,
)
print(f"Chat Client: {base_url} [key:{len(api_key)}]")

def get_kw(kw, opt, default=None):
  return kw[opt] if opt in kw else default

def chat_stream(messages, **kwargs):
  global client
  stream = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=messages,
    temperature=get_kw(kwargs, 'temperature', 0.7),
    stream=True
  )

  for chunk in stream:
    if chunk.choices[0].delta.content is not None:
      yield chunk.choices[0].delta.content

ctx = cm.ContextManager(max_tokens=1024, ranker=cm.SimpleRanker().rank)
ctx.add_dynamic('dt', 'current date and time', fn=lambda: "Current Date and Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
ctx.add_dynamic('content-ex', 'ContextManager chat history example', content="This is an example of using ContextManager for a simple chat with history.")

system_message = "You're an intelligent, sarcastic spy named Lana Kane, helping your new partner."
last_messages = []

while True:
  line = input('> ')
  if line is None or line == '' or line == 'quit' or line == 'exit':
    break

  if line == '/last':
    print(f"Last messages:")
    for msg in last_messages:
      print(f" - {msg}")
    continue
  if line == '/clear':
    ctx.messages = []
    continue
  if line.startswith("/system"):
    new_msg = line[8:]
    if new_msg == '':
      print(f"Current System: {system_message}")
    else:
      system_message = line[8:]
    continue
  ctx.start_new_message()
  sys_msg = ctx.request(system_message, role=cm.Roles.system, include_text=False)
  ctx.request(line)
  msgs = ctx.generate_messages()
  last_messages = msgs
  res = ''
  for chunk in chat_stream(msgs, temperature=0.4):
    res += chunk
    sys.stdout.write(chunk)
    sys.stdout.flush()
  ctx.add_message(line)
  ctx.add_message(res, cm.Roles.assistant)
  print()
