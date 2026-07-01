from clean_text import build_model_input, build_ai_prompt
from database import get_email_full_for_ai

email = get_email_full_for_ai(595)
model_input = build_model_input(email)
prompt = build_ai_prompt(model_input, label_gmail=email.get('label'))
print(len(prompt))