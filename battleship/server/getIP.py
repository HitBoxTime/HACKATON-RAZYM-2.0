import socket

def get_ip_addresses():
    hostname = socket.gethostname()
    local_ip = socket.gethostname(hostname)

    print(hostname)
    print(local_ip)

    try:
        ip_list = socket.gethostbyname_ex(hostname)[2]
        for ip in ip_list:
            print(ip)
    except:
        print("Ошибка")

if __name__ == '__main__':
    get_ip_addresses()
    input()