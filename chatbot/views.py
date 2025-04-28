import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import speech_recognition as sr

from .models import ChatMessage
from .utils import get_bot_response, handle_user_query_direct


@login_required
@require_GET
def load_history(request):
    try:
        messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
        dialog = [
            {
                'sender': msg.sender,
                'text': msg.message,
                'timestamp': timezone.localtime(msg.timestamp).strftime('%H:%M')
            } for msg in messages
        ]
        return JsonResponse({'dialog': dialog})
    except Exception as e:
        print(f"Ошибка загрузки истории чата для {request.user}: {e}")
        return JsonResponse({'dialog': [], 'error': 'Не удалось загрузить историю.'}, status=500)


@login_required
@require_POST
def get_response(request):
    try:
        data = json.loads(request.body)
        user_input = data.get('message')

        if not user_input or not isinstance(user_input, str):
            return HttpResponseBadRequest(json.dumps({"error": "Некорректный запрос."}), content_type='application/json')

        user_msg = ChatMessage.objects.create(
            user=request.user,
            sender='user',
            message=user_input
        )

        direct_response = handle_user_query_direct(user_input)

        if direct_response is not None:
            bot_response_text = direct_response
            print(f"Direct response for user '{request.user}': {bot_response_text}")
        else:
            print(f"Query not handled directly for user '{request.user}', calling AI...")
            history_queryset = ChatMessage.objects.filter(user=request.user)
            bot_response_text = get_bot_response(user_input, history_queryset)

        bot_msg = ChatMessage.objects.create(
            user=request.user,
            sender='bot',
            message=bot_response_text
        )

        return JsonResponse({
            "response": bot_response_text,
        })

    except json.JSONDecodeError:
        print(f"JSONDecodeError in get_response for user '{request.user}'")
        return HttpResponseBadRequest(json.dumps({"error": "Неверный формат JSON."}), content_type='application/json')
    except Exception as e:
        print(f"Неожиданная ошибка в get_response для пользователя '{request.user}': {e}")
        return HttpResponseServerError(json.dumps({"error": f"Внутренняя ошибка сервера: {e}"}), content_type='application/json')


@login_required
@require_POST
def clear_history(request):
    try:
        deleted_count, _ = ChatMessage.objects.filter(user=request.user).delete()
        print(f"Удалено {deleted_count} сообщений для пользователя {request.user.username}.")
        return JsonResponse({"status": "ok", "message": "История чата очищена."})
    except Exception as e:
        print(f"Ошибка очистки истории чата для {request.user}: {e}")
        return HttpResponseServerError(json.dumps({"error": "Не удалось очистить историю."}), content_type='application/json')

def voice_input(request):
     recognizer = sr.Recognizer()
     with sr.Microphone() as source:
         try:
             print("Слушаю...")
             audio = recognizer.listen(source, timeout=5)
             text = recognizer.recognize_google(audio, language="ru-RU")
             print(f"Распознанный текст: {text}")
             return JsonResponse({"success": True, "text": text})
         except sr.UnknownValueError:
             print("Не удалось распознать голос")
             return JsonResponse({"success": False, "error": "Не удалось распознать голос"})
         except sr.RequestError as e:
             print(f"Ошибка сервиса распознавания речи: {e}")
             return JsonResponse({"success": False, "error": f"Ошибка сервиса распознавания речи: {e}"})
         except Exception as e:
             print(f"Неожиданная ошибка в voice_input: {e}")
             return JsonResponse({"success": False, "error": f"Неожиданная ошибка распознавания: {e}"})