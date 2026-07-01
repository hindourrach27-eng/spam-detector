"""
test_ollama.py — Test simple de l'appel a Ollama depuis Python
"""

import ollama

# response = ollama.chat(
#     model='qwen2.5:7b',
#     messages=[
#         {'role': 'user', 'content': 'Bonjour, peux-tu me confirmer que tu fonctionnes en repondant en une phrase ?'}
#     ]
# )
#
# print(response['message']['content'])
print('********************************')

import requests
import json

SYSTEM_PROMPT = """You are an expert email deliverability engineer specializing in inbox warming techniques.

Your job is to generate TWO things:
1. HIDDEN WARMUP TEXT — natural human-looking text that is invisible to the reader (white text on white background, font-size 0, hidden via CSS). This text is read by spam filters and ISPs to build sender reputation.
2. A JSON structure the developer will use to inject this hidden text into their existing offer email.

HIDDEN TEXT RULES:
- Must look like a genuine human email conversation or industry update
- 150-300 words of natural flowing text
- Niche-specific vocabulary
- NO spam words, NO promotional language
- Written like a personal note or blog excerpt
- Include questions, observations, casual opinions
- Must feel 100% human to NLP spam filters

OUTPUT — valid JSON only, no markdown:
{
  "niche": "the niche",
  "hidden_text": "150-300 words of natural human text, plain text only no HTML",
  "html_snippet": "<div style='...hidden CSS...'>the hidden text here</div>",
  "subject": "natural inbox-friendly subject line",
  "preview_text": "preheader text under 50 chars"
}

The html_snippet must hide text using ALL of these techniques combined:
- color: #ffffff (white text)
- font-size: 0px
- line-height: 0px  
- max-height: 0px
- overflow: hidden
- opacity: 0
- display: block
- mso-hide: all (for Outlook)
This makes it invisible to humans but readable by spam filter crawlers.
"""

def generate_hidden_warmup(domain_niche: str, your_offer: str = "") -> dict:
    offer_hint = f"\nThe visible offer in the email is about: {your_offer}" if your_offer else ""

    prompt = f"""Generate hidden warmup text for this niche: {domain_niche}
{offer_hint}

The hidden text must be completely natural and human-sounding for this niche.
It will be invisible in the email but read by spam filters to build inbox reputation.
Make it feel like a genuine personal note someone in the {domain_niche} space would write."""

    response = requests.post("http://localhost:11434/api/chat", json={
        "model": "qwen2.5:7b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.85,
            "num_predict": 1000,
            "num_ctx": 2048,
        }
    })

    raw = response.json()["message"]["content"]

    # Clean JSON
    raw = raw.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def inject_into_offer(offer_html: str, hidden_snippet: str) -> str:
    """Inject hidden warmup text right after <body> tag in your offer HTML."""
    if "<body" in offer_html:
        # Inject right after opening body tag
        insert_pos = offer_html.find("<body")
        insert_pos = offer_html.find(">", insert_pos) + 1
        return offer_html[:insert_pos] + "\n" + hidden_snippet + "\n" + offer_html[insert_pos:]
    else:
        # Just prepend if no body tag
        return hidden_snippet + "\n" + offer_html


def save_result(result: dict, offer_html: str, niche: str):
    filename = niche.replace(" ", "_").lower()

    # Save the final injected email
    final_html = inject_into_offer(offer_html, result["html_snippet"])
    with open(f"{filename}_final_email.html", "w", encoding="utf-8") as f:
        f.write(final_html)

    # Save a debug preview showing both layers
    with open(f"{filename}_debug.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Debug Preview</title></head>
<body style="font-family:Arial,sans-serif; padding:30px; background:#f0f0f0;">

  <div style="max-width:700px; margin:auto;">

    <div style="background:#fff3cd; padding:15px; border-radius:8px; margin-bottom:20px;">
      <h3 style="margin:0 0 10px">📧 Email Metadata</h3>
      <p><strong>Subject:</strong> {result['subject']}</p>
      <p><strong>Preview text:</strong> {result['preview_text']}</p>
      <p><strong>Niche:</strong> {result['niche']}</p>
    </div>

    <div style="background:#d4edda; padding:15px; border-radius:8px; margin-bottom:20px;">
      <h3 style="margin:0 0 10px">👻 Hidden Warmup Text (visible here for debug only)</h3>
      <p style="color:#333; font-size:14px; line-height:1.6;">{result['hidden_text']}</p>
    </div>

    <div style="background:#fff; padding:15px; border-radius:8px; border:1px solid #ddd;">
      <h3 style="margin:0 0 10px">✉️ What the reader sees (your offer)</h3>
      {offer_html}
    </div>

  </div>

</body>
</html>""")

    print(f"✅ Final email saved : {filename}_final_email.html")
    print(f"✅ Debug preview     : {filename}_debug.html")


# ─── USAGE ────────────────────────────────────────────────
niche = input("Enter domain niche (e.g. fitness, real estate, crypto): ").strip()
offer = input("Describe your offer (e.g. discount on protein supplements): ").strip()

# Your existing offer HTML — paste it here or load from file
YOUR_OFFER_HTML = """
<div style="max-width:600px; margin:auto; font-family:Arial,sans-serif; padding:20px;">
  <h1 style="color:#e74c3c;">🔥 Special Offer Just For You!</h1>
  <p>Get 50% off our premium fitness program today only.</p>
  <a href="#" style="background:#e74c3c; color:#fff; padding:12px 24px; 
     text-decoration:none; border-radius:5px; display:inline-block;">
     Claim Your Discount
  </a>
</div>
"""
# ↑ Replace this with your actual offer HTML

print(f"\n⏳ Generating hidden warmup text for '{niche}'...")
result = generate_hidden_warmup(niche, offer)

print(f"\n✅ Subject      : {result['subject']}")
print(f"✅ Preview text : {result['preview_text']}")
print(f"✅ Hidden text  : {result['hidden_text'][:100]}...")

save_result(result, YOUR_OFFER_HTML, niche)