import requests
import json
from django.conf import settings
from listings.models import Brand, Model, Car

LMSTUDIO_API_URL = getattr(settings, 'LMSTUDIO_API_URL', "http://localhost:1234/v1/chat/completions")
MODEL_NAME = getattr(settings, 'LMSTUDIO_MODEL_NAME', "gemma-3-12b-it")
SYSTEM_PROMPT = getattr(settings, 'CHATBOT_SYSTEM_PROMPT', "Сен пайдалы ЖИ ассистент. Бір тілде жауап бер.")
HISTORY_LENGTH = getattr(settings, 'CHATBOT_HISTORY_LENGTH', 5)

def get_bot_response_from_lmstudio(user_input, message_history_queryset):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    recent_history = message_history_queryset.order_by('-timestamp')[:HISTORY_LENGTH * 2]
    for msg in reversed(recent_history):
        role = "user" if msg.sender == 'user' else "assistant"
        messages.append({"role": role, "content": msg.message})

    cars = Car.objects.all()
    if cars.exists():
        car_list = [
            f"{car.brand.name} {car.model.name} ({car.year}) ({car.mileage} км) - ${car.price}"
            for car in cars
        ]
        available_cars_info = "Доступные автомобили:\n" + "\n".join(car_list)
    else:
        available_cars_info = "На сайте пока нет доступных автомобилей."

    messages.append({"role": "system", "content": f"Информация о доступных машинах: {available_cars_info}"})

    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        response = requests.post(LMSTUDIO_API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        response_data = response.json()

        choices = response_data.get("choices", [])
        if choices and isinstance(choices, list) and len(choices) > 0:
            message_data = choices[0].get("message", {})
            assistant_message = message_data.get("content", "")
            if assistant_message and isinstance(assistant_message, str):
                return assistant_message.strip()
            else:
                print("LM Studio вернул пустое или некорректное сообщение:", response_data)
                return "Извините, от нейросети пришел пустой или некорректный ответ."
        else:
            print("LM Studio жауап форматы қате немесе жауап жоқ:", response_data)
            return "Извините, формат ответа нейросети не распознан."

    except requests.exceptions.Timeout:
        print(f"Таймаут при запросе к LM Studio ({LMSTUDIO_API_URL}).")
        return "Извините, нейросеть долго отвечает. Попробуйте позже."
    except requests.exceptions.ConnectionError:
        print(f"Ошибка соединения с LM Studio ({LMSTUDIO_API_URL}).")
        return "Извините, не удается подключиться к локальной нейросети. Убедитесь, что LM Studio запущен."
    except requests.exceptions.RequestException as e:
        status_code = e.response.status_code if e.response is not None else "N/A"
        print(f"Ошибка запроса к LM Studio ({status_code}): {e}")
        error_detail = ""
        if e.response is not None:
            try:
                error_detail = e.response.json()
            except json.JSONDecodeError:
                error_detail = e.response.text
        return f"Извините, произошла ошибка при обращении к нейросети: {e}. {error_detail}"
    except Exception as e:
        print(f"Неожиданная ошибка в get_bot_response_from_lmstudio: {e}")
        # В продакшене лучше логировать детали ошибки, а не показывать пользователю
        return f"Извините, произошла внутренняя ошибка: {e}"

def handle_user_query(user_input):
    user_input = user_input.lower()

    if "бренды" in user_input or "марки" in user_input:
        brands = Brand.objects.all()
        if brands.exists():
            brand_names = ", ".join([brand.name for brand in brands])
            return f"На сайте представлены следующие бренды: {brand_names}."
        else:
            return "На сайте пока нет доступных брендов."

    if "модели" in user_input:
        for brand in Brand.objects.all():
            if brand.name.lower() in user_input:
                models = Model.objects.filter(brand=brand)
                if models.exists():
                    model_names = ", ".join([model.name for model in models])
                    return f"Для бренда {brand.name} доступны следующие модели: {model_names}."
                else:
                    return f"Для бренда {brand.name} пока нет доступных моделей."

    if "автомобили" in user_input or "машины" in user_input:
        cars = Car.objects.all()
        if cars.exists():
            car_list = [
                f"{car.brand.name} {car.model.name} ({car.year}) - ${car.price}"
                for car in cars
            ]
            return "Доступные автомобили:\n" + "\n".join(car_list)
        else:
            return "На сайте пока нет доступных автомобилей."

    return "Извините, я не понял ваш запрос. Попробуйте уточнить."