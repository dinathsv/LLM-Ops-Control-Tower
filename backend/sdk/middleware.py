import time
import json
import logging
from typing import Any, Dict, Optional
import google.generativeai as genai
from confluent_kafka import Producer
from core.schema import LLMCallEvent
from datetime import datetime

logger = logging.getLogger(__name__)

class ControlTowerMiddleware:
    def __init__(self, kafka_bootstrap_servers: str, project_id: str, app_name: str):
        self.project_id = project_id
        self.app_name = app_name
        self.producer = Producer({
            'bootstrap.servers': kafka_bootstrap_servers,
            'client.id': f'{app_name}-producer'
        })
        self.topic = 'llm_traces'

    def _delivery_report(self, err, msg):
        """Called once for each message produced to indicate delivery result."""
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def generate_content(self, model_name: str, prompt: str, **kwargs) -> Any:
        """
        Wraps the Gemini generate_content call.
        Intersects the request, measures latency, extracts tokens, and fires an event to Kafka.
        """
        model = genai.GenerativeModel(model_name)
        
        start_time = time.time()
        
        # Execute the actual LLM Call
        try:
            response = model.generate_content(prompt, **kwargs)
            error = None
        except Exception as e:
            error = str(e)
            raise e
        finally:
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract usage metadata if available (Gemini API provides usage_metadata)
            input_tokens = 0
            output_tokens = 0
            if response and hasattr(response, 'usage_metadata'):
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                
            # Estimate cost (Dummy estimation for demonstration, replace with actual pricing logic)
            # Gemini 1.5 Pro estimation: $3.5 / 1M input, $10.5 / 1M output
            cost_usd = (input_tokens / 1_000_000 * 3.5) + (output_tokens / 1_000_000 * 10.5)
            
            event = LLMCallEvent(
                project_id=self.project_id,
                application_name=self.app_name,
                model_version=model_name,
                prompt=prompt,
                response=response.text if response else error,
                latency_ms=latency_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd,
                metadata={"status": "success" if not error else "error"}
            )
            
            # Produce to Kafka asynchronously
            self.producer.produce(
                self.topic,
                key=event.trace_id,
                value=event.model_dump_json(),
                callback=self._delivery_report
            )
            # Trigger any available delivery report callbacks from previous produce() calls
            self.producer.poll(0)
            
        return response

    def flush(self):
        """Wait for any outstanding messages to be delivered and delivery report callbacks to be triggered."""
        self.producer.flush()
