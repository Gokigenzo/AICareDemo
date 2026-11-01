"""Read-only audio dependency/device check. Never opens a recording stream."""
import sys
import platform


def main():
    print('Python:', sys.executable)
    try:
        import sounddevice as sd
    except (ImportError, OSError) as exc:
        print('Chưa sẵn sàng:', str(exc))
        if platform.system() == 'Linux' and 'PortAudio' in str(exc):
            print('Ubuntu/Debian: sudo apt-get install libportaudio2')
        return 1
    try:
        devices = sd.query_devices()
        print(devices)
        device = sd.query_devices(kind='input')
        print('Micro mặc định:', device['name'])
        sd.check_input_settings(channels=1, dtype='float32', samplerate=device['default_samplerate'])
        print('Thiết bị hỗ trợ cấu hình ghi. Chưa thu âm; thử bằng nút micro trong ứng dụng.')
        return 0
    except Exception as exc:
        print('Chưa truy cập được micro:', str(exc))
        print('Kiểm tra micro mặc định và quyền âm thanh trong cài đặt hệ điều hành.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
