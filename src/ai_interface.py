from typing import Dict, Optional, Union, List, Any
from langchain.schema import HumanMessage
from langchain.schema.output import LLMResult
import os
import logging
# Import only the necessary Ollama model class
from langchain_ollama import OllamaLLM

# Set up logger for this module
logger = logging.getLogger(__name__)

class AIInterface:
    """
    A unified interface for interacting with multiple AI models.
    Currently configured to work with Ollama models only.
    """
    
    def __init__(self, 
                 model_provider: str, 
                 model_name: str,
                 **kwargs: Optional[str] 
                 ) -> None:
        
        logger.info(f"Initializing AIInterface with provider: {model_provider}, model: {model_name}")
        
        if model_provider.lower() == 'ollama':
            try:
                # Initialize Ollama with only the basic parameters
                ollama_url = None
                if os.getenv('CONTAINER', 'false').lower() == 'true':
                    ollama_url = "http://host.docker.internal:11434"
                    logger.debug("Running in container mode - using host.docker.internal")
                else:
                    ollama_url = "http://localhost:11434"
                    logger.debug("Running in local mode - using localhost")
                
                logger.debug(f"Connecting to Ollama at: {ollama_url}")
                
                self.model = OllamaLLM(
                    model=model_name, 
                    base_url=ollama_url,
                    **kwargs
                )
                
                logger.info(f"Successfully initialized Ollama model: {model_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize Ollama model: {e}")
                raise
        else:
            logger.error(f"Unsupported model provider: {model_provider}")
            raise ValueError(f"Currently only 'ollama' provider is supported")
    
    def get_completion(self, prompt: str) -> str:
        """Get completion from the AI model for a simple prompt"""
        logger.debug(f"Getting completion for prompt: {len(prompt)} characters")
        
        try:
            # For Ollama, just pass the prompt directly
            response = self.model.invoke(prompt)
            logger.debug(f"Received response: {len(response)} characters")
            logger.debug(f"Response preview: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error getting completion from AI model: {e}")
            raise
    
    def get_completion(self, messages: List[Dict[str, str]] = None, prompt: str = None) -> str:
        """Get completion from the AI model - supports both messages and prompt formats"""
        
        if messages:
            logger.debug(f"Getting completion for {len(messages)} messages")
            # Convert messages to a single prompt for Ollama
            prompt_text = ""
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                prompt_text += f"{role}: {content}\n"
            
            logger.debug(f"Converted messages to prompt: {len(prompt_text)} characters")
            
        elif prompt:
            prompt_text = prompt
            logger.debug(f"Using direct prompt: {len(prompt_text)} characters")
        else:
            logger.error("Neither messages nor prompt provided")
            raise ValueError("Either messages or prompt must be provided")
        
        try:
            response = self.model.invoke(prompt_text)
            logger.debug(f"Received response: {len(response)} characters")
            logger.debug(f"Response preview: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error getting completion from AI model: {e}")
            logger.debug(f"Failed prompt: {prompt_text[:200]}...")
            raise

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