import os
from openai import OpenAI
from Inteligencia.Contantes import TEMPERATURE, MAX_TOKENS, CLEAN_TEXT

class InferenceService:
    def __init__(self):
        self.__model = 'gpt-3.5-turbo-instruct'  # Definir el modelo de OpenAI a utilizar
        api_key = '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'  # Reemplaza 'tu_clave_api_aqui' con tu clave de API
        self.__openai_client = OpenAI(api_key=api_key)

    def __inference(self, prompt):
        return CLEAN_TEXT(self.__openai_client.completions.create(
            model=self.__model,
            prompt=prompt,
            max_tokens=MAX_TOKENS*16,
            temperature=TEMPERATURE
        ).choices[0].text)

    def invoke(self, emotions_with_percentages: str):
        prompt = self.__prepare_prompt(emotions_with_percentages)
        response = self.__inference(prompt)
        return response

    def __prepare_prompt(self, emotions_with_percentages: str):
        prompt_template = 'Las emociones identificadas son:\n{emociones}.\nBasado en estas emociones, te recomendaría.'
        return prompt_template.format(emociones=emotions_with_percentages)
