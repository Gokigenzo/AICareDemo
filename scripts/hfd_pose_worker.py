"""Version-isolated OpenPifPaf inference. Binary frames in, JSON observations out."""
import argparse
import json
import struct
import sys
from pathlib import Path


def read_exact(stream, count):
    chunks = bytearray()
    while len(chunks) < count:
        data = stream.read(count-len(chunks))
        if not data:raise EOFError('Incomplete worker frame')
        chunks.extend(data)
    return bytes(chunks)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--weights',required=True)
    parser.add_argument('--resolution',type=float,default=.4)
    args=parser.parse_args()
    output=sys.stdout
    # Third-party diagnostics must never corrupt the response protocol.
    sys.stdout=sys.stderr
    import cv2
    import numpy as np
    import openpifpaf
    import torch
    from PIL import Image
    torch.set_num_threads(4);torch.manual_seed(0);np.random.seed(0);cv2.setNumThreads(1)
    openpifpaf.Predictor.device=torch.device('cpu')
    predictor=openpifpaf.Predictor(checkpoint=args.weights)
    torch_model=predictor.model
    sessions={}
    network_backend=['pytorch']
    if __import__('os').environ.get('FALL_HFD_ENGINE','auto') not in ('auto','torch','onnx'):
        raise ValueError('Unsupported FALL_HFD_ENGINE')
    def accelerated(image_batch):
        import os
        shape=image_batch.shape
        modelpath=Path(args.weights).with_name(f'{Path(args.weights).stem}-{shape[3]}x{shape[2]}.onnx')
        engine=os.environ.get('FALL_HFD_ENGINE','auto')
        if engine!='torch' and modelpath.is_file():
            import onnxruntime as ort
            key=str(modelpath)
            if key not in sessions:
                options=ort.SessionOptions();options.intra_op_num_threads=4;options.inter_op_num_threads=1
                sessions[key]=ort.InferenceSession(key,options,providers=['CPUExecutionProvider'])
            network_backend[0]='onnx'
            output=sessions[key].run(None,{'input_batch':image_batch.cpu().numpy()})
            return [torch.from_numpy(value) for value in output]
        if engine=='onnx':raise FileNotFoundError(f'ONNX model missing for input size: {modelpath}')
        network_backend[0]='pytorch'
        return torch_model(image_batch)
    predictor.model=accelerated
    decoder_parser=argparse.ArgumentParser()
    openpifpaf.decoder.cli(decoder_parser)
    decoder_args=decoder_parser.parse_args(['--seed-threshold','.5','--instance-threshold','.2'])
    openpifpaf.decoder.configure(decoder_args)
    def reply(value):
        output.write(json.dumps(value,allow_nan=False)+'\n');output.flush()
    reply(dict(type='ready',runtime=dict(python=sys.version.split()[0],openpifpaf=openpifpaf.__version__,torch=torch.__version__)))
    stream=sys.stdin.buffer
    while True:
        size=stream.read(4)
        if not size:return
        if len(size)!=4:raise ValueError('Incomplete protocol header')
        length=struct.unpack('<I',size)[0]
        if length>4096:raise ValueError('Oversized protocol header')
        header=json.loads(read_exact(stream,length))
        shape=tuple(header['shape'])
        if len(shape)!=3 or shape[2]!=3 or min(shape)<=0 or shape[0]*shape[1]>16000000:
            raise ValueError('Unsupported frame shape')
        image=np.frombuffer(read_exact(stream,int(np.prod(shape))),dtype=np.uint8).reshape(shape)
        h,w=image.shape[:2]
        tw,th=max(16,int(w*args.resolution//16)*16),max(16,int(h*args.resolution//16)*16)
        # Legacy reference passed BGR to PIL. Preserve this mode for checkpoint parity.
        resized=Image.fromarray(image).resize((tw,th),Image.BICUBIC)
        annotations,_,_=predictor.pil_image(resized)
        found=[]
        for annotation in annotations:
            points=np.asarray(annotation.data,dtype=float).copy()
            if points.shape!=(17,3) or not np.isfinite(points).all():continue
            model_points=points.copy()
            # Legacy extractor normalized padded tensor coordinates. With target
            # sizes divisible by16, CenterPadTight adds one right/bottom pixel.
            model_points[:,:2]/=[tw+1,th+1]
            points[:,:2]/=[tw,th]
            visible=points[:15,2]>0
            if not visible.any():continue
            low=points[:15,:2][visible].min(axis=0);high=points[:15,:2][visible].max(axis=0)
            for axis,dimension in enumerate((tw,th)):
                if high[axis]-low[axis]<5/dimension:
                    low[axis]-=2/dimension;high[axis]+=2/dimension
            box=[float(low[0]),float(low[1]),float(high[0]-low[0]),float(high[1]-low[1])]
            if min(box[2:])<=0:continue
            model_low=model_points[:15,:2][visible].min(axis=0)
            model_high=model_points[:15,:2][visible].max(axis=0)
            for axis,dimension in enumerate((tw,th)):
                if model_high[axis]-model_low[axis]<5/dimension:
                    model_low[axis]-=2/dimension;model_high[axis]+=2/dimension
            model_bbox=[[int(model_low[0]*w),int(model_low[1]*h)],[int(model_high[0]*w),int(model_high[1]*h)]]
            score=annotation.score
            found.append(dict(bbox=box,score=float(score() if callable(score) else score),keypoints=points.tolist(),
                              model_keypoints=model_points.tolist(),model_bbox=model_bbox))
        reply(dict(**{k:header[k] for k in ('source_id','run_id','frame_index','pts_sec')},observations=found,
                   timing=dict(network_sec=predictor.last_nn_time,decoder_sec=predictor.last_decoder_time,
                               network_backend=network_backend[0])))


if __name__=='__main__':
    try:main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.__stdout__.write(json.dumps({'error':str(error)})+'\n');sys.__stdout__.flush()
        sys.exit(1)
