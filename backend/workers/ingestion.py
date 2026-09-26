import json
import logging
from confluent_kafka import Consumer, KafkaError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.schema import LLMCallEvent
from backend.core.db_models import Base, Trace
import chromadb
from datetime import datetime
import dateutil.parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "llm_traces"
PG_URI = "postgresql+psycopg2://llmops:llmops_pass@localhost:5432/control_tower"

# Initialize Postgres
engine = create_engine(PG_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Initialize ChromaDB
# For this worker, we connect to the ChromaDB running in docker
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
# Create or get collection
collection = chroma_client.get_or_create_collection(name="llm_responses")

# Initialize Kafka Consumer
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'ingestion_worker_group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([KAFKA_TOPIC])

def process_message(msg_value: str):
    data = json.loads(msg_value)
    event = LLMCallEvent(**data)
    
    # 1. Save to Postgres
    session = Session()
    try:
        trace_record = Trace(
            trace_id=event.trace_id,
            timestamp=event.timestamp,
            project_id=event.project_id,
            application_name=event.application_name,
            model_version=event.model_version,
            prompt=event.prompt,
            response=event.response,
            latency_ms=event.latency_ms,
            input_tokens=event.input_tokens,
            output_tokens=event.output_tokens,
            cost_usd=event.cost_usd,
            metadata_=event.metadata
        )
        session.add(trace_record)
        session.commit()
        logger.info(f"Saved trace {event.trace_id} to Postgres")
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving to DB: {e}")
    finally:
        session.close()

    # 2. Save to Chroma DB (we embed the prompt to find similar traces later)
    try:
        collection.add(
            documents=[event.prompt],
            metadatas=[{"trace_id": event.trace_id, "model": event.model_version}],
            ids=[event.trace_id]
        )
        logger.info(f"Added trace {event.trace_id} to ChromaDB")
    except Exception as e:
        logger.error(f"Error saving to Chroma: {e}")

def run():
    logger.info("Starting Ingestion Worker...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Kafka error: {msg.error()}")
                    break
            
            logger.info(f"Received message from Kafka partition {msg.partition()}")
            process_message(msg.value().decode('utf-8'))
    except KeyboardInterrupt:
        logger.info("Shutting down worker...")
    finally:
        consumer.close()

if __name__ == "__main__":
    run()
