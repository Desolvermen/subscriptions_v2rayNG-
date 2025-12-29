import requests
import os
import hashlib
from datetime import datetime

# Конфигурация - одна ссылка для протокола Trojan
TROJAN_URL = "https://istanbulsydneyhotel.com/blogs/site/sni.php?kind=trojan"
OUTPUT_DIR = "subscriptions"
OUTPUT_FILENAME = "trojan_subscriptions.txt"

def fetch_trojan_data():
    """Загрузка данных по протоколу Trojan"""
    try:
        print(f"🔗 Загружаем Trojan-подписки с: {TROJAN_URL}")
        response = requests.get(TROJAN_URL, timeout=15)
        response.raise_for_status()
        
        content = response.text.strip()
        if not content:
            print("⚠️  Получен пустой ответ")
            return None, False
        
        print(f"✅ Успешно загружено {len(content)} символов")
        print(f"📊 Найдено строк: {len(content.splitlines())}")
        return content, True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при загрузке: {e}")
        return None, False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return None, False

def save_trojan_file(content):
    """Сохранение Trojan-подписок в файл"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        filepath = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        
        # Создаем информативный заголовок
        header = "🚀 ПОДПИСКИ TROJAN (НАДЕЖНЫЙ ПРОТОКОЛ)\n"
        header += "=" * 50 + "\n"
        header += f"📅 Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"🔗 Источник: {TROJAN_URL}\n"
        header += "=" * 50 + "\n\n"
        
        # Сохраняем в файл
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + content)
        
        print(f"✅ Файл сохранен: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении файла: {e}")
        return False

def has_content_changed(new_content):
    """Проверка, изменилось ли содержимое"""
    filepath = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    
    if not os.path.exists(filepath):
        return True
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            old_content = f.read()
        
        # Извлекаем основное содержимое (после заголовка)
        lines = old_content.split('\n')
        
        # Ищем, где заканчивается заголовок
        content_start = 0
        for i, line in enumerate(lines):
            if 'trojan://' in line:  # Первая строка с конфигурацией
                content_start = i
                break
        
        # Если не нашли конфигураций, значит файл пустой
        if content_start == 0 and 'trojan://' not in old_content:
            return True
        
        # Сравниваем основное содержимое
        old_main_content = '\n'.join(lines[content_start:]) if content_start < len(lines) else ''
        old_hash = hashlib.md5(old_main_content.encode()).hexdigest()
        new_hash = hashlib.md5(new_content.encode()).hexdigest()
        
        changed = old_hash != new_hash
        if not changed:
            print("ℹ️  Содержимое не изменилось с прошлого обновления")
        
        return changed
        
    except Exception as e:
        print(f"⚠️  Ошибка при проверке изменений: {e}")
        return True

def filter_trojan_lines(content):
    """Фильтрация только Trojan конфигураций (опционально)"""
    lines = content.split('\n')
    trojan_lines = [line for line in lines if line.strip().startswith('trojan://')]
    
    if len(trojan_lines) < len(lines):
        print(f"ℹ️  Отфильтровано {len(lines) - len(trojan_lines)} не-Trojan строк")
    
    return '\n'.join(trojan_lines)

def main():
    print("=" * 60)
    print("🔄 ОБНОВЛЕНИЕ TROJAN-ПОДПИСОК")
    print("=" * 60)
    
    # Загружаем данные
    content, success = fetch_trojan_data()
    if not success or content is None:
        print("❌ Не удалось загрузить данные")
        return False
    
    # Опционально: фильтруем только Trojan строки
    filtered_content = filter_trojan_lines(content)
    
    if not filtered_content:
        print("⚠️  Не найдено ни одной Trojan-конфигурации")
        return False
    
    # Проверяем изменения
    if has_content_changed(filtered_content):
        # Сохраняем обновленные данные
        if save_trojan_file(filtered_content):
            print("✅ Trojan-подписки успешно обновлены!")
            
            # Показываем несколько первых конфигураций для проверки
            lines = filtered_content.split('\n')
            print(f"\n📋 Примеры конфигураций ({min(3, len(lines))} из {len(lines)}):")
            for i in range(min(3, len(lines))):
                if lines[i].strip():
                    print(f"  {lines[i][:80]}...")
            
            return True
        else:
            print("❌ Ошибка при сохранении файла")
            return False
    else:
        print("✅ Обновление не требуется (данные не изменились)")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
