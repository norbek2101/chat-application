from channels.generic.websocket import AsyncJsonWebsocketConsumer 
from json.decoder import JSONDecodeError

import json

from channels.layers import get_channel_layer


channel_layer = get_channel_layer()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        user = self.scope.get('user', False)
        await self.accept()

        if user.is_anonymous:
            await self.send_json({"user": str(user), 'errors': user.get_errors})
            return await self.close()
            
            
        return await self.send(
            json.dumps(
                        {
                            "message": "User connected", 
                            "user": str(user.id)
                        }
                    )
                )