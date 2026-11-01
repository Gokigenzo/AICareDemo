from pathlib import Path
import sys,os,importlib.util,tempfile
ROOT=Path(__file__).resolve().parent
bundle=Path(r'C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies')
lo=ROOT.parents[1]/'runtime/document-render/portable/program/soffice.exe'
os.environ['PATH']=str(bundle/'native/poppler/Library/bin')+os.pathsep+os.environ.get('PATH','')
tmp=ROOT/'render_tmp';tmp.mkdir(exist_ok=True);tempfile.tempdir=str(tmp)
os.environ['TEMP']=str(tmp);os.environ['TMP']=str(tmp)
script=Path(r'C:\Users\USER\.codex\plugins\cache\openai-primary-runtime\documents\26.1022.11436\skills\documents\render_docx.py')
spec=importlib.util.spec_from_file_location('docx_renderer',script);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod._resolve_soffice=lambda:str(lo)
sys.argv=[str(script),*sys.argv[1:]]
mod.main()
