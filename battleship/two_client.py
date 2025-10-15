import subprocess
import sys
import time
import os
import threading

def run_server():
    """Запускает сервер в отдельном процессе"""
    print("Запуск сервера...")
    
    server_path = os.path.join('server', 'server.py')
    if not os.path.exists(server_path):
        server_path = 'server.py'
    
    process = subprocess.Popen([sys.executable, server_path], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE,
                             text=True)
    
    def read_output():
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"[СЕРВЕР] {output.strip()}")
    
    thread = threading.Thread(target=read_output)
    thread.daemon = True
    thread.start()
    
    return process

def run_client(client_name, delay=0):
    """Запускает клиент в отдельном процессе"""
    time.sleep(delay)
    print(f"Запуск {client_name}...")

    process = subprocess.Popen([sys.executable, "main.py"])
    return process

if __name__ == "__main__":
    print("ЗАПУСК СИСТЕМЫ МОРСКОЙ БОЙ")
    print("=" * 50)
    
    server_process = run_server()
    time.sleep(3) 
    
    print("Сервер запущен! Ожидание подключений...")
    print("=" * 50)
    
    client1 = run_client("Клиент 1 (Игрок 1)", 1)
    time.sleep(3)
    
    client2 = run_client("Клиент 2 (Игрок 2)", 1)
    
    print("=" * 50)
    print("СИСТЕМА ЗАПУЩЕНА!")
    print("В каждом клиенте выберите 'Сетевая игра'")
    print("Используйте настройки по умолчанию: localhost:5555")
    print("=" * 50)
    print("Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        client1.wait()
        client2.wait()
        
        print("Остановка сервера...")
        server_process.terminate()
        server_process.wait()
        
    except KeyboardInterrupt:
        print("\nОстановка системы...")
        client1.terminate()
        client2.terminate()
        server_process.terminate()
        
        client1.wait()
        client2.wait()
        server_process.wait()
        
    print("Система остановлена.")