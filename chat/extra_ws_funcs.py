from chat.serializers import MessageSerializer
from chat.models import Message

from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict


def queryset_to_list(qs,fields=None, exclude=None):
    my_list=[]
    for x in qs:
        my_list.append(model_to_dict(x,fields=fields,exclude=exclude))
    return my_list


@sync_to_async
def get_all_msgs(chat):
    msgs = Message.objects.filter(chat=chat)
    serializer = MessageSerializer(data=queryset_to_list(msgs), many=True)
    serializer.is_valid(raise_exception=True)
    return serializer.data  


@sync_to_async
def create_msg(content):
    serializer = MessageSerializer(data=content)
    print(serializer.is_valid())
    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        return serializer.errors
