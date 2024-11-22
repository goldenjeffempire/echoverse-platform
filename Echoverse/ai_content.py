import openai
from django.conf import settings

# Ensure you've set your API key in your settings.py
openai.api_key = settings.OPENAI_API_KEY

def generate_blog_post(prompt):
    try:
        # Call OpenAI API to generate content based on a prompt
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=700,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating content: {e}")
        return None
