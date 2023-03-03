import tiktoken
from config import Config


class Token:
    MODEL_MAX_TOKENS = {
        'gpt-3.5-turbo': 4096,
        'gpt-3.5-turbo-0301': 4096,
        'text-davinci-003': 4000,
        'text-davinci-002': 4000,
        'code-davinci-002': 4000,
        'else': 2048,
    }

    @classmethod
    def get(cls, string: str, model):
        return tiktoken.encoding_for_model(model).encode(string)

    @classmethod
    def length(cls, string: str, model):
        return len(Token.get(string, model))

    @classmethod
    def max_tokens(cls, model):
        return cls.MODEL_MAX_TOKENS.get(model, cls.MODEL_MAX_TOKENS['else'])
