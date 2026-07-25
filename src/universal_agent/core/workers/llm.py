import logging

logger = logging.getLogger(__name__)

class LLMWorker:
    def __init__(self, model_name="local-llama"):
        self.model_name = model_name

    def generate(self, prompt: str):
        logger.info(f"LLMWorker [{self.model_name}] called with prompt: {prompt[:20]}...")
        return {"status": "ok", "completion": "mock completion"}
