import tiktoken
from typing import List
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
    def length_messages(cls, messages: List, model="gpt-3.5-turbo"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model.startswith("gpt-3.5-turbo"):  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not presently implemented for model {model}. 
                See https://github.com/openai/openai-python/blob/main/chatml.md for information on 
                how messages are converted to tokens.""")

    @classmethod
    def get(cls, string: str, model):
        return tiktoken.encoding_for_model(model).encode(string)

    @classmethod
    def length(cls, string: str, model):
        return len(Token.get(string, model))

    @classmethod
    def max_tokens(cls, model):
        return cls.MODEL_MAX_TOKENS.get(model, cls.MODEL_MAX_TOKENS['else'])
