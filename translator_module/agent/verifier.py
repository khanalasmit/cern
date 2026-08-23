import os
from openai import OpenAI

class ContextVerifier:
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def verify_context(self, query: str, context: str) -> bool:
        """
        Uses a lightweight LLM call to verify if the retrieved context 
        contains sufficient schema information to answer the query.
        Returns True if sufficient, False otherwise.
        """
        prompt = f"""
        You are a Self-RAG verification model for an OKS (Object Knowledge System) schema retrieval pipeline.
        Your task is to determine if the provided OKS schema context is sufficient to translate the given user query into an OKS query.
        
        If the context contains the necessary class definitions, attributes, or relationships mentioned in the query, output "YES".
        If the context is entirely irrelevant or missing key components needed to answer the query, output "NO".
        
        User Query:
        {query}
        
        Retrieved Schema Context:
        {context}
        
        Output only "YES" or "NO".
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )
            result = response.choices[0].message.content.strip().upper()
            return "YES" in result
        except Exception as e:
            # Fallback to True if verification fails due to API error
            print(f"Warning: Context verification failed with error: {e}. Defaulting to True.")
            return True
