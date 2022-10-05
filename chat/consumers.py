import json
from json.decoder import JSONDecodeError

from channels.generic.websocket import AsyncJsonWebsocketConsumer 
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

from chat.extra_ws_funcs import get_all_msgs, create_msg
from chat.models import Message

from django.forms.models import model_to_dict

channel_layer = get_channel_layer()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        user = self.scope.get('user', False)
        await self.accept()

        if user.is_anonymous:
            await self.send_json({"user": str(user), 'errors': user.get_errors})
            return await self.close()
            
        self.room_group_name = str(user.id)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        return await self.send(
            json.dumps(
                        {
                            "message": "User connected", 
                            "user": str(user.id)
                        }
                    )
                )


    async def disconnect(self, code):
        user = self.scope.get('user', False)
        try:
            if not user.is_anonymous:
                await self.channel_layer.group_discard(
                            self.room_group_name,
                            self.channel_name
                        )
        except:
            pass
        finally:
            return await super().disconnect(code)


    async def receive(self, text_data):

        try:
            content = json.loads(text_data)
            if not isinstance(content, dict):
                return await self.send(
                                json.dumps(
                                    {
                                        'error': 'expected type json, got str instead'
                                    }
                                )
                            )
        except JSONDecodeError as e:
            return await self.send(json.dumps({'error': str(e)}))
        
        user = self.scope.get('user', False)
        action = content.pop('action', False)
       
        
        if action == 'get-messages':
            chat = content.pop('chat_id', False)

            if not chat:
                return await self.send_data({'data':{'error': "'chat_id' this field is required"}})
            else:
                result = await get_all_msgs(chat)
                return  await self.send_data({'data':result})


        elif action == 'send-message':
            content['sender'] = user.id
            result = await create_msg(content)
            print("result", result)
            
            return await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_data',
                    "data": result
                }
            )


        elif action == 'get-message':
            id = content.pop('id', False)
            if not id:
                return self.send_data({"data":"'id' this field is required"})
            else:
                result = await self.get_message(id)
                return await self.send_data({"data":result})


        elif action == "update-message":
            id = content.pop('id', False)
            text = content.pop("text", False)
            if not text:
                return await self.send_data({"data": {"text":"this field is required"}})
            else:
                result = await self.update_message(id, text)
                return await self.send_data({"data":result})


        elif action == 'delete-message':
            id = content.pop('id', False)
            if not id:
                return self.send_data({"data":"'id' this field is required"})
            else:
                result = await self.delete_message(id)
                return await self.send_data({"data":result})


    async def send_data(self, event):
        data = event['data']
        await self.send_json(data)

    
    @database_sync_to_async
    def get_message(self, id):
        try:
            msg = Message.objects.get(id=id)
            result= model_to_dict(msg)
            return result
        except Message.DoesNotExist:
            result = {"error":f"message pk not found"}
            return result


    @database_sync_to_async
    def update_message(self, id, text):
        try:    
            msg = Message.objects.get(id=id)
            msg.text = text
            msg.save()
            result= model_to_dict(msg)
            return result
        except Message.DoesNotExist:
            result = {"error":f"message pk not found"}
            return result


    @database_sync_to_async
    def delete_message(self, id):
        try:
            msg = Message.objects.get(id=id)
            msg.delete()
            result = {"deleted":f"message pk == {id}"}
            return result
        except Message.DoesNotExist:
            result = {"error":f"message pk not found"}
            return result
