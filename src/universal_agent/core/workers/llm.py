import json
import logging
import urllib.error
import urllib.request

from ..config import config

logger = logging.getLogger(__name__)

class LLMWorker:
    def __init__(self, endpoint="http://127.0.0.1:11434/v1/chat/completions", model_name="local-llama"):
        self.endpoint = endpoint
        self.model_name = model_name
        self.enabled = config.enable_llm

    def check_health(self):
        # Safely check endpoint without generation (e.g. check models or just GET to base)
        try:
            # We can check the models endpoint for OpenAI compatible or Ollama
            base_url = self.endpoint.rsplit('/v1/chat/completions', 1)[0]
            if base_url == self.endpoint:
                base_url = self.endpoint.rsplit('/api/generate', 1)[0]
            req = urllib.request.Request(f"{base_url}/v1/models", method="GET")
            with urllib.request.urlopen(req, timeout=5) as res:
                if res.status == 200:
                    return {"status": "ok", "message": "LLM endpoint reachable"}
        except Exception as e:
            return {"status": "error", "error": f"LLM endpoint unreachable: {e}"}
        return {"status": "error", "error": "Unknown issue with LLM endpoint"}

    def generate(self, prompt: str, timeout: int = 60):
        if not self.enabled:
            return {"status": "error", "error": "LLM worker is disabled by configuration"}
            
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as res:
                response = json.loads(res.read().decode('utf-8'))
                # Extract for OpenAI standard
                if 'choices' in response and len(response['choices']) > 0:
                    content = response['choices'][0].get('message', {}).get('content', '')
                    return {"status": "ok", "completion": content}
                return {"status": "error", "error": "Invalid response format"}
        except urllib.error.URLError as e:
            return {"status": "error", "error": str(e)}
        except Exception as e:
            return {"status": "error", "error": str(e)}
