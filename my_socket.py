import socket
import os
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.bufsize = 32768 
        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()
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
                clnt_sock.settimeout(30.0)  # 타임아웃 시간 증가 (30초)
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
                    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                    file_path = os.path.join(self.DIR_PATH, f'request_{timestamp}.bin')
                    with open(file_path, 'wb') as f:
                        f.write(response)
                    print(f"Saved request to {file_path}")

                    self.verify_bin_file(file_path)

                    try:
                        self.save_multipart_data(response)
                    except Exception as e:
                        print(f"Error processing request: {e}")
                        clnt_sock.sendall(b"HTTP/1.1 500 Internal Server Error \r\n\r\n")
                        continue

                    clnt_sock.sendall(self.RESPONSE)

                clnt_sock.close()

        except KeyboardInterrupt:
            print("\r\nStop the server...")
            self.sock.close()

    def save_multipart_data(self, response):
        headers, _, body = response.partition(b'\r\n\r\n')
        headers_str = headers.decode('utf-8')

        boundary = self._extract_boundary(headers_str)  # 문자열로 바운더리 추출
        if not boundary:
            print("No boundary found in the headers.")
            return 
        
        boundary = boundary.encode()  # 바운더리 문자열을 바이트로 변환
        parts = body.split(b'--' + boundary)  # 바이트로 된 바운더리로 본문 분리

        saved_files = set() # 이미지 중복 저장 방지
        for part in parts:
            part = part.strip()
            if part and b'Content-Disposition' in part:
                disposition = part.split(b'\r\n\r\n')[0]
                filename = self._extract_filename(disposition)  # 바이트 문자열로 파일 이름 추출
                if filename and filename not in saved_files: # 이미지 중복 저장 방지
                    image_data = part.split(b'\r\n\r\n')[1].rstrip(b'\r\n--')
                    self._save_image(filename, image_data)
                    saved_files.add(filename)

    def _extract_boundary(self, headers):
        for line in headers.split('\r\n'):
            if 'Content-Type: multipart/form-data' in line:
                parts = line.split('boundary=')
                if len(parts) > 1:
                    return parts[1].strip()
        return None
    
    def _extract_filename(self, disposition):
        try:
            disposition_str = disposition.decode('utf-8')
            for part in disposition_str.split(';'):
                if 'filename=' in part:
                    filename = part.split('=')[1].strip().strip('"')
                    print(f"Extracted filename: {filename}")
                    return filename.split('"')[0]    
        except UnicodeDecodeError:
            print("Failed to decode disposition header.") 
        return None
    
    def _save_image(self, filename, image_data):
        if not filename:
            print("No valid filename found. Skipping save.")
            return 
        image_path = os.path.join(self.DIR_PATH, filename)
        try:
            with open(image_path, 'wb') as img_file:
                img_file.write(image_data)
            print(f"Saved image to {image_path}")

        except Exception as e:
            print(f"Error saving image: {e}")


    def verify_bin_file(self, file_path):
        """저장된 BIN 파일 검증"""
        try:
            # 파일 크기 확인
            file_size = os.path.getsize(file_path)
            print(f"BIN 파일 크기: {file_size} bytes")

            # 파일 내용 일부 확인 (앞 100바이트 미리보기)
            with open(file_path, 'rb') as f:
                preview = f.read(100)
                print(f"파일 미리보기 (앞 100바이트): {preview}")

        except Exception as e:
            print(f"BIN 파일 검증 중 오류: {e}")
    

if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)
