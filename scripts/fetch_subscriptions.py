import requests
import os
import hashlib
from datetime import datetime
import concurrent.futures

# Конфигурация 8 стран
COUNTRIES = {
    'netherlands': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=nl',
        'flag': '🇳🇱',
        'name': 'Нидерланды'
    },
    'germany': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=de',
        'flag': '🇩🇪',
        'name': 'Германия'
    },
    'finland': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=fi',
        'flag': '🇫🇮',
        'name': 'Финляндия'
    },
    'turkey': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=tr',
        'flag': '🇹🇷',
        'name': 'Турция'
    },
    'uk': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=gb',
        'flag': '🇬🇧',
        'name': 'Великобритания'
    },
    'sweden': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=se',
        'flag': '🇸🇪',
        'name': 'Швеция'
    },
    'france': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=fr',
        'flag': '🇫🇷',
        'name': 'Франция'
    },
    'norway': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=no',
        'flag': '🇳🇴',
        'name': 'Норвегия'
    }
}

OUTPUT_DIR = "subscriptions"

def fetch_country_data(country_key, country_info):
    """Загрузка данных для одной страны"""
    try:
        response = requests.get(country_info['url'], timeout=10)
        response.raise_for_status()
        return country_key, response.text.strip(), True
    except Exception as e:
        print(f"  ✗ {country_info['flag']} {country_info['name']}: ошибка загрузки")
        return country_key, None, False

def save_country_file(country_key, country_info, content):
    """Сохранение данных в файл для страны"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        filename = f"{country_key}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Создаем заголовок с информацией
        header = f"# {country_info['flag']} {country_info['name']}\n"
        header += f"# URL: {country_info['url']}\n"
        header += f"# Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += "#" * 40 + "\n\n"
        
        # Сохраняем в файл
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + content)
        
        return True
    except Exception as e:
        print(f"  ✗ Ошибка сохранения {country_info['name']}: {e}")
        return False

def has_content_changed(country_key, new_content):
    """Проверка изменилось ли содержимое"""
    filepath = os.path.join(OUTPUT_DIR, f"{country_key}.txt")
    
    if not os.path.exists(filepath):
        return True
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            old_content = f.read()
        
        # Сравниваем хеши (игнорируя заголовок с датой)
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        # Сравниваем только основное содержимое
        old_hash = hashlib.md5('\n'.join(old_lines[4:]).encode()).hexdigest()
        new_hash = hashlib.md5(new_content.encode()).hexdigest()
        
        return old_hash != new_hash
    except:
        return True

def process_single_country(country_key, country_info):
    """Обработка одной страны"""
    # Загружаем данные
    country_key, content, success = fetch_country_data(country_key, country_info)
    
    if not success or not content:
        return country_key, False, "Ошибка загрузки"
    
    # Проверяем изменения
    if has_content_changed(country_key, content):
        # Сохраняем обновленные данные
        if save_country_file(country_key, country_info, content):
            return country_key, True, "Обновлен"
        else:
            return country_key, False, "Ошибка сохранения"
    else:
        return country_key, True, "Без изменений"

def main():
    print("=" * 50)
    print("🔄 ОБНОВЛЕНИЕ ПОДПИСОК (8 СТРАН)")
    print("=" * 50)
    
    results = []
    
    # Параллельная загрузка всех стран
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Запускаем задачи для всех стран
        futures = []
        for country_key, country_info in COUNTRIES.items():
            future = executor.submit(process_single_country, country_key, country_info)
            futures.append(future)
        
        # Собираем результаты
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=15)
                results.append(result)
            except:
                results.append(("unknown", False, "Таймаут"))
    
    # Выводим результаты
    print("\n📊 РЕЗУЛЬТАТЫ:")
    print("-" * 50)
    
    updated_count = 0
    for country_key, success, message in results:
        if country_key in COUNTRIES:
            country_info = COUNTRIES[country_key]
            status = "✅" if success else "❌"
            print(f"{status} {country_info['flag']} {country_info['name']}: {message}")
            if "Обновлен" in message:
                updated_count += 1
    
    print("-" * 50)
    print(f"📈 Обновлено файлов: {updated_count}/8")
    print(f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    # Возвращаем успех, если все страны обработаны
    return len([r for r in results if r[1]]) >= 4  # Хотя бы половина успешно

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
