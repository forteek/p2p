from enum import Enum
import json


class MessageEvent(Enum):
    HAS = 'has'
    NEED = 'need'


class Message:
    def __init__(self, event: MessageEvent, content: str):
        self.event = event
        self.content = content


class MessageSerializer:
    @staticmethod
    def serialize(message: Message) -> bytes:
        return json.dumps({'event': message.event.value, 'content': message.content}).encode('utf-8')

    @staticmethod
    def deserialize(message: bytes) -> Message:
        data = json.loads(message.decode('utf-8'))

        return Message(
            MessageEvent[data['event']],
            data['content']
        )
