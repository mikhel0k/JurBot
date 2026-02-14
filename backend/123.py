from openai import OpenAI
from app.core.config import settings

client = OpenAI(
    api_key=settings.API_TOKEN
)

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "system", "content": "Ты профессиональный разработчик, который помогает пользователям пользоваться API OpenAI. Ты должен быть очень подробным и понятным."}, {"role": "user", "content": "Расскажи мне подробно как пользоваться API OpenAI"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")