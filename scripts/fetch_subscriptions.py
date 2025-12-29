import requests
import os
import hashlib
from datetime import datetime

# Конфигурация - одна ссылка для протокола VLESS
VLESS_URL = "https://istanbulsydneyhotel.com/blogs/site/sni.php?kind=vless"
OUTPUT_FILENAME = "VLESS_Subscriptions.txt"  # Файл в корне репозитория

def fetch_vless_data():
    """Загрузка данных по протоколу VLESS"""
    try:
        print(f"🔗 Загружаем VLESS-подписки с: {VLESS_URL}")
        response = requests.get(VLESS_URL, timeout=20)
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

def save_vless_file(content):
    """Сохранение VLESS-подписок в файл в корне репозитория"""
    try:
        # Создаем информативный заголовок
        header = "⚡ ПОДПИСКИ VLESS (НАДЕЖНЫЙ ПРОТОКОЛ)\n"
        header += "=" * 50 + "\n"
        header += f"📅 Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"🔗 Источник: {VLESS_URL}\n"
        header += "💡 Совет: Ищите конфигурации с 'reality' и 'xtls' для максимальной надежности\n"
        header += "=" * 50 + "\n\n"
        
        # Сохраняем в файл в корне репозитория
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(header + content)
        
        print(f"✅ Файл сохранен: {OUTPUT_FILENAME}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении файла: {e}")
        return False

def has_content_changed(new_content):
    """Проверка, изменилось ли содержимое"""
    if not os.path.exists(OUTPUT_FILENAME):
        return True
    
    try:
        with open(OUTPUT_FILENAME, 'r', encoding='utf-8') as f:
            old_content = f.read()
        
        # Извлекаем основное содержимое (после заголовка)
        lines = old_content.split('\n')
        
        # Ищем, где заканчивается заголовок (первая строка с vless://)
        content_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('vless://'):  # Первая строка с конфигурацией
                content_start = i
                break
        
        # Если не нашли конфигураций, значит файл пустой
        if content_start == 0 and 'vless://' not in old_content:
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

def filter_vless_lines(content):
    """Фильтрация только VLESS конфигураций и их анализ"""
    lines = content.split('\n')
    vless_lines = []
    
    # Счетчики для статистики
    total_lines = len(lines)
    vless_count = 0
    reality_count = 0
    xtls_count = 0
    ws_count = 0
    tcp_count = 0
    
    for line in lines:
        line = line.strip()
        if line.startswith('vless://'):
            vless_lines.append(line)
            vless_count += 1
            
            # Анализ конфигурации для статистики
            if 'reality' in line.lower():
                reality_count += 1
            if 'xtls' in line.lower():
                xtls_count += 1
            if 'type=ws' in line.lower() or 'type=websocket' in line.lower():
                ws_count += 1
            if 'type=tcp' in line.lower():
                tcp_count += 1
    
    # Вывод статистики
    print(f"📊 Анализ конфигураций:")
    print(f"   Всего строк: {total_lines}")
    print(f"   VLESS конфигураций: {vless_count}")
    if vless_count > 0:
        print(f"   • Reality: {reality_count}")
        print(f"   • XTLS: {xtls_count}")
        print(f"   • WebSocket: {ws_count}")
        print(f"   • TCP: {tcp_count}")
    
    if vless_count < total_lines:
        print(f"ℹ️  Отфильтровано {total_lines - vless_count} не-VLESS строк")
    
    # Если есть Reality конфигурации, покажем одну как пример
    if reality_count > 0:
        print(f"\n💡 Найдены конфигурации Reality (самые надежные!)")
        for line in vless_lines:
            if 'reality' in line.lower():
                print(f"   Пример: {line[:100]}...")
                break
    
    return '\n'.join(vless_lines)

def main():
    print("=" * 60)
    print("🔄 ОБНОВЛЕНИЕ VLESS-ПОДПИСОК")
    print("=" * 60)
    
    # Загружаем данные
    content, success = fetch_vless_data()
    if not success or content is None:
        print("❌ Не удалось загрузить данные")
        return False
    
    # Фильтруем только VLESS строки и анализируем
    filtered_content = filter_vless_lines(content)
    
    if not filtered_content:
        print("⚠️  Не найдено ни одной VLESS-конфигурации")
        return False
    
    # Проверяем изменения
    if has_content_changed(filtered_content):
        # Сохраняем обновленные данные
        if save_vless_file(filtered_content):
            print(f"\n✅ VLESS-подписки успешно обновлены!")
            print(f"📁 Файл в корне репозитория: {OUTPUT_FILENAME}")
            
            # Показываем несколько первых конфигураций для проверки
            lines = filtered_content.split('\n')
            print(f"\n📋 Примеры конфигураций ({min(3, len(lines))} из {len(lines)}):")
            for i in range(min(3, len(lines))):
                if lines[i].strip():
                    # Обрезаем для лучшего отображения
                    config_line = lines[i].strip()
                    if len(config_line) > 100:
                        print(f"  {i+1}. {config_line[:100]}...")
                    else:
                        print(f"  {i+1}. {config_line}")
            
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
