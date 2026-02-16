from rest_framework import serializers

class TelegramChatSerializer(serializers.Serializer):
    chat_id = serializers.CharField(max_length=50, help_text="ID чата Telegram")