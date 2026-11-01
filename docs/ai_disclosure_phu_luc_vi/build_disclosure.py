import os
from pathlib import Path
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parent
REF=Path(os.environ['AICARE_REFERENCE_DOCX'])
OUT=ROOT/'PHIEU_KHAI_BAO_SU_DUNG_AI_AI_CARE_PHU_LUC_VI.docx'
shutil.copy2(REF,ROOT/'reference.docx')
(ROOT/'artifact.md').write_text('''# Biểu mẫu Phụ lục VI
Bản mẫu giữ nguyên tại reference.docx. Giữ khổ Letter dọc 21,59 x 27,94 cm, lề trên 1,75 cm, dưới 0,5 cm, trái 2,25 cm, phải 1,59 cm; hai phần I và II cùng các vùng chữ ký cuối.
Giữ bảng công cụ 5 cột và khung nhật ký câu lệnh 1 cột. Mở rộng nội dung theo số công cụ và tình huống sử dụng có bằng chứng. Body Times New Roman 12, bảng 11; tiêu đề đen; không thêm đường kẻ dưới tiêu đề.
Điền tên dự án; để trống danh tính, lĩnh vực đăng ký, cơ sở, đơn vị, địa điểm/ngày ký và chữ ký. Không xác nhận thay người hướng dẫn hay nhóm.
Công cụ trợ giúp: OpenAI Codex với đóng góp đáng kể trong mã, kiểm thử, đóng gói và tài liệu. Công cụ trong sản phẩm: Zipformer/sherpa-onnx, MediaPipe, OpenCV, PyTorch/ExpressionNet; phần mềm số hỗ trợ kiểm thử và Word được kê riêng.
Prompt log chỉ ghi rõ là bản tóm tắt các yêu cầu/phản hồi trong phiên làm việc, không dựng hội thoại nguyên văn hay nhật ký đầy đủ. Không ghi PII hoặc đường dẫn tài khoản máy cá nhân.
Không nêu mô hình GPT cụ thể, số giờ, tỷ lệ đóng góp hay chi phí khi không có căn cứ. Không nhận AI tạo kết quả nghiên cứu trên người, xác minh lâm sàng hoặc mô hình được nhóm huấn luyện từ đầu.
Nguồn đối chiếu là mã, cấu hình, các artifacts kiểm thử và tài liệu dự án. Giữ bản mẫu gốc, không sửa nguồn.
'''+hashlib.sha256(REF.read_bytes()).hexdigest(),encoding='utf-8')
d=Document(REF);ps=list(d.paragraphs);tables=list(d.tables)
for name in ['Normal','Title','Heading 1','Heading 2']:
 st=d.styles[name] if name in d.styles else d.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
 st.font.name='Times New Roman';st.font.size=Pt(12);st.font.color.rgb=RGBColor(0,0,0)
 st.paragraph_format.line_spacing=1
 if name=='Title':
  for el in list(st._element.iter(qn('w:pBdr'))):el.getparent().remove(el)

def fmt(p,size=12,bold=None,align=None):
 p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(0);p.paragraph_format.widow_control=True
 if align is not None:p.alignment=align
 for r in p.runs:
  r.font.name='Times New Roman';r.font.size=Pt(size);r.font.color.rgb=RGBColor(0,0,0)
  if bold is not None:r.bold=bold
 return p

def insert(anchor,text,bold=False):
 el=OxmlElement('w:p');anchor._p.addnext(el);p=Paragraph(el,anchor._parent);p.add_run(text);fmt(p,bold=bold);return p

def tablefmt(t,widths):
 t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
 for c,w in zip(t.columns,widths):c.width=Cm(w)
 for n,row in enumerate(t.rows):
  pr=row._tr.get_or_add_trPr()
  for e in list(pr.findall(qn('w:trHeight'))):pr.remove(e)
  if pr.find(qn('w:cantSplit')) is None:pr.append(OxmlElement('w:cantSplit'))
  if n==0 and pr.find(qn('w:tblHeader')) is None:pr.append(OxmlElement('w:tblHeader'))
  for i,c in enumerate(row.cells):
   c.width=Cm(widths[i]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
   for p in c.paragraphs:fmt(p,11,n==0,WD_ALIGN_PARAGRAPH.LEFT);p.paragraph_format.keep_with_next=False
   tc=c._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    e=OxmlElement('w:'+side);e.set(qn('w:w'),'75');e.set(qn('w:type'),'dxa');m.append(e)
   tc.append(m)

for p in ps:fmt(p)
ps[3].style=d.styles['Title'];fmt(ps[3],14,True,WD_ALIGN_PARAGRAPH.CENTER)
for el in list(ps[3]._p.iter(qn('w:pBdr'))):el.getparent().remove(el)
ps[7].text='Tên dự án dự thi: HỆ THỐNG TRỢ LÝ AI HỖ TRỢ CHĂM SÓC VÀ PHỤC HỒI CHỨC NĂNG CHO NGƯỜI CAO TUỔI';fmt(ps[7])
ps[8]._p.getparent().remove(ps[8]._p)
for i in [6,15,16,17]:fmt(ps[i],12,True);ps[i].paragraph_format.keep_with_next=True
ps[15].paragraph_format.page_break_before=True
ps[17].paragraph_format.page_break_before=True
rows=[
('1','OpenAI Codex\nTrợ lý lập trình AI','Đọc và sửa mã; viết/chạy kiểm thử; chuyển STT sang Zipformer; sửa vòng đời micro; chuẩn hóa runtime và đóng gói hai ZIP PT/HP. Biên tập báo cáo IIIa/IIIb, nhật ký V và phiếu khai báo VI.','Hỗ trợ trực tiếp, đáng kể; có tạo/sửa mã và nội dung tài liệu. Tác vụ được giao bằng yêu cầu ngôn ngữ tự nhiên; AI thực hiện qua công cụ.','Không khai là chỉ tra cứu/chính tả. Chưa xác định model GPT cụ thể hoặc tỷ lệ đóng góp theo phần trăm.'),
('2','Zipformer tiếng Việt 30M INT8\nsherpa-onnx 1.12.40','Nhận âm thanh micro hoặc tệp, giải mã tiếng Việt trên CPU, trả transcript để hiển thị và chuyển vào bộ luật xử lý lệnh. Model được kèm trong bản portable.','Thành phần AI chạy trực tiếp trong sản phẩm; nạp mô hình có sẵn và suy luận cục bộ.','Không huấn luyện model từ đầu. Benchmark hiện có là trên tệp mẫu, chưa phải độ chính xác trên nhóm người cao tuổi.'),
('3','MediaPipe','Trích điểm mốc cơ thể cho đếm động tác phục hồi; trích điểm mốc khuôn mặt cho luồng xử lý biểu cảm.','Thư viện/mô hình có sẵn tích hợp trong pipeline thị giác cục bộ.','Số lần và tiến độ do logic dự án xử lý từ dữ liệu điểm mốc; chưa có đánh giá hiệu quả phục hồi lâm sàng.'),
('4','OpenCV\nDNN và LBPH','Xử lý ảnh, phát hiện khuôn mặt bằng DNN và nhận diện hồ sơ bằng LBPH; phục vụ chọn đúng người sử dụng trên desktop.','Sử dụng thư viện thị giác, mô hình phát hiện có sẵn và dữ liệu đăng ký của ứng dụng.','Không coi nhận diện khuôn mặt là kiểm chứng quyền truy cập web; quyền truy cập được kiểm tra theo tài khoản và liên kết chăm sóc.'),
('5','PyTorch và ExpressionNet','Nạp checkpoint ExpressionNet, kết hợp với tín hiệu điểm mốc/FACS và logic làm mượt trong mô-đun biểu cảm.','Mô hình có sẵn được dùng trong nguyên mẫu; khai báo việc nạp và suy luận, không tự nhận huấn luyện mới.','Biểu cảm là thông tin tham khảo, không phải chẩn đoán trạng thái tâm lý; chưa công bố độ chính xác trên người sử dụng thực.'),
('6','Python, pytest, Git; python-docx và LibreOffice','Lập trình, lưu phiên bản, kiểm thử tự động; tạo và kết xuất tài liệu Word để rà soát bảng, số trang và định dạng theo mẫu.','Công cụ số hỗ trợ quy trình; các lệnh được AI gọi khi thực hiện công việc đã giao.','Không phải tất cả công cụ ở dòng này đều là AI. Kết quả kiểm thử phần mềm không thay cho thử nghiệm trên người.')]
t=tables[0]
for r in list(t.rows)[1:]:t._tbl.remove(r._tr)
for vals in rows:
 cells=t.add_row().cells
 for c,v in zip(cells,vals):c.text=v
tablefmt(t,[.7,3.25,6.0,4.0,3.8])
insert(ps[16],'Phạm vi kê khai gồm công cụ AI hỗ trợ làm dự án và các thành phần AI/công nghệ số được tích hợp trong sản phẩm. Không gán kết quả do công cụ tạo ra thành công việc tự thực hiện độc lập.')
# Concise, explicit summaries of available human requests and AI actions; no fabricated transcript.
logs=[
('Chuyển mô hình STT','Yêu cầu: Thay faster-whisper bằng Zipformer để tăng tốc nhận giọng nói tiếng Việt.','Phản hồi và công việc AI: Kiểm tra luồng local_voice; cài sherpa-onnx; tải model tiếng Việt 30M INT8; sửa engine, cấu hình, script chuẩn bị model, dependency và kiểm thử. Chạy nhận dạng tệp mẫu.','Đối chiếu: engine.py, config.py, STT_ZIPFORMER.md và zipformer-benchmark.json.'),
('Sửa micro không thu được âm thanh','Yêu cầu: Micro mở chậm rồi tắt ngay sau khi bấm nhận giọng nói.','Phản hồi và công việc AI: Kiểm tra controller, widget và cơ chế đổi ngữ cảnh; sửa hành vi chờ model rồi tự ghi, giữ phiên với cùng người bệnh, hủy khi đổi người bệnh. Tách hiển thị transcript khỏi thực hiện lệnh cũ và chạy kiểm thử hồi quy.','Đối chiếu: controller.py, dispatcher.py và test_local_voice.py.'),
('Chuẩn hóa và đóng gói hai ZIP','Yêu cầu: Chốt Zipformer làm model chuẩn, cập nhật hai ZIP sẵn có và loại faster-whisper khỏi hệ thống.','Phản hồi và công việc AI: Gỡ dependency/trọng số STT cũ; cập nhật cache runtime, manifest và cấu hình; dựng PT/HP; chạy QA bằng Python nhúng, launcher, Qt, API và nhận dạng thật; nén và kiểm tra CRC/SHA-256.','Đối chiếu: QA_REPORT.txt và hai tệp PORTABLE_*_VALIDATION.json.'),
('Biên tập báo cáo theo Phụ lục III','Yêu cầu: Viết lại báo cáo dự án theo biểu mẫu Phụ lục III từ nội dung đã chỉnh sửa.','Phản hồi và công việc AI: Sắp xếp theo bốn mục dành cho dự án kỹ thuật, lập tóm tắt IIIb, cập nhật phần STT/đóng gói; định dạng Word và rà soát bản kết xuất 12 trang. Không tạo thêm kết quả khảo sát hoặc thử nghiệm lâm sàng.','Đối chiếu: Báo cáo IIIa/IIIb và hồ sơ kiểm tra trong report_phu_luc_iii.'),
('Biên soạn nhật ký theo Phụ lục V','Yêu cầu: Viết nhật ký theo mẫu V, lấy dữ liệu từ dự án và không dẫn chiếu nhật ký tham khảo trong bản xuất.','Phản hồi và công việc AI: Đối chiếu tài liệu có ngày, commit, JUnit, benchmark và QA; lập 15 mốc cùng danh mục minh chứng; giữ trống thông tin nhân sự/xác nhận; kết xuất và kiểm tra 10 trang.','Đối chiếu: Nhật ký Phụ lục V và evidence_audit.json trong journal_phu_luc_v.'),
('Soạn phiếu khai báo sử dụng AI','Yêu cầu: Điền thêm mẫu khai báo AI theo Phụ lục VI.','Phản hồi và công việc AI: Đọc mẫu; kê khai mức hỗ trợ của Codex và các thành phần AI trong hệ thống; lập bản tóm tắt yêu cầu/phản hồi, giữ trống danh tính và chữ ký để người có trách nhiệm hoàn thiện.','Đối chiếu: Phiếu này và hồ sơ mã nguồn/tài liệu được nêu trong từng mục.')]
t=tables[1];t.cell(0,0).text='Tên công cụ: OpenAI Codex\nTóm tắt yêu cầu và phản hồi liên quan đến dự án; không phải bản chép nguyên văn toàn bộ hội thoại.'
for r in list(t.rows)[1:]:t._tbl.remove(r._tr)
for i,(title,req,answer,proof) in enumerate(logs,1):
 c=t.add_row().cells[0];c.text=f'{i}. {title}\n{req}\n{answer}\n{proof}'
tablefmt(t,[17.75])
for row in list(t.rows)[1:]:
 p=row.cells[0].paragraphs[0]
 # One paragraph with soft line breaks intentionally keeps each summary together.
 p.runs[0].bold=False
# Retain official instructions and sign-off slots; clarify which artifacts are technical evidence.
# Product-model evidence is identified in the tools table.
# Keep space for actual signatures and date, without inventing independent verification.
for i in [19,20,21,25,26]:fmt(ps[i],12)
for i in [22,23,24]:
 if not ps[i].text.strip():ps[i]._p.getparent().remove(ps[i]._p)
ps[25].paragraph_format.space_before=Pt(18)
ps[25].paragraph_format.keep_with_next=True
d.core_properties.author='';d.core_properties.last_modified_by='';d.core_properties.title='Phiếu khai báo sử dụng công nghệ số và AI của dự án AI Care'
d.save(OUT)
with ZipFile(OUT) as z:parts={i.filename:z.read(i.filename) for i in z.infolist()}
for n,data in list(parts.items()):
 if n.endswith('.rels'):
  tr=etree.fromstring(data)
  for e in list(tr):
   if e.get('TargetMode')=='External':tr.remove(e)
  parts[n]=etree.tostring(tr,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
 for n,data in parts.items():z.writestr(n,data)
(ROOT/'audit.json').write_text(json.dumps({'output':str(OUT),'reference_sha256':hashlib.sha256(REF.read_bytes()).hexdigest(),'tools_rows':len(rows),'prompt_summaries':len(logs),'invented_identity_or_signatures':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT)


