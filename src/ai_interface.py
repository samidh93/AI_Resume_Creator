from typing import Dict, Optional, Union, List, Any
from langchain.schema import HumanMessage
from langchain.schema.output import LLMResult

# Import only the necessary Ollama model class
from langchain_ollama import OllamaLLM


class AIInterface:
    """
    A unified interface for interacting with multiple AI models.
    Currently configured to work with Ollama models only.
    """
    
    def __init__(self   ,     
                  model_provider: str, 
                  model_name: str,
                  **kwargs: Optional[str] 
                  ) -> None:

        if model_provider.lower() == 'ollama':
            # Initialize Ollama with only the basic parameters
            self.model = OllamaLLM(
                model=model_name, 
                **kwargs
            )
        else:
            # Other providers are commented out for now
            raise ValueError(f"Currently only 'ollama' provider is supported")
            
    
    def get_completion(self,
                       prompt: str) -> str:
        
        # For Ollama, just pass the prompt directly
        return self.model.invoke(prompt)
    
 

# Main execution section
if __name__ == "__main__":
    
    # Create the AI interface
    ai = AIInterface(
            model_provider="ollama",
            model_name="qwen2.5:3b",
            temperature=0.5,
            #max_tokens=100,
            format="json"
        )


    prompt = "What is the greater number between 2 and 3?"
        
    try:
            response = ai.get_completion(
                prompt=prompt
            )
            print(f"\nResponse :\n{response}")
    except Exception as e:
        print(f"Error: {e}")