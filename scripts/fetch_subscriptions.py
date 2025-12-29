import requests
import os
import hashlib
from datetime import datetime
import concurrent.futures
import re

# Конфигурация 8 стран с русскими названиями
COUNTRIES = {
    'Нидерланды': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=nl',
        'flag': '🇳🇱',
        'filename': '🇳🇱 Нидерланды 🇳🇱'
    },
    'Германия': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=de',
        'flag': '🇩🇪',
        'filename': '🇩🇪 Германия 🇩🇪'
    },
    'Финляндия': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=fi',
        'flag': '🇫🇮',
        'filename': '🇫🇮 Финляндия 🇫🇮'
    },
    'Турция': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=tr',
        'flag': '🇹🇷',
        'filename': '🇹🇷 Турция 🇹🇷'
    },
    'Великобритания': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=gb',
        'flag': '🇬🇧',
        'filename': '🇬🇧 Великобритания 🇬🇧'
    },
    'Швеция': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=se',
        'flag': '🇸🇪',
        'filename': '🇸🇪 Швеция 🇸🇪'
    },
    'Франция': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=fr',
        'flag': '🇫🇷',
        'filename': '🇫🇷 Франция 🇫🇷'
    },
    'Норвегия': {
        'url': 'https://istanbulsydneyhotel.com/blogs/site/sni.php?country=no',
        'flag': '🇳🇴',
        'filename': '🇳🇴 Норвегия 🇳🇴'
    }
}

OUTPUT_DIR = "subscriptions"

def clean_filename(filename):
    """Очистка имени файла от небезопасных символов"""
    # Заменяем символы, которые могут быть проблемными в именах файлов
    safe_name = re.sub(r'[<>:"/\\|?*]', '', filename)
    safe_name = safe_name.replace(' ', '_')  # Заменяем пробелы на подчеркивания
    return safe_name + '.txt'

def fetch_country_data(country_name, country_info):
    """Загрузка данных для одной страны"""
    try:
        print(f"{country_info['flag']} Загружаем {country_name}...")
        response = requests.get(country_info['url'], timeout=15)
        response.raise_for_status()
        
        content = response.text.strip()
        print(f"  ✓ {country_info['flag']} {country_name}: {len(content)} символов")
        return country_name, content, True
    except requests.exceptions.RequestException as e:
        print(f"  ✗ {country_info['flag']} {country_name}: ошибка сети - {e}")
        return country_name, None, False
    except Exception as e:
        print(f"  ✗ {country_info['flag']} {country_name}: ошибка - {e}")
        return country_name, None, False

def save_country_file(country_name, country_info, content):
    """Сохранение данных в файл для страны"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Формируем имя файла в нужном формате
        filename_base = country_info['filename']  # 🇳🇱 Нидерланды 🇳🇱
        filename = clean_filename(filename_base)
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Создаем заголовок в том же формате
        header = f"{filename_base}\n"
        header += f"{country_info['url']}\n"
        header += f"Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += "=" * 50 + "\n\n"
        
        # Сохраняем в файл
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + content)
        
        print(f"  ✓ Файл сохранен: {filename}")
        return True
    except Exception as e:
        print(f"  ✗ Ошибка сохранения {country_name}: {e}")
        return False

def has_content_changed(country_name, country_info, new_content):
    """Проверка изменилось ли содержимое"""
    filename_base = country_info['filename']
    filename = clean_filename(filename_base)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        return True
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            old_content = f.read()
        
        # Извлекаем только основное содержимое (после заголовка)
        lines = old_content.split('\n')
        
        # Находим где начинается основное содержимое (после разделителя "=")
        content_start = 0
        for i, line in enumerate(lines):
            if '=====' in line:  # Ищем разделительную линию
                content_start = i + 1
                break
        
        # Сравниваем хеши основного содержимого
        old_main_content = '\n'.join(lines[content_start:]) if content_start < len(lines) else ''
        old_hash = hashlib.md5(old_main_content.encode()).hexdigest()
        new_hash = hashlib.md5(new_content.encode()).hexdigest()
        
        return old_hash != new_hash
    except Exception as e:
        print(f"  ⚠ Ошибка при проверке изменений {country_name}: {e}")
        return True

def process_single_country(country_name, country_info):
    """Обработка одной страны"""
    # Загружаем данные
    country_name, content, success = fetch_country_data(country_name, country_info)
    
    if not success or not content:
        return country_name, False, "Ошибка загрузки"
    
    # Проверяем изменения
    if has_content_changed(country_name, country_info, content):
        # Сохраняем обновленные данные
        if save_country_file(country_name, country_info, content):
            return country_name, True, "Обновлен"
        else:
            return country_name, False, "Ошибка сохранения"
    else:
        return country_name, True, "Без изменений"

def main():
    print("=" * 60)
    print("🔄 ОБНОВЛЕНИЕ ПОДПИСОК 8 СТРАН (РУССКИЕ НАЗВАНИЯ)")
    print("=" * 60)
    
    results = []
    
    # Параллельная загрузка всех стран
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Запускаем задачи для всех стран
        futures = []
        for country_name, country_info in COUNTRIES.items():
            future = executor.submit(process_single_country, country_name, country_info)
            futures.append(future)
        
        # Собираем результаты
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=20)
                results.append(result)
            except concurrent.futures.TimeoutError:
                results.append(("Таймаут", False, "Таймаут выполнения"))
                print("  ⚠ Одна из стран: превышено время ожидания")
            except Exception as e:
                results.append(("Ошибка", False, f"Ошибка: {e}"))
    
    # Выводим результаты
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ОБНОВЛЕНИЯ:")
    print("=" * 60)
    
    updated_count = 0
    total_countries = len(COUNTRIES)
    
    for country_name, success, message in results:
        if country_name in COUNTRIES:
            country_info = COUNTRIES[country_name]
            status = "✅" if success else "❌"
            print(f"{status} {country_info['flag']} {country_name}: {message}")
            if "Обновлен" in message:
                updated_count += 1
        else:
            print(f"❌ {country_name}: {message}")
    
    print("-" * 60)
    
    # Выводим список созданных файлов
    if os.path.exists(OUTPUT_DIR):
        print("📁 СОЗДАННЫЕ ФАЙЛЫ:")
        files = os.listdir(OUTPUT_DIR)
        for file in sorted(files):
            if file.endswith('.txt'):
                print(f"  📄 {file}")
    
    print("-" * 60)
    print(f"📈 ОБНОВЛЕНО: {updated_count}/{total_countries} стран")
    print(f"🕐 ВРЕМЯ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Возвращаем успех, если хотя бы половина стран обработана
    successful_count = len([r for r in results if r[1]])
    return successful_count >= total_countries / 2

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
