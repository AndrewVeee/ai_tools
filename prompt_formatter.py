
PROMPT_TEMPLATES = {
  "chatlm": {
    "name": "chatlm",
    "role_map": { "user": "user", "system": "system", "assistant": "assistant" },
    "tmpl": ["<|im_start|>", "::role", "::nl", "::prompt", "<|im_end|>", "::nl"],
  },
  "openchat": {
    "name": "OpenChat",
    "role_map": { "user": "User", "system": "User", "assistant": "assistant" },
    "tmpl": ["GPT4 ", "::role", ": ", "::prompt", "<|end_of_turn|>"],
    "stops": ["<|end_of_turn|>"],
  },
}

class PromptFormatter:
  def __init__(self, format='chatlm'):
    self.format = format
    self.tmpl = PROMPT_TEMPLATES[format]
    self.messages = []
    self.role_map = {
      'user': 'user',
      'system': 'system',
      'assistant': 'assistant',
    }
  
  def add_message(self, content, role='user'):
    self.messages.append({'content': content, 'role': role})

  def generate_message(self, content, role=None):
    message_str = ""
    real_role = self.tmpl['role_map'][role] if role in self.tmpl['role_map'] else self.tmpl['role_map']['user']
    prompt_subs = {"role": real_role, "nl": "\n", "prompt": content}
    for prompt_val in self.tmpl['tmpl']:
      if prompt_val.startswith("::"):
        message_str += prompt_subs[prompt_val.lstrip('::')]
      else:
        message_str += prompt_val
    return message_str
  
  def generate(self):
    prompt_str = '';

    for message in self.messages:
      prompt_str += self.generate_message(message['content'], message['role'])
    
    return prompt_str
