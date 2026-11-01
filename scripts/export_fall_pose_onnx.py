"""Export existing local weights; never download a model implicitly."""
import argparse
from pathlib import Path
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('weights')
    args = parser.parse_args()
    path = Path(args.weights).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    os.environ['YOLO_AUTOINSTALL'] = 'false'
    os.environ.setdefault('YOLO_CONFIG_DIR', str(Path(__file__).resolve().parents[1]/'.cache'/'ultralytics'))
    from ultralytics import YOLO
    YOLO(str(path), task='pose').export(format='onnx', imgsz=640, dynamic=True,
                                     simplify=False, opset=17, device='cpu')


if __name__ == '__main__':
    main()
