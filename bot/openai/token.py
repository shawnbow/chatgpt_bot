import tiktoken
from config import Config


class Token:
    @classmethod
    def get(cls, string: str, model=Config.openai('text_model')):
        if model not in tiktoken.model.MODEL_TO_ENCODING.keys():
            model = 'text-davinci-003'
        return tiktoken.encoding_for_model(model).encode(string)
