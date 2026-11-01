import os
from pathlib import Path
from copy import deepcopy
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
import json,hashlib,shutil,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
REF=Path(os.environ['AICARE_REFERENCE_DOCX'])
OUT=ROOT/'NHAT_KY_NGHIEN_CUU_AI_CARE_PHU_LUC_V.docx'
shutil.copy2(REF,ROOT/'reference.docx')
refhash=hashlib.sha256(REF.read_bytes()).hexdigest()
(ROOT/'artifact.md').write_text('''# Hợp đồng biểu mẫu Phụ lục V
Nguồn định dạng: reference.docx, sao nguyên mẫu chính thức. Mẫu có 3 trang, 1 section, khổ Letter dọc 21,59 x 27,94 cm; lề trên/dưới 1,75 cm, trái 2,25 cm, phải 1,59 cm. Giữ hình học này.
Giữ 5 phần I–V, thứ tự trường thông tin, 8 cột nhật ký, các khung kê khai vai trò, lựa chọn hồ sơ và vùng chữ ký. Không tạo chữ ký hay xác nhận thay người phụ trách.
Times New Roman 12 cho nội dung và biểu mẫu; bảng nhật ký và bảng dữ liệu mở rộng dùng 11 pt. Giãn dòng đơn, chữ đen, hàng tiêu đề lặp; không chia một mục nhật ký qua hai trang.
Nội dung hướng dẫn được giữ khi cần để điền biểu mẫu. Bảng nhật ký được mở rộng bằng mẫu hàng có sẵn; điều chỉnh độ rộng cột để nội dung và kết quả đọc được. Phần II, III, IV, V bắt đầu trang để tránh tách biểu mẫu.
Trường thông tin cá nhân, lĩnh vực dự thi, địa điểm, phân công theo người, chi phí và hồ sơ chưa cung cấp để trống. Không tự gán công việc cho học sinh/người hướng dẫn.
Dữ liệu nội dung chỉ lấy từ dự án: tài liệu triển khai có ngày, mã nguồn, JUnit, benchmark, manifest và QA. Nhật ký người dùng đưa để tham khảo phạm vi không phải nguồn dữ kiện và không xuất hiện trong văn bản xuất.
Có 15 mốc công việc ngày 01/10–24/10/2026. Ngày các đợt cũ lấy từ báo cáo kỹ thuật có ghi ngày; không suy ra ngày tạo mô-đun từ commit nhập nguồn. Số liệu 35/235 giữ độc lập với 50 kiểm thử STT.
Phần IV gồm danh mục chứng cứ và trích số liệu trực tiếp. Phần V đánh dấu mục 4b và mô tả hỗ trợ Codex đã thực hiện trong dự án; không xác nhận hồ sơ đồng ý tham gia hay ý kiến chuyên gia.
Các phần gói mẫu không cần thay đổi giữ nguyên; document/styles/core/header/footer được sửa theo các trường trên. Không thêm hyperlink hay dữ liệu cá nhân trong metadata.
'''+f'\nSHA256 nguồn định dạng: {refhash}\n',encoding='utf-8')

# Evidence-backed chronology, independent of the supplied example journal.
entries=[
('01/10/2026','Chuẩn bị bản chạy Windows: xác định main.py, cấu hình PyQt5, thư viện và tài nguyên AI; tổ chức gói nguồn, tách dữ liệu sử dụng khỏi mã chương trình.','MC01','Có hồ sơ kiểm tra khởi tạo ứng dụng trên Windows và hướng dẫn SETUP/START. Đây là gói nguồn cần thiết lập môi trường, chưa phải gói runtime nhúng hoàn chỉnh.'),
('03/10/2026','Sửa SETUP v3: xác minh Python thực, kiểm tra .venv trước khi cài thư viện; xử lý launcher trả mã thành công nhưng thiếu runtime, đường dẫn có dấu cách và lần chạy thiết lập lại.','MC02','Hồ sơ kiểm tra ghi nhận SETUP dừng khi tạo môi trường thất bại, tái sử dụng môi trường hợp lệ và khởi tạo dashboard ở chế độ thử. Chưa thử trên máy Windows thứ hai hoàn toàn sạch.'),
('10/10/2026','Tích hợp bộ luật tiếng Việt cục bộ cho thao tác thuốc, bài tập và yêu cầu liên hệ; giữ dấu, phủ định và ngữ cảnh; kiểm tra hồ sơ thật, người nhận hợp lệ và xác nhận trước thao tác cần phê duyệt.','MC03','Hình thành luồng văn bản → luật → kiểm tra ngữ cảnh → dịch vụ nghiệp vụ. Yêu cầu hỗ trợ được lưu riêng với trạng thái gửi và xử lý; không dùng lời nói để tự ghi hoàn thành bài tập.'),
('15/10/2026','Sửa lỗi lưu số đo: bổ sung danh mục loại chỉ số bằng migration 008; kiểm tra toàn bộ dữ liệu trước khi ghi; thống nhất mã huyết áp giữa API và ứng dụng.','MC04','Hồ sơ ghi nhận 13 kiểm thử đạt trên CSDL riêng. API từ chối batch lỗi, chống ghi trùng và không lưu số đo dở; desktop đọc đúng huyết áp thử 128/84 mmHg. Không coi số đo thử là dữ liệu người bệnh.'),
('15/10/2026','Xây dựng tổng hợp biểu cảm theo cửa sổ hai giờ; tách thời gian quan sát khỏi thời gian mất camera; lưu trạng thái, xử lý khởi động lại và cập nhật cổng người nhà qua sự kiện.','MC05','Có kiểm tra mốc thời gian, chống thông báo lặp, tách hồ sơ và trường hợp mất mặt/camera. Kết quả là kiểm tra xử lý thời gian và tích hợp, chưa xác lập độ chính xác phân loại biểu cảm trên người cao tuổi.'),
('15/10/2026','Tích hợp người nhà tải MP3/WAV theo hồ sơ; kiểm tra nội dung tệp và quyền truy cập; hợp nhất danh mục nhạc trên desktop, không tự phát hay ngắt bài đang nghe khi nhận bài mới.','MC06','Hồ sơ kiểm tra có upload, Range GET, chống tệp giả, rollback và upload trùng. Máy QA đọc được bài mới; vị trí QMediaPlayer tăng khi phát với âm lượng 0. Chưa suy ra loa thực đã được kiểm tra.'),
('16/10/2026','Điều chỉnh STT giai đoạn trước: thay cấu hình Whisper Small CPU bằng Medium GPU, bổ sung bỏ DC, khuếch đại có giới hạn, giữ dấu/phủ định và giới hạn bản ghi tối đa 30 giây.','MC07','Lưu được hồ sơ thay đổi cấu hình và cách đo trên mẫu công khai. Đây là mốc lịch sử trước Zipformer; không dùng kết quả Whisper cũ để mô tả mô hình đang phát hành.'),
('24/10/2026','Nhập mã nguồn vào kho Git và kiểm kê các thành phần: ứng dụng người cao tuổi, cổng web theo vai trò, thuốc, số đo, phục hồi, trò chơi, âm nhạc và giọng nói.','MC08','Commit 1b7512e ghi nhận thời điểm nhập nguồn. Mốc này xác nhận ảnh chụp mã nguồn; không phải ngày bắt đầu xây dựng tất cả chức năng.'),
('24/10/2026','Chạy đợt kiểm thử thuốc, giải mã âm thanh, đăng ký hồ sơ, sức khỏe và đồng bộ cấu hình tập trên dữ liệu thử; lưu JUnit để xác định ca đạt và ca còn lỗi.','MC09','35 ca: 32 đạt, 3 không đạt, 0 lỗi thiết lập. Có trường hợp kỳ vọng nhãn giao diện chưa khớp. Giữ nguyên kết quả chưa đạt trong hồ sơ để tiếp tục xử lý.'),
('24/10/2026','Chạy đợt kiểm thử bổ sung cho luật giọng nói, yêu cầu hỗ trợ, bài tập, trò chơi và số đo; đối chiếu lỗi liên kết người nhận với lỗi thiết lập dữ liệu mẫu.','MC10','235 ca: 220 đạt, 3 không đạt, 12 lỗi thiết lập. Tổng hai đợt MC09–MC10: 270 ca, 252 đạt, 6 không đạt, 12 lỗi thiết lập; không quy đổi thành độ chính xác AI.'),
('24/10/2026','Chuyển STT sang Zipformer tiếng Việt 30M INT8 qua sherpa-onnx 1.12.40; giải mã CPU trong worker; kiểm tra file model, Unicode NFC và âm thanh đầu vào.','MC11','Với tệp mẫu 3,74 giây, ba lượt giải mã là 171/62/52 ms; nạp model 1.958 ms. Đợt STT riêng ghi nhận 50 ca đạt. Chưa có WER/CER trên tập giọng người dùng.'),
('24/10/2026','Sửa vòng đời micro: một lần bấm có thể chờ model rồi bắt đầu ghi; không đóng micro chỉ vì dữ liệu cùng hồ sơ cập nhật; tách hiển thị transcript khỏi việc thực hiện lệnh khi ngữ cảnh cũ đã đổi.','MC12','Kiểm thử xác nhận tiếp tục ghi với cùng người bệnh, hủy khi đổi người bệnh và không thực hiện lệnh từ ngữ cảnh cũ. Cần kiểm tra thêm thiết bị thu và tiếng ồn khi chuyển máy.'),
('24/10/2026','Chuẩn hóa gói PT/HP: đưa Python nhúng, model và thư viện đi kèm; gỡ faster-whisper và CTranslate2 và trọng số cũ; cập nhật cấu hình, manifest và cơ chế chuyển cấu hình STT cũ.','MC13','Cả hai runtime chạy được nhận dạng tệp tiếng Việt; launcher, dashboard offscreen, API, xác thực và dừng dịch vụ qua QA. Model bị thay checksum được phát hiện. Chưa thử Windows sạch với camera/micro thật.'),
('24/10/2026','Tạo lại hai ZIP phát hành, kiểm tra CRC và SHA-256; đối chiếu model, mã micro và manifest trong gói; giữ các tệp giao diện web riêng của PT/HP.','MC14','PT: 580.378.673 byte; HP: 580.372.889 byte, khoảng 553,5 MiB/bản. Hai ZIP qua CRC; không có gói faster-whisper và CTranslate2 hoặc trọng số Whisper trong thành phần chạy.'),
('24/10/2026','Biên tập báo cáo kết quả dự án theo cấu trúc kỹ thuật IIIa và tóm tắt IIIb; giữ riêng kết quả kiểm thử chức năng, kiểm tra mô hình và giới hạn ứng dụng; kết xuất và rà soát từng trang.','MC15','Báo cáo 12 trang; phần tóm tắt 235 từ theo cách đếm khoảng trắng, 281 từ khi tính cả tiêu đề và trường thông tin trang tóm tắt. Các số liệu đã đối chiếu với hồ sơ dự án.')]
registry=[
('MC01','docs/PORTABLE_WINDOWS_REPORT.md','Báo cáo đóng gói Windows ghi ngày 01/10/2026; cấu trúc gói nguồn và kiểm tra khởi tạo.'),
('MC02','docs/WINDOWS_SETUP_V3_REPORT.md; packaging/portable/test_setup.ps1','Hồ sơ SETUP v3 ghi ngày 03/10/2026 và kịch bản kiểm tra môi trường.'),
('MC03','docs/local_rules/HANDOFF.md; services/local_rules/','Bàn giao ghi ngày 10/10/2026; bộ luật, thực thi, quyền người nhận và hàng đợi hỗ trợ.'),
('MC04','docs/VITALS_SYNC_FIX.md; tests/test_vitals_sync_regression.py','Báo cáo sửa số đo ghi ngày 15/10/2026; 13 ca hồi quy được ghi trong báo cáo.'),
('MC05','docs/EMOTION_SUMMARY_UPDATE.md; services/emotion_summary_service.py','Hồ sơ tổng hợp biểu cảm ngày 15/10/2026 và mã xử lý thời gian quan sát.'),
('MC06','docs/FAMILY_MUSIC_UPDATE.md; services/family_music_service.py; services/music_playback.py','Hồ sơ nhạc ngày 15/10/2026; lưu trữ, kiểm tra tệp và phát âm thanh theo hồ sơ.'),
('MC07','docs/STT_ACCURACY_UPGRADE.md','Hồ sơ thay đổi cấu hình STT ghi ngày 16/10/2026. Số liệu cũ không được dùng thay cho benchmark Zipformer.'),
('MC08','Git commit 1b7512e66e0e04ba9d7eca2ffae022a550cec9d9; main.py; app/; services/; web/','Thời điểm commit: 24/10/2026, 14:54:06, UTC+7; dùng để xác định mốc nhập nguồn.'),
('MC09','runtime/report-verification/results.xml','JUnit: 24/10/2026, 14:59:52, UTC+7; 35 ca, 3 failure, 0 error.'),
('MC10','runtime/report-verification-additional/results.xml','JUnit: 24/10/2026, 15:00:35, UTC+7; 235 ca, 3 failure, 12 error.'),
('MC11','reports/local_stt/zipformer-benchmark.json; docs/STT_ZIPFORMER.md; models/manifest.json','Độ trễ trên tệp 0.wav, cấu hình Zipformer, hash bốn tệp mô hình và ghi nhận 50 kiểm thử STT.'),
('MC12','services/local_voice/controller.py; services/local_voice/dispatcher.py; app/local_voice_widget.py; tests/voice_ai/test_local_voice.py','Mã và kiểm thử vòng đời micro, đổi người bệnh, kết quả trễ và hiển thị transcript.'),
('MC13','packaging/windows_portable/; QA_REPORT.txt và VERSION.json của hai bản portable','Runtime nhúng, model cục bộ, kiểm tra launcher/Qt/API và loại bỏ runtime STT cũ.'),
('MC14','releases/PORTABLE_PT_VALIDATION.json; releases/PORTABLE_HP_VALIDATION.json; tệp .zip.sha256','Kích thước, số tệp, CRC và SHA-256 của hai ZIP mới.'),
('MC15','docs/report_phu_luc_iii/BAO_CAO_AI_CARE_THEO_PHU_LUC_III.docx; authoring_audit.json','Báo cáo và kết quả kiểm tra 12 trang; tóm tắt dưới 300 từ theo cách đếm khoảng trắng.')]

# Hash evidence parts in an internal authoring manifest, not the journal supplied for context.
evidence=[]
for code,locations,meaning in registry:
 for loc in locations.split('; '):
  p=PROJECT/loc
  if p.is_file():evidence.append({'id':code,'path':loc,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'evidence_audit.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')

doc=Document(REF);ps=list(doc.paragraphs);tables=list(doc.tables)
try:doc.styles['Title']
except KeyError:doc.styles.add_style('Title',WD_STYLE_TYPE.PARAGRAPH)
for name in ['Normal','Title','Heading 1','Heading 2','Heading 3']:
 st=doc.styles[name] if name in doc.styles else doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
 st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0);st.font.size=Pt(12)
 st.paragraph_format.line_spacing=1


def fmt(p,size=12,bold=None,align=None):
 p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(0)
 p.paragraph_format.widow_control=True
 if align is not None:p.alignment=align
 for r in p.runs:
  r.font.name='Times New Roman';r.font.size=Pt(size);r.font.color.rgb=RGBColor(0,0,0)
  if bold is not None:r.bold=bold
 return p

def setp(p,text,bold=None):
 p.text=text;fmt(p,bold=bold);return p

def insert_after(anchor,text,bold=False):
 el=OxmlElement('w:p');anchor._p.addnext(el);p=Paragraph(el,anchor._parent);p.add_run(text);fmt(p,bold=bold);return p

def make_table(anchor,headers,rows,widths):
 t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
 for i,h in enumerate(headers):t.rows[0].cells[i].text=h
 for row in rows:
  cells=t.add_row().cells
  for c,val in zip(cells,row):c.text=str(val)
 style_table(t,widths,11)
 anchor._p.addnext(t._tbl)
 return t

def style_table(t,widths,size):
 t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
 for c,w in zip(t.columns,widths):c.width=Cm(w)
 for n,row in enumerate(t.rows):
  trpr=row._tr.get_or_add_trPr()
  for old in list(trpr.findall(qn('w:trHeight'))):trpr.remove(old)
  if not trpr.find(qn('w:cantSplit')) is not None:trpr.append(OxmlElement('w:cantSplit'))
  if n==0 and trpr.find(qn('w:tblHeader')) is None:trpr.append(OxmlElement('w:tblHeader'))
  seen=set()
  for i,c in enumerate(row.cells):
   if id(c._tc) in seen:continue
   seen.add(id(c._tc));c.width=Cm(widths[i]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
   pr=c._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'000000');b.append(el)
   pr.append(b);margin=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:w'),'65');el.set(qn('w:type'),'dxa');margin.append(el)
   pr.append(margin)
   for p in c.paragraphs:fmt(p,size,n==0,WD_ALIGN_PARAGRAPH.LEFT);p.paragraph_format.keep_with_next=False

# Preserve source components and fill only supported slots.
for p in ps:fmt(p)
ps[3].style=doc.styles['Title'];fmt(ps[3],14,True,WD_ALIGN_PARAGRAPH.CENTER)
for node in [doc.styles['Title']._element,ps[3]._element]:
 for border in list(node.iter(qn('w:pBdr'))):border.getparent().remove(border)
setp(ps[6],'Tên dự án dự thi: HỆ THỐNG TRỢ LÝ AI HỖ TRỢ CHĂM SÓC VÀ PHỤC HỒI CHỨC NĂNG CHO NGƯỜI CAO TUỔI')
ps[7]._element.getparent().remove(ps[7]._element)
insert_after(ps[15],'Các mốc công việc ghi nhận trong nhật ký: từ 01/10/2026 đến 24/10/2026.')
for i in [5,16,18,28,35]:fmt(ps[i],12,True);ps[i].paragraph_format.keep_with_next=True
for i in [16,18,28,35]:ps[i].paragraph_format.page_break_before=True
# Expand the actual 8-column source table, keep the sign-off column blank.
t=tables[0]
for row in list(t.rows)[1:]:t._tbl.remove(row._tr)
for i,(date,content,proof,result) in enumerate(entries,1):
 cells=t.add_row().cells
 for c,text in zip(cells,[str(i),date.replace('/2026','/\n2026'),content,'…………','…………',proof+'\n(Xem mục IV)',result,'']):c.text=text
style_table(t,[.8,1.45,4.2,1.35,1.35,2.1,4.0,2.5],11)
# Keep all actual role/fee forms unassigned: project evidence cannot establish individual identity or payment.
for t in tables[1:]:
 t.autofit=False
 for row in t.rows:
  for c in row.cells:
   for p in c.paragraphs:fmt(p,12)
# Mark reproduced evidence, rather than claiming separate attachments have been supplied.
setp(ps[29],'Minh chứng dữ liệu được đính kèm Nhật ký này: Có [X]    Không [ ]')
setp(ps[31],'1. Hồ sơ kỹ thuật và mã nguồn được kê khai theo mã minh chứng MC01–MC15 dưới đây.')
setp(ps[32],'2. Dữ liệu kiểm thử được trích trực tiếp tại mục IV gồm JUnit, benchmark Zipformer và kết quả kiểm tra hai ZIP.')
setp(ps[33],'3. Tệp dữ liệu gốc, mã nguồn và gói phát hành được lưu tại hồ sơ dự án để xuất trình khi được yêu cầu.')
ps[34]._element.getparent().remove(ps[34]._element)
anchor=insert_after(ps[33],'Danh mục minh chứng',True)
reg=make_table(anchor,['Mã','Tài liệu hoặc dữ liệu trong dự án','Nội dung đối chiếu'],registry,[1.4,8.35,8.0])
# Insert paragraphs after tables through an explicit paragraph anchor.
el=OxmlElement('w:p');reg._tbl.addnext(el);a=Paragraph(el,doc._body);a.add_run('Trích dữ liệu kiểm thử ngày 24/10/2026');fmt(a,bold=True);a.paragraph_format.keep_with_next=True
jrows=[]
for label,rel in [('Đợt 1 (MC09)','runtime/report-verification/results.xml'),('Đợt 2 (MC10)','runtime/report-verification-additional/results.xml')]:
 suite=ET.parse(PROJECT/rel).getroot().find('testsuite');attrs=suite.attrib
 total=int(attrs['tests']);fail=int(attrs['failures']);error=int(attrs['errors']);skip=int(attrs.get('skipped',0));jrows.append([label,total,total-fail-error-skip,fail,error])
res=make_table(a,['Đợt','Tổng ca','Đạt','Không đạt','Lỗi thiết lập'],jrows+[['Tổng hai đợt',270,252,6,12]],[5.0,2.8,2.8,3.5,3.65])
el=OxmlElement('w:p');res._tbl.addnext(el);a=Paragraph(el,doc._body);a.add_run('Nguồn: Hai tệp results.xml kê khai tại MC09 và MC10. Đơn vị là ca kiểm thử phần mềm, không phải người tham gia nghiên cứu.');fmt(a)
a=insert_after(a,'Benchmark Zipformer trên CPU (MC11)',True);a.paragraph_format.keep_with_next=True
b=json.loads((PROJECT/'reports/local_stt/zipformer-benchmark.json').read_text(encoding='utf-8'))
bench=make_table(a,['Chỉ tiêu','Giá trị được ghi nhận'],[['Thời lượng tệp mẫu','3.740 ms (3,74 giây)'],['Nạp mô hình lần đầu',str(b['cold_load_ms'])+' ms'],['Thời gian ba lượt giải mã',' / '.join(str(r['inference_ms']) for r in b['results'])+' ms'],['Trung vị (p50)',str(b['p50_ms']).replace('.',',')+' ms']],[8.2,9.55])
el=OxmlElement('w:p');bench._tbl.addnext(el);a=Paragraph(el,doc._body);a.add_run('Nguồn: zipformer-benchmark.json. Mẫu 0.wav thuộc bộ mẫu phát hành model; phép đo không phải đánh giá WER/CER hay khảo sát người cao tuổi. Đợt 50 kiểm thử STT được ghi riêng trong STT_ZIPFORMER.md, không cộng vào tổng 270 ca.');fmt(a)
a=insert_after(a,'Dữ liệu kiểm tra gói phát hành (MC14)',True);a.paragraph_format.keep_with_next=True
for edition in ['PT','HP']:
 v=json.loads((PROJECT/f'releases/PORTABLE_{edition}_VALIDATION.json').read_text(encoding='utf-8'))
 a=insert_after(a,f"{edition}: {v['file']}; {v['bytes']:,} byte; {v['files']:,} tệp; CRC: {v['crc']}.".replace(',','.'))
 a=insert_after(a,'SHA-256: '+v['sha256'])
a=insert_after(a,'Nguồn: Hai tệp PORTABLE_PT_VALIDATION.json và PORTABLE_HP_VALIDATION.json. Các kết quả QA là trên máy build; chưa xác nhận camera, micro và vận hành dài giờ trên máy Windows sạch.')
# AI disclosure is factual for the actual work completed in this project.
old=ps[42].text.strip();setp(ps[42],'[X] '+old)
a=insert_after(ps[43],'Nội dung sử dụng công nghệ số/AI đã ghi nhận: Codex hỗ trợ đọc và sửa mã, viết và chạy kiểm thử, chuyển bộ STT sang Zipformer, sửa vòng đời micro, đóng gói PT/HP và biên tập báo cáo, nhật ký từ hồ sơ dự án. Các nội dung này cần được kê khai chi tiết tại Phụ lục VI.')
# Ensure signatures remain available for actual signatories; no dates or names are filled.
for i in [44,45,46,51,52]:fmt(ps[i],12)
# Page numbers, no identifying footer.
footer=doc.sections[0].footer
for p in footer.paragraphs:p.clear()
p=footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');p._p.append(f);fmt(p,11)
doc.core_properties.author='';doc.core_properties.last_modified_by='';doc.core_properties.title='Nhật ký nghiên cứu hệ thống AI Care theo Phụ lục V'
doc.save(OUT)
# No outside hyperlinks are necessary in this administrative artifact.
with ZipFile(OUT) as z:parts={i.filename:z.read(i.filename) for i in z.infolist()}
for n,data in list(parts.items()):
 if n.endswith('.rels'):
  tr=etree.fromstring(data)
  for e in list(tr):
   if e.get('TargetMode')=='External':tr.remove(e)
  parts[n]=etree.tostring(tr,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
 for n,data in parts.items():z.writestr(n,data)
(ROOT/'authoring_audit.json').write_text(json.dumps({'output':str(OUT),'entry_count':len(entries),'evidence_count':len(registry),'reference_sha256':refhash,'input_journal_used_as_factual_source':False,'dates_based_on':'Dated project records and artifact metadata; no invented individual assignments'},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT);print('Entries',len(entries),'evidence items',len(registry))
