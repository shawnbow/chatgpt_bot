import tiktoken
from config import Config


class Token:
    MODEL_MAX_TOKENS = {
        'gpt-3.5-turbo': 4096,
        'gpt-3.5-turbo-0301': 4096,
        'text-davinci-003': 4000,
        'text-davinci-002': 4000,
        'code-davinci-002': 4000,
    }

    @classmethod
    def get(cls, string: str, model=Config.openai('chat_model')):
        if model not in tiktoken.model.MODEL_TO_ENCODING.keys():
            model = 'text-davinci-003'
        return tiktoken.encoding_for_model(model).encode(string)

    @classmethod
    def length(cls, string: str, model=Config.openai('chat_model')):
        return len(Token.get(string, model=model))

    @classmethod
    def max_tokens(cls, model=Config.openai('chat_model')):
        return cls.MODEL_MAX_TOKENS.get(model, Config.openai('max_tokens'))
