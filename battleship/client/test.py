import socket
import sys

def test_connection(host, port=5555):
    print(f"Пытаюсь подключиться к {host}:{port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        print("✓ УСПЕШНО! Подключение установлено")
        sock.close()
        return True
    except Exception as e:
        print(f"✗ ОШИБКА: {e}")
        return False

if __name__ == "__main__":
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К СЕРВЕРУ")
    print("=" * 40)
    
    host = input("Введите IP сервера (или 'localhost' для теста локально): ").strip()
    if not host:
        host = "localhost"
    
    if test_connection(host):
        print("\nПодключение работает! Можно запускать игру.")
    else:
        print("\nПодключение не работает. Проверьте:")
        print("1. Сервер запущен на указанном IP")
        print("2. Брандмауэр разрешает подключения")
        print("3. Компьютеры в одной сети")
    
    input("\nНажмите Enter для выхода...")