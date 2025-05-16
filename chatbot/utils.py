import requests
import json
from django.conf import settings
from django.urls import reverse
from listings.models import Brand, Model, Car

INTELLIGENCE_API_URL = getattr(settings, 'INTELLIGENCE_API_URL', "https://api.intelligence.io.solutions/api/v1/chat/completions")
MODEL_NAME = getattr(settings, 'INTELLIGENCE_MODEL_NAME', "CohereForAI/c4ai-command-r-plus-08-2024")
IOINTELLIGENCE_API_KEY = getattr(settings, 'IOINTELLIGENCE_API_KEY', None)

SYSTEM_PROMPT = getattr(settings, 'CHATBOT_SYSTEM_PROMPT', "Сен пайдалы ЖИ ассистент. Бір тілде жауап бер.")
HISTORY_LENGTH = getattr(settings, 'CHATBOT_HISTORY_LENGTH', 5)
MAX_RESPONSE_TOKENS = getattr(settings, 'CHATBOT_MAX_TOKENS', 1024)


def handle_user_query_direct(user_input):
    lower_input = user_input.lower()

    # Handle catalog and search related queries
    if "каталог" in lower_input or "категории" in lower_input:
        catalog_url = reverse('catalog')
        return f"Вы можете просмотреть полный каталог автомобилей по ссылке: {catalog_url}\n\nТам вы найдете удобную навигацию по брендам и моделям."
    
    if "поиск" in lower_input or "найти" in lower_input or"искать" in lower_input:
        search_url = reverse('car_search')
        return f"Для поиска автомобилей воспользуйтесь нашей системой расширенного поиска: {search_url}\n\nТам вы сможете фильтровать по марке, модели, году выпуска, цене и другим параметрам."

    if "бренды" in lower_input or "марки" in lower_input:
        brands = Brand.objects.all().order_by('name')
        if brands.exists():
            brand_names = ", ".join([brand.name for brand in brands])
            return f"На сайте представлены следующие бренды: {brand_names}."
        else:
            return "На сайте пока нет доступных брендов."

    if "модели" in lower_input:
        found_brand = None
        for brand in Brand.objects.all():
            if brand.name.lower() in lower_input:
                found_brand = brand
                break

        if found_brand:
            models = Model.objects.filter(brand=found_brand).order_by('name')
            if models.exists():
                model_names = ", ".join([model.name for model in models])
                return f"Для бренда {found_brand.name} доступны следующие модели: {model_names}."
            else:
                return f"Для бренда {found_brand.name} пока нет доступных моделей."
        else:
             all_models = Model.objects.select_related('brand').order_by('brand__name', 'name')
             if all_models.exists():
                 model_list = [f"{m.brand.name} {m.name}" for m in all_models]
                 if len(model_list) > 20:
                      return f"На сайте есть модели следующих брендов и названий (показаны не все): {', '.join(model_list[:20])}, и т.д."
                 else:
                      return f"На сайте представлены следующие модели: {', '.join(model_list)}."
             else:
                 return "На сайте пока нет доступных моделей."

    if "автомобили" in lower_input or "машины" in lower_input or "есть в наличии" in lower_input:
        cars = Car.objects.select_related('brand', 'model').all()
        if cars.exists():
            car_list = [
                f"{car.brand.name} {car.model.name} ({car.year}, {car.mileage} км) - ${car.price}"
                for car in cars
            ]
            return "Вот список доступных автомобилей:\n" + "\n".join(car_list)
        else:
            return "На сайте пока нет доступных автомобилей."

    return None


def get_bot_response(user_input, message_history_queryset):
    if not IOINTELLIGENCE_API_KEY:
        print("ERROR: IOINTELLIGENCE_API_KEY is not configured in settings.")
        return "Извините, сервис временно недоступен из-за отсутствия API ключа."

    current_system_prompt = SYSTEM_PROMPT

    messages = [{"role": "system", "content": current_system_prompt}]

    recent_history = message_history_queryset.order_by('-timestamp')[:HISTORY_LENGTH * 2]
    for msg in reversed(list(recent_history)):
        role = "user" if msg.sender == 'user' else "assistant"
        messages.append({"role": role, "content": msg.message})

    try:
        cars = Car.objects.select_related('brand', 'model').all()
        if cars.exists():
            car_list = [
                f"{car.brand.name} {car.model.name} ({car.year}, {car.mileage} км) - ${car.price}"
                for car in cars
            ]
            available_cars_info = "Список доступных автомобилей:\n" + "\n".join(car_list)
        else:
            available_cars_info = "На сайте пока нет доступных автомобилей."

        messages.append({"role": "system", "content": f"Информация для ответа пользователю: {available_cars_info}"})

    except Exception as e:
        print(f"Warning: Could not fetch car info for chatbot context: {e}")

    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": MAX_RESPONSE_TOKENS,
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {IOINTELLIGENCE_API_KEY}"
    }

    try:
        response = requests.post(INTELLIGENCE_API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        response_data = response.json()

        choices = response_data.get("choices", [])
        if choices and isinstance(choices, list) and len(choices) > 0:
            message_data = choices[0].get("message", {})
            assistant_message = message_data.get("content", "")
            if assistant_message and isinstance(assistant_message, str):
                return assistant_message.strip()
            else:
                print("Удаленная нейросеть вернула пустое или некорректное сообщение:", response_data)
                return "Извините, от нейросети пришел пустой или некорректный ответ."
        else:
            print("Формат ответа удаленной нейросети ошибочный или нет выбора:", response_data)
            return "Извините, формат ответа нейросети не распознан."

    except requests.exceptions.Timeout:
        print(f"Таймаут при запросе к удаленной нейросети ({INTELLIGENCE_API_URL}).")
        return "Извините, нейросеть долго отвечает. Попробуйте позже."
    except requests.exceptions.ConnectionError:
        print(f"Ошибка соединения с удаленной нейросетью ({INTELLIGENCE_API_URL}). Убедитесь, что адрес верный и доступен.")
        return "Извините, не удается подключиться к нейросети."
    except requests.exceptions.RequestException as e:
        status_code = e.response.status_code if e.response is not None else "N/A"
        print(f"Ошибка запроса к удаленной нейросети ({status_code}): {e}")
        error_detail = ""
        if e.response is not None:
            try:
                error_detail = e.response.json()
            except json.JSONDecodeError:
                error_detail = e.response.text
            print("Error Response Detail:", error_detail)
        return f"Извините, произошла ошибка при обращении к нейросети. Код: {status_code}. Подробности в логах."
    except Exception as e:
        print(f"Неожиданная ошибка в get_bot_response: {e}")
        return "Извините, произошла внутренняя ошибка при обработке запроса."