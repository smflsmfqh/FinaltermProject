import socket
import os
from datetime import datetime
import threading
import platform

class SocketServer:
    def __init__(self):
        self.bufsize = 32768 
        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: failed to create the directory.")

    def run(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")
        
        try:
            while True:
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(30.0)  
                print("Request message from: ", req_addr)

                response = b""
                while True:
                    try:
                        part = clnt_sock.recv(self.bufsize)
                        if not part:
                            break
                        response += part
                    except socket.timeout:
                        print("Receiving data timed out.")
                        break

                if response:
                    # 요청 내용을 파일로 저장
                    self.save_request_to_file(response)

                    self.print_request(response)

                    # 클라이언트에게 HTTP 응답 전송
                    clnt_sock.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
                    clnt_sock.sendall(b'{"message": "Request received"}')

                clnt_sock.close()

        except KeyboardInterrupt:
            print("\r\nStop the server...")
            self.sock.close()

    def save_request_to_file(self, response):
        # 요청 내용이 HTTP 형식인지 확인
        try:
            headers, _, body = response.partition(b'\r\n\r\n')
            headers_str = headers.decode('utf-8')
            print(f"Received headers: {headers_str}")

            user_agent = self.extract_user_agent(headers_str)
            print(f"User-Agent: {user_agent}")

            # 요청을 request.bin 파일로 저장
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            file_path = os.path.join(self.DIR_PATH, f'request_{timestamp}.bin')
            with open(file_path, 'wb') as f:
                f.write(response)
            print(f"Saved request to {file_path}")

        except Exception as e:
            print(f"Error saving request: {e}")

    def extract_user_agent(self, headers_str):
        # User-Agent 헤더를 찾기
        for line in headers_str.splitlines():
            if line.startswith("User-Agent:"):
                return line.split(":", 1)[1].strip()  # User-Agent 값을 반환
        return "No User-Agent found"  # User-Agent가 없을 경우
    
    def print_request(self, response):
        # 요청을 출력하는 함수
        headers, _, body = response.partition(b'\r\n\r\n')
        headers_str = headers.decode('utf-8')
        print("\n--- Received Request ---")
        print(headers_str)  # 헤더 출력
        print("--- End of Request ---\n")

def get_dynamic_user_agent():
    # 시스템 정보를 기반으로 User-Agent 문자열 생성
    system = platform.system()
    version = platform.version()
    architecture = platform.architecture()[0]
    user_agent = f"Dalvik/2.1.0 (Linux; U; {system} {version}; {architecture} Build/TPB4.220624.004)"
    return user_agent


def send_request():
    # 서버 주소와 포트 설정
    host = '127.0.0.1'  # 서버가 실행 중인 호스트
    port = 8000

    dynamic_user_agent = get_dynamic_user_agent()
    # 요청 메시지 작성
    request = (
        "GET /api_root/Post/ HTTP/1.1\r\n"
        "Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyODgxMDQwOSwiaWF0IjoxNzI4NzI0MDA5LCJqdGkiOiJhZjI4ZWJhMjA3M2U0ZTE5OTUzZmE3ZGZhY2I3NWNhOSIsInVzZXJfaWQiOjF9.N5G51AxWUMn4jqdmysGQKHPc0wU8Q5iLHBtjwoAZa4Y\r\n"
        f"User-Agent: {dynamic_user_agent}\r\n" 
        "Host: 10.0.2.2:8000\r\n"
        "Connection: Keep-Alive\r\n"
        "Accept-Encoding: gzip\r\n"
        "\r\n"
    )

    # 소켓 생성
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 서버에 연결
        s.connect((host, port))
        # 요청 전송
        s.sendall(request.encode())

        # 응답 받기
        response = s.recv(4096)
        print("서버 응답:")
        print(response.decode())

if __name__ == "__main__":
    server = SocketServer()
    
    # 서버를 다른 스레드에서 실행
    server_thread = threading.Thread(target=server.run, args=("127.0.0.1", 8000))
    server_thread.start()
    
    # 클라이언트 요청 전송
    send_request()
