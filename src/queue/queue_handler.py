# src/queue/queue_handler.py

import asyncio
from typing import Dict, Any, Callable
import json
import logging
from aio_pika import connect_robust, Message, ExchangeType
from src.config.settings import settings

logger = logging.getLogger(__name__)

class QueueHandler:
    """
    Handles asynchronous message processing using RabbitMQ.
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.handlers: Dict[str, Callable] = {}

    async def connect(self):
        """
        Establish connection to RabbitMQ.
        """
        try:
            self.connection = await connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                "taxi_trips",
                ExchangeType.TOPIC
            )
            
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    async def publish_message(self, routing_key: str, message: Dict[str, Any]):
        """
        Publish message to queue.
        """
        try:
            await self.exchange.publish(
                Message(
                    json.dumps(message).encode(),
                    content_type="application/json"
                ),
                routing_key=routing_key
            )
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise

    async def register_handler(self, routing_key: str, handler: Callable):
        """
        Register a message handler for a specific routing key.
        """
        queue = await self.channel.declare_queue(routing_key)
        await queue.bind(self.exchange, routing_key)
        self.handlers[routing_key] = handler
        
        async def process_message(message):
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    await handler(data)
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    
        await queue.consume(process_message)
        logger.info(f"Registered handler for {routing_key}")

    async def close(self):
        """
        Close queue connections.
        """
        if self.connection:
            await self.connection.close()