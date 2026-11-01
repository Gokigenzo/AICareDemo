import os
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from copy import deepcopy
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json,re,shutil

ROOT=Path(__file__).resolve().parent
SRC=Path(os.environ['AICARE_SOURCE_DOCX'])
REF=Path(os.environ['AICARE_REFERENCE_DOCX'])
OUT=ROOT/'BAO_CAO_AI_CARE_THEO_PHU_LUC_III.docx'
source=Document(SRC)
shutil.copy2(REF,ROOT/'reference.docx')
contract='''# Hợp đồng định dạng\nMẫu Phụ lục III được lưu nguyên trạng tại reference.docx.\nPhần IIIa dùng nhánh dự án kỹ thuật, 4 mục chính; IIIb là tóm tắt dưới 300 chữ, trang riêng cuối tài liệu.\nA4; lề trái 3 cm, phải 2 cm, trên/dưới 2 cm theo quy định bằng chữ trong mẫu (ưu tiên hơn thiết lập trang thực của tệp mẫu).\nTimes New Roman 13; giãn dòng đơn; cách đoạn 3 pt; chữ đen. Tiêu đề và tên dự án căn giữa, đề mục in đậm.\nKhông tên học sinh/trường/đơn vị, logo, QR, hyperlink hay URL. Không dùng ảnh chụp để tránh lộ thông tin nhận diện.\nNội dung mẫu hướng dẫn được thay bằng nội dung báo cáo; mẫu khoa học và các điều khoản hướng dẫn không đưa vào báo cáo điền hoàn chỉnh.\nCác đoạn bản gốc được giữ tối đa, chuyển về 4 mục kỹ thuật; có bổ sung tiêu chí đánh giá và diễn giải lựa chọn thiết kế từ chức năng có sẵn.\nSố liệu 270/252/6/12 được giữ như kết quả hai đợt cũ, tách khỏi 50 kiểm thử STT mới. Cập nhật dung lượng gói Zipformer theo kết quả đóng gói đã ghi nhận.\nCác phần OOXML ngoài document/styles/core/header/footer/relationships ảnh giữ theo bản mẫu khi không có nhu cầu thay đổi.\nKết xuất mặc định bị thiếu LibreOffice; không có Word COM hoặc WPS engine khả dụng trên máy. Cần kiểm tra bằng trình kết xuất khi có.\n'''
(ROOT/'artifact.md').write_text(contract+'\nSHA256 mẫu '+hashlib.sha256(REF.read_bytes()).hexdigest(),encoding='utf-8')
doc=Document(REF)
body=doc._element.body
for child in list(body):
 if child.tag!=qn('w:sectPr'):body.remove(child)
sec=doc.sections[0]
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
sec.left_margin=Cm(3);sec.right_margin=Cm(2);sec.top_margin=Cm(2);sec.bottom_margin=Cm(2)
sec.header_distance=Cm(.7);sec.footer_distance=Cm(.7)
for h in [sec.header,sec.footer]:
 for p in h.paragraphs:p.clear()
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
 try:st=doc.styles[name]
 except KeyError:st=doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
 st.font.name='Times New Roman';st.font.size=Pt(13);st.font.color.rgb=RGBColor(0,0,0)
 st.paragraph_format.space_before=Pt(0);st.paragraph_format.space_after=Pt(3);st.paragraph_format.line_spacing=1
 st.paragraph_format.widow_control=True
 st.paragraph_format.page_break_before=False
 if name.startswith('Heading'):st.paragraph_format.keep_with_next=True


def fmt(p,bold=False,align=None):
 p.alignment=align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
 f=p.paragraph_format;f.line_spacing=1;f.space_before=Pt(0);f.space_after=Pt(3);f.widow_control=True
 for r in p.runs:
  r.font.name='Times New Roman';r.font.size=Pt(13);r.font.color.rgb=RGBColor(0,0,0);r.bold=bold
  r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),'Times New Roman')
 return p

def para(text,style='Normal',bold=False,center=False):
 p=doc.add_paragraph(text,style);fmt(p,bold,WD_ALIGN_PARAGRAPH.CENTER if center else None)
 if text.startswith('Bảng '):p.paragraph_format.keep_with_next=True
 return p

def heading(text,level=1):
 p=para(text,'Heading '+str(level),True);p.paragraph_format.keep_with_next=True
 return p

def block(a,b):
 for i in range(a,b+1):
  p=source.paragraphs[i];text=p.text.strip()
  if not text or not any(c.isalnum() for c in text):continue
  if i==123:text='Máy cần đủ chỗ lưu bản giải nén, dữ liệu và tệp nhạc. Hai gói portable đã cập nhật Zipformer có dung lượng nén khoảng 553,5 MiB mỗi bản. Đây là dung lượng tệp phát hành, không phải mức RAM hay dung lượng tối thiểu khi chạy. Nếu máy thiếu thành phần hệ thống, người thiết lập sử dụng bộ cài thư viện đi kèm theo hướng dẫn. [8]'
  if i==88:text=text.replace('Mã nguồn đang làm việc đã cập nhật bộ nhận dạng sang','Bản portable đã thống nhất sử dụng bộ nhận dạng')
  text=text.replace('mô tả ở Phần II','mô tả ở mục 2').replace('của Bảng 1','của Bảng 2')
  if p.style.name in ['Heading 2','Heading 3','Research Topic']:
   clean=re.sub(r'^\d+(?:\.\d+)*\.\s*','',text)
   heading(clean,3)
  else:
   para(text)

def table(headers,rows,widths):
 t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Cm(w)
 for i,h in enumerate(headers):t.rows[0].cells[i].text=h
 for row in rows:
  cells=t.add_row().cells
  for c,text in zip(cells,row):c.text=str(text)
 for n,row in enumerate(t.rows):
  trPr=row._tr.get_or_add_trPr();flag=OxmlElement('w:cantSplit');trPr.append(flag)
  if n==0:
   tag=OxmlElement('w:tblHeader');trPr.append(tag)
  for i,c in enumerate(row.cells):
   c.width=Cm(widths[i]);tcpr=c._tc.get_or_add_tcPr();marg=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:w'),'70');el.set(qn('w:type'),'dxa');marg.append(el)
   tcpr.append(marg)
   borders=OxmlElement('w:tcBorders')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'000000');borders.append(el)
   tcpr.append(borders)
   for p in c.paragraphs:fmt(p,n==0,WD_ALIGN_PARAGRAPH.LEFT)
 return t

para('BÁO CÁO KẾT QUẢ THỰC HIỆN DỰ ÁN DỰ THI','Title',True,True)
para('IIIa Đối với dự án kỹ thuật','Subtitle',True,True)
para('HỆ THỐNG TRỢ LÝ AI HỖ TRỢ CHĂM SÓC\nVÀ PHỤC HỒI CHỨC NĂNG CHO NGƯỜI CAO TUỔI','Title',True,True)
para('AI Care & Rehabilitation Assistant',center=True)
para('Ngày 24 tháng 10 năm 2026',center=True)
heading('1. Vấn đề nghiên cứu hoặc cần giải quyết')
heading('1.1. Đòi hỏi thực tế và vấn đề đặt ra',2);block(25,27)
heading('1.2. Mục tiêu và phạm vi của giải pháp',2);block(29,33)
heading('1.3. Tiêu chí đánh giá giải pháp',2)
para('Các mục tiêu trên được cụ thể hóa thành tiêu chí kiểm tra nguyên mẫu. Tiêu chí về chức năng được đối chiếu bằng dữ liệu và trạng thái của từng luồng; tiêu chí liên quan đến người sử dụng hoặc độ chính xác mô hình cần phép đánh giá riêng.')
para('Bảng 1. Tiêu chí kiểm tra nguyên mẫu',bold=True)
table(['Tiêu chí','Cách đối chiếu'],[
('Thống nhất hồ sơ chăm sóc','Đăng ký, liên kết và truy xuất đúng hồ sơ giữa ứng dụng và các cổng web.'),
('Quản lý thuốc có trạng thái rõ','Đối chiếu hiệu lực đơn, lịch trong ngày, thao tác xác nhận và hủy đơn; phân biệt ghi nhận tự khai với xác minh thực tế.'),
('Theo dõi hoạt động và số đo','Kiểm tra việc lưu thời điểm đo, chỉ tiêu tập, tiến độ, phiên chơi và danh mục nhạc.'),
('Thao tác giọng nói có kiểm soát','Hiển thị văn bản đã nhận; kiểm tra đúng hồ sơ, ngữ cảnh và xác nhận trước khi thực hiện lệnh liên quan.'),
('Phân quyền và triển khai','Kiểm tra truy cập theo liên kết chăm sóc; nạp mô hình, khởi động và kiểm tra toàn vẹn gói portable.')],[5,11])
para('Nguồn: Tổng hợp từ mục tiêu, chức năng và hồ sơ kiểm tra của dự án [1]–[9].')
heading('2. Thiết kế và phương pháp nghiên cứu')
heading('2.1. Phân tích và lựa chọn giải pháp',2)
para('Vấn đề thiết kế là kết nối thao tác của người được chăm sóc với chỉ định và phản hồi của những người phụ trách. Giải pháp được chọn sử dụng hồ sơ nghiệp vụ chung, ứng dụng máy tính cho người cao tuổi và cổng web theo vai trò cho người nhà, bác sĩ, quản trị viên. Cách tổ chức này đáp ứng yêu cầu theo dõi dữ liệu từ nhiều giao diện mà không phải nhập lại cùng một thông tin ở từng nơi.')
para('Khâu nhận dạng hình ảnh và giọng nói được bố trí cục bộ để phù hợp gói portable. Đối với lời nói, mô hình chuyển âm thanh thành văn bản, còn bộ luật xử lý các yêu cầu đã định nghĩa. Những thao tác liên quan đến thuốc được kiểm tra thêm theo hồ sơ và lần uống đang có, thay vì chỉ dựa vào câu được nhận dạng. Lựa chọn này giới hạn phạm vi xử lý ở các chức năng chăm sóc đã xây dựng.')
para('Bản nhận dạng giọng nói được chuyển từ faster-whisper sang Zipformer tiếng Việt 30M INT8 qua sherpa-onnx, chạy CPU. Việc lựa chọn được kiểm tra bằng khả năng nạp model, nhận dạng tệp tiếng Việt và độ trễ trên máy phát triển. Chưa có phép thử đối chứng trên cùng tập giọng nói để kết luận mức cải thiện độ chính xác giữa hai mô hình. [9]')
heading('2.2. Kiến trúc nguyên mẫu và nền tảng vận hành',2);block(36,41)
heading('2.3. Phương pháp xây dựng và kiểm tra',2);block(43,43)
para('Với mỗi luồng, đầu vào là thao tác và dữ liệu thử; kết quả quan sát là trạng thái được lưu, quyền truy cập và thông tin đọc lại ở giao diện liên quan. Các tình huống bất lợi gồm dữ liệu không hợp lệ, thao tác lặp, hủy chỉ định, thay đổi hồ sơ và lỗi thiết lập. Việc chạy mô hình trên tệp mẫu được tách khỏi kiểm thử bộ luật xử lý văn bản và đánh giá trên người sử dụng.')
heading('2.4. Thiết kế các nhóm chức năng',2)
block(44,96)
heading('2.5. Quy trình sử dụng và điều kiện vận hành',2)
block(97,124)
heading('3. Thực hiện, chế tạo và kiểm tra')
heading('3.1. Xây dựng và hoàn thiện nguyên mẫu',2);block(127,128)
para('Trong đợt chuẩn hóa STT, nhóm đã đưa Zipformer vào luồng ghi âm của ứng dụng, gỡ faster-whisper và CTranslate2 khỏi môi trường chạy và hai bộ portable. Cơ chế micro được điều chỉnh để một lần bấm có thể chờ model sẵn sàng rồi bắt đầu ghi; cập nhật dữ liệu cùng người bệnh không đóng micro, còn đổi người bệnh vẫn hủy phiên. Nếu ngữ cảnh nghiệp vụ thay đổi, văn bản thu được vẫn hiển thị nhưng lệnh cũ không được tự động thực hiện. [7], [9]')
heading('3.2. Điều kiện và kết quả kiểm thử chức năng',2);block(130,130)
para('Bảng 2. Kết quả hai đợt kiểm thử chức năng trong hồ sơ báo cáo',bold=True)
table(['Đợt kiểm thử','Tổng','Đạt','Không đạt','Lỗi thiết lập'],[
('Thuốc, âm thanh, hồ sơ đăng ký, sức khỏe và cấu hình tập','35','32','3','0'),
('Bộ luật giọng nói, yêu cầu hỗ trợ, chuỗi bài tập, trò chơi và số đo','235','220','3','12'),
('Tổng hai đợt','270','252','6','12')],[7,1.6,1.6,2.7,3.1])
para('Nguồn: Hai hồ sơ JUnit trong hồ sơ kiểm thử dự án, ngày 24/10/2026 [1]–[7].')
block(133,138)
heading('3.3. Kiểm tra Zipformer và vòng đời micro',2)
para('Đợt kiểm thử riêng sau khi thay model ghi nhận 50 ca đạt, bao gồm kiểm tra STT, controller micro và nhận dạng tệp tiếng Việt thực trong bộ mẫu phát hành của model. Đây là đợt kiểm tra sau cập nhật, không cộng dồn với 270 ca trong Bảng 2 vì phạm vi kiểm tra có thể giao nhau. [9]')
para('Trên một tệp tiếng Việt dài 3,74 giây, ba lượt giải mã trong môi trường phát triển ghi nhận thời gian 171 ms, 62 ms và 52 ms; thời gian nạp model ban đầu là 1.958 ms. Các số đo mô tả độ trễ của trường hợp thử này. Chưa có tập dữ liệu và bản chép lời đối chiếu đủ để xác lập tỷ lệ lỗi từ hoặc ký tự trên giọng người sử dụng. [9]')
heading('3.4. Kiểm tra đóng gói và khởi chạy',2);block(140,140)
para('Hai bản portable PT và HP sử dụng Python 3.12 nhúng, thư viện và model Zipformer đi kèm. Người sử dụng giải nén toàn bộ rồi chạy tệp EXE; không cần cài Python hoặc tải model riêng. Dung lượng gói PT là 580.378.673 byte và HP là 580.372.889 byte. Cả hai đã qua kiểm tra nhận dạng bằng runtime nhúng, dashboard ở chế độ không hiển thị, API, đăng nhập, dừng dịch vụ, CRC và SHA-256 trên máy build. Chưa thử trên máy Windows sạch với camera và micro vật lý. [8]')
heading('4. Kết quả, kết luận và khả năng ứng dụng')
heading('4.1. Kết quả và đóng góp của nguyên mẫu',2);block(144,146)
heading('4.2. Khả năng ứng dụng',2)
para('Tại gia đình, nguyên mẫu có thể phục vụ trình diễn lịch chăm sóc trong ngày và thử nghiệm quy trình phối hợp giữa các vai trò: bác sĩ lập chỉ định, người cao tuổi xem và thực hiện công việc, người nhà ghi số đo và theo dõi tiến độ. Lịch sử thao tác và trạng thái yêu cầu cung cấp cơ sở để kiểm tra lại thông tin đã ghi nhận. Việc áp dụng tại cơ sở chăm sóc cần thêm người phụ trách vận hành, điều kiện mạng và kế hoạch đánh giá phù hợp.')
heading('4.3. Kiến nghị trước khi sử dụng thử',2);block(148,149)
heading('4.4. Hướng phát triển',2);block(151,158)
heading('Tài liệu tham khảo và hồ sơ đối chiếu').paragraph_format.page_break_before=True
para('Các tài liệu dưới đây là mã nguồn và hồ sơ kiểm tra nội bộ của dự án. Chúng được dùng để đối chiếu việc triển khai, kiểm thử và đóng gói; không thay cho nghiên cứu y khoa về hiệu quả điều trị.')
refs=[
'[1] Hồ sơ chức năng đăng ký và liên kết chăm sóc: registration_dialog.py, patient_sync_service.py, test_caregiver_desktop_registration_flow.py và giao diện quản trị. Phiên bản dự án ngày 24/10/2026.',
'[2] Hồ sơ chức năng thuốc: today_todo_widget.py, medication_schedule_sync.py, elder_sync_client.py; kiểm thử hồi quy đơn thuốc, âm thanh và hủy đơn. Phiên bản dự án ngày 24/10/2026.',
'[3] Hồ sơ đồng bộ số đo: api_router.py, cổng người nhà, cổng bác sĩ; test_vitals_sync_regression.py và test_caregiver_clinician_health_sync.py. Phiên bản dự án ngày 24/10/2026.',
'[4] Hồ sơ phục hồi vận động: config.py, dashboard.py, rehab_engine.py; test_routine_and_games.py và test_caregiver_rehab_config_sync.py. Phiên bản dự án ngày 24/10/2026.',
'[5] Hồ sơ trò chơi và âm nhạc: family_music_service.py, music_playback.py, mô-đun cognitive_games và test_family_music.py. Phiên bản dự án ngày 24/10/2026.',
'[6] Hồ sơ tổng hợp biểu cảm: emotion_summary_service.py và test_emotion_summary.py. Phiên bản dự án ngày 24/10/2026.',
'[7] Hồ sơ giọng nói và yêu cầu hỗ trợ: local_voice_widget.py; các mô-đun local_voice, local_rules và bộ kiểm thử luật cục bộ. Phiên bản dự án ngày 24/10/2026.',
'[8] Hồ sơ đóng gói portable: QA_REPORT.txt của PT và HP; PORTABLE_PT_VALIDATION.json và PORTABLE_HP_VALIDATION.json; manifest SHA-256. Bản 6.0.0-zipformer.1 ngày 24/10/2026.',
'[9] Hồ sơ cập nhật Zipformer: STT_ZIPFORMER.md, zipformer-benchmark.json; engine.py, config.py, controller.py và kiểm thử STT. Model sherpa-onnx-zipformer-vi-30M-int8-2026-02-09; sherpa-onnx 1.12.40.']
for r in refs:para(r)
para('Hồ sơ kiểm thử chức năng gồm report-verification/results.xml với 35 ca và report-verification-additional/results.xml với 235 ca. Bảng tổng hợp chi tiết được lưu trong BANG_CHUNG_KIEM_THU_2026-10-24.json của hồ sơ báo cáo gốc. Các kết quả này không được quy đổi thành độ chính xác mô hình, hiệu quả chăm sóc hoặc mức hài lòng người dùng.')
doc.add_page_break()
para('BÁO CÁO TÓM TẮT KẾT QUẢ THỰC HIỆN\nDỰ ÁN DỰ THI IIIb','Title',True,True)
para('Tên dự án dự thi: Hệ thống trợ lý AI hỗ trợ chăm sóc và phục hồi chức năng cho người cao tuổi.',bold=True)
para('Lĩnh vực dự thi: ........................................................................')
heading('Tóm tắt kết quả',2)
summary=[
('Mục tiêu','Xây dựng nguyên mẫu kết nối người cao tuổi, người nhà và bác sĩ qua hồ sơ chăm sóc chung, hỗ trợ nhắc thuốc, theo dõi tập luyện và gửi yêu cầu hỗ trợ.'),
('Phương pháp nghiên cứu','Sử dụng Python, PyQt5, SQLite, cổng web phân quyền và các mô hình AI cục bộ. Giọng nói được chuyển thành văn bản bằng Zipformer tiếng Việt, sau đó xử lý bằng bộ luật có kiểm tra ngữ cảnh.'),
('Quá trình thực hiện','Xây dựng các luồng đăng ký, đơn thuốc, số đo, ba bài tập trước camera, trò chơi trí nhớ, âm nhạc và trao đổi chăm sóc; kiểm tra đồng bộ, phân quyền, thao tác lặp và đóng gói portable.'),
('Kết quả chính','Hai đợt kiểm thử chức năng ghi nhận 252/270 ca đạt, 6 ca không đạt và 12 lỗi thiết lập. Đợt kiểm tra STT riêng có 50 ca đạt. Hai gói PT và HP đã qua kiểm tra runtime nhúng, khởi động và toàn vẹn trên máy build.'),
('Ý nghĩa và kết luận','Nguyên mẫu tổ chức công việc chăm sóc theo cùng hồ sơ và cho phép kiểm tra lại trạng thái đã ghi nhận. Chưa có đánh giá hiệu quả lâm sàng hoặc độ chính xác mô hình trên nhóm người cao tuổi; cần thử trên thiết bị thực và hoàn thiện các ca kiểm thử còn lại.')]
for label,text in summary:
 p=doc.add_paragraph();p.add_run(label+': ').bold=True;p.add_run(text);fmt(p)
 p.runs[0].bold=True
summary_words=len(' '.join(k+' '+v for k,v in summary).split())
# Page numbers only, no identifying headers.
p=sec.footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run();field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');r._r.addnext(field);fmt(p,align=WD_ALIGN_PARAGRAPH.CENTER)
doc.core_properties.author='';doc.core_properties.last_modified_by='';doc.core_properties.title='Báo cáo kết quả thực hiện dự án AI Care theo Phụ lục III'
doc.save(OUT)
# Remove any template hyperlink relationships and ensure no outside links were inherited.
with ZipFile(OUT) as z:entries={i.filename:z.read(i.filename) for i in z.infolist()}
from lxml import etree
for name,data in list(entries.items()):
 if name.endswith('.rels'):
  tree=etree.fromstring(data)
  for el in list(tree):
   if el.get('TargetMode')=='External':tree.remove(el)
  entries[name]=etree.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
 for name,data in entries.items():z.writestr(name,data)
(ROOT/'authoring_audit.json').write_text(json.dumps({'output':str(OUT),'summary_words':summary_words,'reference_sha256':hashlib.sha256(REF.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT);print('Summary words',summary_words);print('Paragraphs',len(doc.paragraphs))
