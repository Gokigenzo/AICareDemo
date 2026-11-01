"""Create an offline visual annotation bundle using decoded source timestamps."""
import argparse
import hashlib
import json
from pathlib import Path
import cv2

HTML = r'''<!doctype html><meta charset="utf-8"><title>Fall annotation — source PTS</title>
<style>body{font:16px sans-serif;margin:24px;background:#eef4f8}canvas{max-width:100%;background:#111}button,input,select{font:inherit;margin:6px;padding:6px}pre{white-space:pre-wrap}</style>
<h1>Gán nhãn video nguồn</h1><p>Vẽ bbox trên ảnh; không dùng kết quả detector làm nhãn. Bbox một phần cần ghi visibility. Đây là bản nháp một người rà soát, chưa adjudicated.</p>
<label>Người rà soát <input id="reviewer"></label><label>Subject <select id="subject"></select></label>
<label>Visibility <select id="visibility"><option>visible</option><option>partial</option><option>uncertain</option></select></label><br>
<button onclick="move(-1)">Trước</button><input id="slider" type="range" min="0" value="0"><button onclick="move(1)">Sau</button><b id="pts"></b><br>
<canvas id="canvas"></canvas><br>
<button onclick="mark('slip_start_sec')">Mốc bắt đầu ngã</button><button onclick="mark('impact_sec')">Mốc chạm đất</button><button onclick="mark('rest_sec')">Mốc nằm yên</button>
<button onclick="erase()">Xóa bbox tại frame này</button><button onclick="save()">Xuất JSON nháp</button>
<pre id="summary"></pre><script>
const bundle=__BUNDLE__,frames=bundle.frames,gt=bundle.ground_truth;
let index=0,start=null;const c=document.getElementById('canvas'),ctx=c.getContext('2d'),img=new Image();
const sel=document.getElementById('subject'),vis=document.getElementById('visibility'),slider=document.getElementById('slider');
gt.subjects.forEach(s=>{let o=document.createElement('option');o.value=s.subject_id;o.textContent=s.subject_id;sel.appendChild(o)});
slider.max=frames.length-1;slider.oninput=()=>{index=Number(slider.value);render()};sel.onchange=render;
function current(){return gt.subjects.find(s=>s.subject_id===sel.value)}
function move(delta){index=Math.max(0,Math.min(frames.length-1,index+delta));slider.value=index;render()}
function render(){document.getElementById('pts').textContent=`PTS nguồn ${frames[index].pts_sec.toFixed(3)}s`;img.src=frames[index].image;
 document.getElementById('summary').textContent=JSON.stringify(current(),null,2)}
img.onload=()=>{c.width=img.width;c.height=img.height;ctx.drawImage(img,0,0);let s=current().bbox_samples.find(s=>s.pts_sec===frames[index].pts_sec);
 if(s){ctx.strokeStyle='#ffbb00';ctx.lineWidth=3;ctx.strokeRect(s.bbox[0]*c.width,s.bbox[1]*c.height,s.bbox[2]*c.width,s.bbox[3]*c.height)}};
function xy(e){let r=c.getBoundingClientRect();return [Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))]}
c.onpointerdown=e=>{start=xy(e);c.setPointerCapture(e.pointerId)};
c.onpointerup=e=>{if(!start)return;let end=xy(e),bbox=[Math.min(start[0],end[0]),Math.min(start[1],end[1]),Math.abs(end[0]-start[0]),Math.abs(end[1]-start[1])];start=null;
 if(bbox[2]<.003||bbox[3]<.003)return;let s=current();s.bbox_samples=s.bbox_samples.filter(s=>s.pts_sec!==frames[index].pts_sec);
 s.bbox_samples.push({pts_sec:frames[index].pts_sec,frame_index:frames[index].frame_index,bbox,visibility:vis.value});s.bbox_samples.sort((a,b)=>a.pts_sec-b.pts_sec);render()};
function erase(){current().bbox_samples=current().bbox_samples.filter(s=>s.pts_sec!==frames[index].pts_sec);render()}
function mark(field){current().fall_event[field]=frames[index].pts_sec;render()}
function save(){let reviewer=document.getElementById('reviewer').value.trim();if(!reviewer){alert('Nhập tên người rà soát trước khi xuất');return}
 gt.reviewers=[reviewer];gt.annotation_status='SINGLE_REVIEW_DRAFT';gt.adjudication=null;
 let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(gt,null,2)],{type:'application/json'}));a.download='fall_annotations_draft.json';a.click();URL.revokeObjectURL(a.href)}
render();</script>'''


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('video');p.add_argument('--output',required=True);p.add_argument('--step',type=float,default=.25)
    args=p.parse_args()
    if args.step<=0:p.error('step must be positive')
    video=Path(args.video);out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    cap=cv2.VideoCapture(str(video));frames=[];next_pts=0.;index=0;last_pts=None
    if not cap.isOpened():raise ValueError('Cannot open source video')
    metadata=dict(filename=video.name,sha256=hashlib.sha256(video.read_bytes()).hexdigest(),width=int(cap.get(3)),height=int(cap.get(4)),fps=cap.get(cv2.CAP_PROP_FPS))
    try:
        while True:
            ok,frame=cap.read()
            if not ok:break
            pts=cap.get(cv2.CAP_PROP_POS_MSEC)/1000
            if last_pts is not None and pts<=last_pts:raise ValueError('Decoder PTS must increase for annotation')
            last_pts=pts
            if pts>=next_pts:
                name=f'frame_{index:06d}.jpg';scale=min(1.,960/frame.shape[1]);frame=cv2.resize(frame,(round(frame.shape[1]*scale),round(frame.shape[0]*scale)))
                if not cv2.imwrite(str(out/name),frame):raise IOError('Cannot write annotation frame')
                frames.append(dict(image=name,pts_sec=pts,frame_index=index));next_pts=pts+args.step
            index+=1
    finally:cap.release()
    metadata.update(decoded_frames=index,last_pts=last_pts)
    gt=dict(video_metadata=metadata,dataset_version='development-draft-v3',annotation_status='NOT VERIFIED',reviewers=[],adjudication=None,
            negative_intervals=[],subjects=[dict(subject_id=f'GT_PERSON_{i}',bbox_samples=[],fall_event=dict(event_id=f'fall_{i}',slip_start_sec=None,impact_sec=None,rest_sec=None)) for i in (1,2)])
    bundle=dict(frames=frames,ground_truth=gt)
    (out/'bundle.json').write_text(json.dumps(bundle,indent=2),encoding='utf-8')
    (out/'index.html').write_text(HTML.replace('__BUNDLE__',json.dumps(bundle).replace('</','<\\/')),encoding='utf-8')
    print(json.dumps(dict(decoded_frames=index,sampled_frames=len(frames),annotation_status='NOT VERIFIED',html=str(out/'index.html'))))


if __name__=='__main__':main()
