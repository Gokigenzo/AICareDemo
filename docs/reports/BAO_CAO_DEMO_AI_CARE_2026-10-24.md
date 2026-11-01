# BÁO CÁO ĐỀ TÀI
# HỆ THỐNG TRỢ LÝ AI HỖ TRỢ CHĂM SÓC VÀ PHỤC HỒI CHỨC NĂNG CHO NGƯỜI CAO TUỔI

**Tên sản phẩm:** AI Care & Rehabilitation Assistant  
**Phạm vi:** Bản demo hiện có và kết quả kiểm tra phần mềm đến ngày 24/10/2026.

## PHẦN I. MỞ ĐẦU

### 1. Lý do thực hiện đề tài

Trong việc chăm sóc người cao tuổi tại gia đình, nhiều công việc diễn ra hằng ngày nhưng do những người khác nhau phụ trách. Bác sĩ đưa ra chỉ định; người nhà nhắc uống thuốc, ghi lại số đo và theo dõi việc tập; người cao tuổi trực tiếp thực hiện. Nếu thông tin chỉ được trao đổi qua lời nhắc hoặc ghi chép riêng, người chăm sóc khó biết chỉ định nào còn hiệu lực, lần uống nào đã được xác nhận và buổi tập nào đã hoàn thành.

Đề tài xây dựng một bản demo kết nối các công việc này trên cùng hồ sơ chăm sóc. Người cao tuổi sử dụng ứng dụng trên máy tính, còn người nhà và bác sĩ sử dụng cổng web theo vai trò. Hoạt động trên ứng dụng được lưu để các bên theo dõi; đơn thuốc, lời khuyên và kế hoạch chăm sóc từ cổng web được chuyển đến giao diện người cao tuổi.

Trọng tâm của sản phẩm là tổ chức việc chăm sóc thành những thao tác có thể thực hiện và kiểm tra lại. AI được sử dụng ở các khâu nhận diện khuôn mặt, quan sát biểu cảm, hỗ trợ đếm động tác và chuyển lời nói thành văn bản. Quyết định về thuốc và chỉ định chuyên môn vẫn do người phụ trách thực hiện.

### 2. Mục tiêu nghiên cứu

Mục tiêu chính là xây dựng luồng phối hợp giữa người cao tuổi, người nhà và bác sĩ trong một bản demo thống nhất. Những yêu cầu cụ thể gồm: hiển thị công việc trong ngày; đồng bộ đơn thuốc và trạng thái từng lần uống; lưu chỉ số sức khỏe có thời điểm ghi nhận; hướng dẫn và theo dõi ba bài tập trước camera; cung cấp trò chơi trí nhớ, âm nhạc thư giãn và kênh gửi yêu cầu hỗ trợ.

Đề tài cũng đặt yêu cầu quản lý quyền truy cập theo người được chăm sóc. Người nhà và bác sĩ cần được liên kết với đúng hồ sơ để xem thông tin hoặc thực hiện thao tác trong phạm vi được giao. Bản đóng gói dành cho Windows phải chứa các thành phần cần thiết để có thể chuyển sang máy khác và khởi chạy theo hướng dẫn.

### 3. Đối tượng và phạm vi

Đối tượng sử dụng dự kiến gồm người cao tuổi có người hỗ trợ thiết lập ban đầu, người thân tham gia chăm sóc, bác sĩ phụ trách và quản trị viên. Báo cáo tập trung vào chức năng đã triển khai, luồng sử dụng và bằng chứng kiểm thử của bản demo. Các số đo và hồ sơ dùng trong kiểm thử là dữ liệu thử, không phải kết quả khảo sát người bệnh.

Phạm vi đánh giá hiện tại là phần mềm trên máy Windows dùng để phát triển và đóng gói. Chưa có dữ liệu nghiên cứu theo dõi người cao tuổi dài ngày, đánh giá hiệu quả phục hồi hay đo mức cải thiện tuân thủ dùng thuốc. Vì vậy, kết quả được trình bày ở mức nguyên mẫu hỗ trợ chăm sóc, chưa phải kết quả nghiệm thu lâm sàng.

## PHẦN II. NỘI DUNG VÀ PHƯƠNG PHÁP NGHIÊN CỨU

### 1. Phương án thiết kế và nền tảng vận hành

#### 1.1. Tổ chức theo vai trò sử dụng

Hệ thống gồm ứng dụng dành cho người cao tuổi và ba cổng web dành cho người nhà, bác sĩ, quản trị viên. Các giao diện cùng sử dụng dữ liệu chăm sóc thống nhất. Cách tổ chức này cho phép mỗi người tiếp cận công việc của mình: người cao tuổi xem việc cần làm, người nhà theo dõi và hỗ trợ, bác sĩ cập nhật chỉ định, quản trị viên quản lý tài khoản và phân công.

Ứng dụng người cao tuổi có trang “Việc cần làm hôm nay”, khu vực nhận diện và phục hồi chức năng, khu vực trò chơi trí nhớ và thư giãn. Cổng người nhà chia nội dung thành chỉ số sức khỏe, thuốc, thông tin biểu cảm, âm nhạc, phục hồi chức năng và trao đổi với bác sĩ. Cổng bác sĩ tập trung vào hồ sơ được phân công, số đo, đơn thuốc, lời khuyên và phản hồi.

#### 1.2. Nền tảng kỹ thuật phục vụ sử dụng

Phần mềm sử dụng Python cho xử lý nghiệp vụ, PyQt5 cho ứng dụng máy tính và SQLite để lưu dữ liệu. Các cổng web trao đổi với máy chủ của hệ thống. Khi dữ liệu thay đổi, cơ chế phát sự kiện và làm mới giao diện giúp các vai trò cập nhật thông tin; ứng dụng cũng có nút đồng bộ chủ động.

Các mô hình thị giác và nhận dạng giọng nói được bố trí để chạy cục bộ trong gói portable. Những chức năng cần dịch vụ bên ngoài, chẳng hạn gửi email, vẫn phụ thuộc kết nối và cấu hình. Máy chủ mặc định phục vụ trên máy đang chạy chương trình. Việc truy cập từ thiết bị khác cần thiết lập mạng phù hợp; bản demo hiện tại chưa chứng minh khả năng cung cấp dịch vụ từ xa trên Internet.

#### 1.3. Phương pháp thực hiện và kiểm tra

Việc xây dựng demo được triển khai theo từng luồng công việc, từ thao tác ở một giao diện đến dữ liệu mà vai trò khác nhận được. Các tình huống kiểm tra gồm đăng ký hồ sơ, kê và hủy đơn thuốc, nhập số đo, thay đổi chỉ tiêu tập, tải nhạc và gửi yêu cầu hỗ trợ. Các kiểm thử còn xem xét trường hợp nhập sai, thao tác lặp, khác quyền truy cập hoặc thay đổi hồ sơ trong lúc xử lý.

Khi tổng hợp báo cáo, mã nguồn hiện tại được đối chiếu với kiểm thử tự động và hồ sơ kiểm tra hai gói portable. Những tài liệu lịch sử có nội dung không còn phù hợp không được dùng làm bằng chứng cho chức năng hiện hành. Các thông số thử nghiệm được tách khỏi kết luận về hiệu quả sử dụng thực tế.

### 2. Chức năng tài khoản và hồ sơ chăm sóc

#### 2.1. Đăng ký người cao tuổi và người nhà

Ứng dụng có chức năng đăng ký hồ sơ mới, gồm mã hồ sơ, họ tên, tuổi, giới tính và thông tin tiền sử hoặc bệnh lý. Người thực hiện đăng ký đồng thời nhập thông tin người nhà như họ tên, mối quan hệ, email, số điện thoại và mật khẩu đăng nhập web. Ảnh khuôn mặt được thu nhận để phục vụ nhận diện người đã đăng ký.

Luồng này gắn người được chăm sóc với người hỗ trợ ngay từ khâu tạo hồ sơ. Sau đăng ký, người nhà đăng nhập cổng web bằng tài khoản đã thiết lập và truy cập hồ sơ được liên kết. Bộ kiểm thử đăng ký hiện có đã kiểm tra việc lưu liên kết, đăng nhập web và giới hạn truy cập theo người được chăm sóc. [1]

#### 2.2. Quản lý tài khoản và phân công

Quản trị viên có giao diện quản lý bác sĩ, người nhà và người cao tuổi. Các thao tác gồm tạo tài khoản bác sĩ, cập nhật trạng thái hoạt động, khóa hoặc mở tài khoản, phân công người bệnh cho bác sĩ và liên kết người nhà với hồ sơ chăm sóc.

Việc phân công là cơ sở để hệ thống xác định phạm vi dữ liệu của người đăng nhập. Trong vận hành, cần kiểm tra đúng quan hệ này trước khi gửi thông tin hoặc cập nhật chỉ định. Khả năng nhận diện khuôn mặt trên ứng dụng giúp lựa chọn hồ sơ sử dụng; quyền xem và sửa dữ liệu trên web được kiểm tra theo tài khoản cùng quan hệ chăm sóc.

### 3. Chức năng đơn thuốc, nhắc uống và ghi nhận chỉ số sức khỏe

#### 3.1. Từ đơn thuốc đến lịch uống trong ngày

Bác sĩ chọn người bệnh được phân công và lập đơn thuốc với thời gian hiệu lực, thuốc, liều dùng, giờ dùng và chỉ dẫn. Đơn được lưu theo phiên bản để phân biệt nội dung đang áp dụng với nội dung đã thay thế hoặc hủy. Người nhà xem đơn trên cổng web; người cao tuổi xem thông tin đơn và lịch uống trên ứng dụng.

Ở bản demo hiện tại, thông tin đơn thuốc và các lần uống trong ngày được trình bày thành hai khu vực riêng. Người dùng vẫn xem được nội dung chỉ định ngay cả khi chưa có lần uống hợp lệ của ngày đang chọn. Sự phân biệt này giúp tránh hiểu nhầm rằng không có lịch hôm nay đồng nghĩa với không nhận được đơn.

Trong quá trình hoàn thiện đã phát hiện một đơn thử có ngày kết thúc trước ngày bắt đầu. Phần mềm hiện kiểm tra thứ tự ngày và định dạng giờ trước khi lưu đơn mới. Với đơn cũ có thời gian không hợp lệ, ứng dụng hiển thị yêu cầu bác sĩ sửa đơn, không tự thay đổi thời gian điều trị. Cơ chế bổ sung lịch còn thiếu được kiểm tra theo đơn đang hoạt động và giới hạn khoảng thời gian tạo lịch. [2]

#### 3.2. Xác nhận và theo dõi từng lần uống

Trên trang việc cần làm, người cao tuổi có thể xác nhận đã uống, nhắc lại sau hoặc yêu cầu hỗ trợ đối với lần uống được hiển thị. Người nhà và bác sĩ theo dõi trạng thái để biết lần nào đã được ghi nhận và lần nào cần kiểm tra thêm. Khi đơn bị hủy, các lần uống không còn hiệu lực được loại khỏi lịch đang sử dụng, trong khi lịch sử nghiệp vụ được giữ lại. [2]

Trạng thái “đã uống” phản ánh thao tác tự khai hoặc ghi nhận hỗ trợ. Camera và phần mềm không xác minh thuốc đã được uống vào cơ thể. Vì vậy, dữ liệu phù hợp để tổ chức nhắc việc và trao đổi với người chăm sóc; khi cần xác nhận thực tế vẫn phải hỏi hoặc kiểm tra trực tiếp.

#### 3.3. Nhập và xem chỉ số sức khỏe

Cổng web có biểu mẫu nhập huyết áp, nhịp tim, SpO2, đường huyết và thân nhiệt. Dữ liệu gắn với người được đo và thời điểm đo, sau đó được đưa vào lịch sử, phần tổng quan và biểu đồ tương ứng. Người nhà có thể nhập hộ; yêu cầu nhắc đo được hiển thị trên ứng dụng người cao tuổi.

Trong luồng đã kiểm tra, một nhóm số đo nhập mới được đọc lại ở giao diện dữ liệu của người nhà, bác sĩ và bản tổng hợp dành cho ứng dụng. Phần mềm lưu và hiển thị các giá trị đã nhập; bản demo chưa tích hợp thiết bị tự động đo những chỉ số này. Không có căn cứ để diễn giải hình ảnh camera thành số đo huyết áp hoặc đường huyết. [3]

### 4. Chức năng phục hồi vận động và theo dõi tiến độ

Demo có ba bài tập: nâng tay qua đầu, đứng lên ngồi xuống và đi bộ tại chỗ. Cấu hình mặc định lần lượt là 10 lần, 10 lần và 15 bước, với chuỗi nhắc tập lúc 16 giờ. Giao diện cung cấp lựa chọn từng bài hoặc thực hiện chuỗi bài tập; kế hoạch có thể điều chỉnh giờ nhắc và chỉ tiêu.

Khi bắt đầu, người tập đứng trong vùng camera quan sát được và thực hiện theo hướng dẫn trên màn hình. Phần mềm sử dụng điểm mốc cơ thể để theo dõi chu kỳ động tác, cập nhật số lần và tiến độ. Chuỗi bài tập chuyển sang bước tiếp theo khi đạt chỉ tiêu tương ứng. Kết quả buổi tập được lưu để người nhà và bác sĩ theo dõi.

Người dùng có thể tạm dừng, dừng hoặc đặt lại bài tập. Nếu đã vận động nhưng camera chưa ghi nhận, ứng dụng có nút báo sự cố. Cách ghi nhận này giữ được sự khác biệt giữa kết quả do camera đếm và phản ánh của người dùng, thay vì tự cộng số lần khi không có dữ liệu quan sát.

Sáu ca kiểm thử chuỗi bài tập và khu vực trò chơi đã chạy đạt trong đợt rà soát. Kết quả đó xác nhận logic tiến trình và tích hợp giao diện trong điều kiện thử, chưa xác định độ chính xác đếm động tác trên nhóm người cao tuổi thực tế. Ánh sáng, góc camera, che khuất và khả năng vận động là những điều kiện cần đánh giá thêm khi triển khai. [4]

### 5. Chức năng trò chơi trí nhớ, âm nhạc và quan sát biểu cảm

#### 5.1. Trò chơi trí nhớ

Ứng dụng có hai loại trò chơi: lật hình ghép cặp và nhớ trình tự. Người chơi chọn độ khó, quan sát hình và thực hiện lựa chọn trên màn hình. Trò lật hình có các mức 3, 4, 6 hoặc 8 cặp; trò nhớ trình tự thay đổi độ dài dãy theo mức đã chọn. Giao diện có đường quay lại khu vực chính để người dùng chuyển hoạt động.

Các trò chơi cung cấp hoạt động tương tác có luật rõ và ghi nhận phiên chơi. Kết quả chơi có thể được xem trong ngữ cảnh hoạt động của người sử dụng. Chưa có đánh giá cho phép dùng điểm trò chơi để chẩn đoán suy giảm nhận thức hoặc kết luận hoạt động này cải thiện trí nhớ sau một thời gian sử dụng.

#### 5.2. Nhạc do người nhà gửi

Người nhà tải tệp MP3 hoặc WAV cho đúng hồ sơ người cao tuổi trên cổng web. Hệ thống kiểm tra tệp, lưu thông tin bài hát và bổ sung vào danh mục mà ứng dụng đọc được. Người cao tuổi chọn bài để phát, tạm dừng, dừng hoặc điều chỉnh âm lượng. Thư viện cũng có âm thanh thư giãn đi kèm.

Bài mới được bổ sung vào danh sách mà không tự phát hoặc ngắt bài đang nghe. Đây là điểm quan trọng trong tình huống người nhà gửi bài khi người cao tuổi đang sử dụng ứng dụng. Lỗi có bài hát nhưng không phát ra âm thanh đã được xử lý bằng luồng giải mã âm thanh thống nhất. Kiểm thử xác nhận tệp WAV và MP3 được giải mã thành mẫu âm thanh có biên độ khác không; việc nghe qua loa thực vẫn cần kiểm tra trên thiết bị sử dụng. [5]

Âm nhạc tạo thêm cách người nhà lựa chọn nội dung giải trí cho người thân. Báo cáo không gán cho các bản nhạc tác dụng điều trị hoặc hiệu quả cải thiện sức khỏe chưa được đo.

#### 5.3. Thông tin biểu cảm qua camera

Demo phân loại biểu cảm khuôn mặt thành ba nhóm: vui, bình thường và buồn. Thông tin quan sát được tổng hợp theo cửa sổ hai giờ và hiển thị trên cổng theo dõi. Trong khoảng không có quan sát hợp lệ, phần mềm không được coi thời gian đó là bằng chứng người sử dụng đang có một biểu cảm cụ thể.

Kết quả này là tín hiệu tham khảo để người nhà quan tâm và hỏi thăm thêm. Biểu cảm trước camera không đồng nhất với trạng thái tâm lý, và ba nhãn phân loại không phải chẩn đoán sức khỏe tinh thần. Hồ sơ kiểm thử tổng hợp biểu cảm xác nhận xử lý thời gian quan sát trong tình huống thử, chưa cung cấp độ chính xác phân loại trên người sử dụng thực tế. [6]

### 6. Chức năng giọng nói, yêu cầu hỗ trợ và trao đổi chăm sóc

#### 6.1. Thao tác bằng giọng nói tiếng Việt

Người cao tuổi nhấn nút nhận giọng nói, nói yêu cầu rồi dừng để phần mềm xử lý. Văn bản nhận dạng được hiển thị để người dùng biết hệ thống đã nghe được gì. Bộ luật cục bộ phân loại các câu thuộc phạm vi chức năng đã định nghĩa.

Mã nguồn đang làm việc đã cập nhật bộ nhận dạng sang Zipformer tiếng Việt chạy trên CPU. Hai gói portable đã phát hành trước cập nhật này dùng thành phần nhận dạng cục bộ của phiên bản trước; cần đóng gói lại để đưa cập nhật vào ZIP. Hai mốc được phân biệt khi trình bày kết quả kiểm tra. [9]

Các nhóm thao tác được triển khai gồm hỗ trợ thao tác thuốc, điều khiển bài tập, quay về trang chính và yêu cầu liên hệ bác sĩ hoặc người nhà. Với xác nhận uống thuốc, phần mềm kiểm tra hồ sơ và lần uống liên quan, yêu cầu xác nhận trước khi ghi nhận. Khi có nhiều lần uống hoặc ngữ cảnh không rõ, người dùng được hướng về thao tác lựa chọn trên màn hình. Việc đổi hồ sơ trong lúc xử lý làm ngữ cảnh cũ không còn đủ điều kiện thực hiện lệnh.

Những kiểm tra này nhằm hạn chế một câu được nhận dạng thành thao tác trên nhầm hồ sơ hoặc nhầm lần uống. Chức năng hiện tại xử lý nhóm yêu cầu chăm sóc đã quy định; không có kết quả chứng minh khả năng hiểu mọi cách nói tiếng Việt hoặc tư vấn y khoa tự do. [7]

#### 6.2. Tạo và theo dõi yêu cầu hỗ trợ

Yêu cầu hỗ trợ được gắn với hồ sơ người cao tuổi và vai trò người nhận. Phần mềm có trạng thái theo dõi yêu cầu, tiếp nhận, giải quyết và hủy hoặc đính chính. Giao diện còn cung cấp thao tác báo nhầm, gửi lại, thử lại và xem liên hệ thủ công khi cần.

Trạng thái gửi thông báo và trạng thái xử lý yêu cầu được phân biệt. Máy chủ email chấp nhận thư không có nghĩa bác sĩ hoặc người nhà đã đọc. Nếu email chưa cấu hình hoặc kết nối gặp lỗi, phần mềm cần hiển thị tình trạng tương ứng để người dùng chuyển sang liên hệ trực tiếp. Bản demo chưa được đánh giá như dịch vụ ứng cứu liên tục và không cung cấp bảo đảm về thời gian có người phản hồi.

#### 6.3. Trao đổi giữa người nhà và bác sĩ

Người nhà gửi mô tả diễn biến hoặc dấu hiệu cần trao đổi từ cổng web. Bác sĩ xem nội dung trên hồ sơ được phân công và gửi phản hồi. Bác sĩ cũng có thể soạn lời khuyên theo nhóm nội dung như dinh dưỡng, vận động và tinh thần; người cao tuổi xem và xác nhận đã đọc trên ứng dụng.

Luồng này đặt lời khuyên và phản hồi trong đúng hồ sơ, giúp các bên tìm lại nội dung chăm sóc. Việc xem thông tin tổng hợp hỗ trợ trao đổi, còn đánh giá triệu chứng và quyết định chuyên môn vẫn thuộc người phụ trách.

### 7. Quy trình vận hành dành cho người cao tuổi

Quy trình bắt đầu sau khi hồ sơ và các quan hệ chăm sóc đã được thiết lập. Người hỗ trợ đặt máy, camera, micro và thiết bị âm thanh, sau đó mở ứng dụng. Người sử dụng kiểm tra tên hồ sơ đang hiển thị trước khi ghi nhận hoạt động.

1. **Xem việc cần làm:** đọc đơn thuốc, các lần uống trong ngày, yêu cầu đo, lịch tập và lời khuyên.
2. **Thực hiện việc liên quan đến thuốc:** chọn đúng lần uống rồi xác nhận, nhắc lại sau hoặc yêu cầu hỗ trợ. Các thao tác này được lưu theo lần uống cụ thể.
3. **Đáp ứng yêu cầu đo:** thực hiện đo bằng thiết bị phù hợp; số đo được người có thao tác nhập liệu ghi vào hệ thống.
4. **Tập trước camera:** chọn bài hoặc chuỗi bài, làm theo hướng dẫn, theo dõi bộ đếm; tạm dừng hoặc báo sự cố khi cần.
5. **Giải trí và tương tác:** mở trò chơi hoặc chọn bài nhạc trong danh mục, gồm nhạc do người nhà gửi.
6. **Gửi nhu cầu hỗ trợ:** dùng nút bấm hoặc giọng nói, kiểm tra nội dung nhận dạng và theo dõi trạng thái phản hồi.

Ứng dụng cần được mở để thực hiện nhắc việc theo giờ và quan sát từ camera. Trước khi kết thúc, người sử dụng có thể xem lại trạng thái đồng bộ. Với gói portable, đóng cửa sổ khởi chạy để dừng các thành phần theo quy trình đã thiết kế.

### 8. Quy trình vận hành dành cho người nhà, bác sĩ và quản trị viên

#### 8.1. Người nhà

Người nhà đăng nhập, chọn hồ sơ được liên kết và kiểm tra số đo gần nhất, trạng thái thuốc, tiến độ tập. Khi có kết quả đo mới, người nhà nhập kèm thời điểm; khi cần đo thêm, gửi yêu cầu để ứng dụng hiển thị. Người nhà cũng có thể tải nhạc và gửi mô tả diễn biến cho bác sĩ.

Khi thấy lịch thuốc trống, người nhà cần đối chiếu ngày đang xem, hiệu lực đơn và trạng thái đồng bộ. Khi lần uống chưa được xác nhận, cần trao đổi với người cao tuổi để làm rõ. Một trạng thái chưa ghi nhận trong phần mềm chưa đủ để kết luận hành vi ngoài thực tế.

#### 8.2. Bác sĩ

Bác sĩ truy cập danh sách người bệnh được phân công, chọn hồ sơ và xem số đo, lịch sử thuốc, kết quả tập cùng phản ánh từ người nhà. Nếu cần thay đổi điều trị, bác sĩ cập nhật đơn theo phiên bản hoặc hủy đơn đang dùng. Các lời khuyên được gửi qua chức năng riêng để người nhà và người cao tuổi xem lại.

Khi nhận yêu cầu hỗ trợ, bác sĩ tiếp nhận và cập nhật tình trạng xử lý. Trong luồng demo, dấu vết thao tác giúp phân biệt yêu cầu mới với yêu cầu đã được tiếp nhận. Việc đánh giá tình trạng sức khỏe cần được thực hiện theo trách nhiệm chuyên môn và điều kiện trao đổi thực tế.

#### 8.3. Quản trị viên

Quản trị viên thiết lập tài khoản, kiểm tra thông tin liên hệ, phân công người bệnh cho bác sĩ và liên kết người nhà. Trước buổi trình diễn, cần xác nhận tài khoản hoạt động, quan hệ chăm sóc đúng, camera và âm thanh sẵn sàng, dữ liệu thử được nhận biết rõ.

Khi thay đổi người phụ trách, quản trị viên điều chỉnh quyền liên kết để dữ liệu được truy cập theo phân công hiện tại. Khi chuyển máy hoặc sao lưu, cần giữ riêng dữ liệu đang sử dụng với mã chương trình và gói phát hành.

### 9. Ứng dụng thực tiễn và điều kiện triển khai

#### 9.1. Những tình huống sử dụng có thể tổ chức với demo

Tại gia đình, sản phẩm có thể được dùng để trình diễn một lịch chăm sóc trong ngày: bác sĩ tạo chỉ định, người cao tuổi thực hiện trên ứng dụng, người nhà nhập số đo và theo dõi. Giá trị của cách tổ chức này nằm ở việc các bên cùng xem một hồ sơ và biết thông tin nào đã được ghi nhận.

Đối với hoạt động tập luyện, camera và bộ đếm tạo phản hồi ngay trên màn hình; lịch sử giúp người chăm sóc xem lại mức hoàn thành đã ghi nhận. Trò chơi và nhạc mở thêm hoạt động sử dụng ngoài thời điểm uống thuốc hoặc tập. Đây là các khả năng ứng dụng xuất phát từ chức năng hiện có, chưa phải kết quả chứng minh hiệu quả tại hộ gia đình hoặc cơ sở chăm sóc.

Demo cũng có thể phục vụ thử nghiệm quy trình tại cơ sở chăm sóc sau khi có người phụ trách, điều kiện mạng và kế hoạch đánh giá. Trước khi mở rộng nhiều người dùng đồng thời, cần đo tải, kiểm tra phân quyền và xác nhận cách hỗ trợ khi thiết bị ngừng hoạt động.

#### 9.2. Điều kiện vận hành

Bản portable được đóng gói cho Windows 10/11 64 bit, kèm Python, thư viện và model cục bộ. Máy cần camera để nhận diện và theo dõi động tác, micro cho thao tác bằng lời nói, loa hoặc tai nghe để phát âm thanh. Cần bố trí camera thấy được vùng cơ thể liên quan đến bài tập và có người hỗ trợ thao tác ban đầu khi người sử dụng chưa quen.

Máy cần đủ chỗ lưu bản giải nén, dữ liệu và tệp nhạc. Hai gói đầy đủ hiện có dung lượng nén khoảng 957 MiB mỗi bản; đây là dung lượng tệp phát hành, không phải mức RAM hay dung lượng tối thiểu khi chạy. Nếu máy thiếu thành phần hệ thống, sử dụng bộ cài thư viện đi kèm theo hướng dẫn. Chưa có phép đo để đưa ra cấu hình CPU hoặc RAM tối thiểu đã được xác nhận.

Mô hình cục bộ cho phép xử lý những chức năng tương ứng mà không phải gửi tín hiệu lên dịch vụ AI bên ngoài. Cổng web trên thiết bị khác vẫn cần kết nối đến máy chủ; email cần dịch vụ thư được cấu hình. Do đó, điều kiện mất Internet và điều kiện mất kết nối đến máy chủ phải được kiểm tra riêng.

## PHẦN III. THỬ NGHIỆM VÀ KẾT QUẢ ĐẠT ĐƯỢC

### 1. Sản phẩm và điều chỉnh đã hoàn thành

Sản phẩm hiện có ứng dụng người cao tuổi, cổng người nhà, cổng bác sĩ và cổng quản trị dùng chung dữ liệu nghiệp vụ. Các chức năng thuốc, số đo, kế hoạch tập, lời khuyên, âm nhạc và yêu cầu hỗ trợ đã có phần triển khai để thực hiện luồng chăm sóc mô tả ở Phần II.

Những điều chỉnh trực tiếp trong đợt hoàn thiện gồm tách hiển thị đơn thuốc khỏi lịch uống hôm nay; từ chối đơn có thời gian không hợp lệ; bổ sung cơ chế tạo lịch còn thiếu; sửa đường phát âm thanh; và cập nhật phong cách giao diện web cùng ứng dụng. Hai gói PT và HP giữ hai phiên bản giao diện tương ứng, đồng thời chứa các thành phần để khởi động bằng tệp thực thi.

### 2. Điều kiện và kết quả kiểm thử chức năng

Ngày 24/10/2026, hai đợt kiểm thử bổ sung được chạy trên Windows với cơ sở dữ liệu thử. Các kiểm tra giao diện dùng chế độ không hiển thị cửa sổ, camera bị vô hiệu hóa trong cấu hình thử. Một số dịch vụ ngoài hoặc đầu ra phần cứng được thay bằng thành phần kiểm thử. Đơn vị đếm trong các bảng dưới đây là ca kiểm thử phần mềm, không phải người tham gia hay lần sử dụng thực tế.

**Bảng 1. Kết quả hai đợt kiểm thử được thực hiện khi lập báo cáo**

| Đợt kiểm thử | Tổng số ca | Đạt | Không đạt ở bước kiểm tra | Lỗi ở bước thiết lập |
|---|---:|---:|---:|---:|
| Thuốc, âm thanh, hồ sơ đăng ký, sức khỏe và cấu hình tập | 35 | 32 | 3 | 0 |
| Bộ luật giọng nói, yêu cầu hỗ trợ, chuỗi bài tập, trò chơi và số đo | 235 | 220 | 3 | 12 |
| **Tổng trong hai đợt** | **270** | **252** | **6** | **12** |

Các nhóm đạt gồm 7 ca hồi quy đơn thuốc và giải mã âm thanh, 15 ca về nhạc người nhà, 2 ca đăng ký hồ sơ, 1 ca hủy đơn, 13 ca hồi quy nhập và đồng bộ số đo, 6 ca về chuỗi bài tập và trò chơi. Bộ luật xử lý văn bản đầu vào có 153 ca đạt; 7 ca xử lý thuốc trong luồng luật cục bộ cũng đạt. Các số lượng này thuộc những nhóm con khác nhau của Bảng 1, không phải các thử nghiệm bổ sung ngoài tổng đã nêu. [1]–[7]

Kết quả về âm thanh xác nhận dữ liệu được giải mã và đưa tới đầu ra thử. Kết quả về bộ luật giọng nói xác nhận xử lý văn bản thử theo quy tắc; chúng không đo độ chính xác nghe lời nói thực qua micro. Tương tự, kiểm thử tiến trình tập không thay cho đối chiếu bộ đếm với người quan sát trên video hoặc buổi tập thực.

### 3. Các trường hợp chưa đạt và giới hạn diễn giải

Hai ca theo dõi sức khỏe không đạt vì yêu cầu phải có dữ liệu huyết áp mẫu sẵn trong cơ sở dữ liệu thử, trong khi truy vấn trả về rỗng. Ở cùng nhóm, ca nhập số đo mới và đồng bộ đạt. Nhóm hồi quy sử dụng dữ liệu nhập mới cũng đạt 13 ca. Vì vậy, kết quả cần được diễn giải theo dữ liệu đầu vào, không xem truy vấn rỗng của bộ mẫu là bằng chứng mọi luồng đồng bộ đều hỏng.

Một ca kiểm tra cấu hình tập không đạt ở phép so khớp chữ in hoa trên nhãn nút. Trước điểm dừng đó, các kiểm tra chỉ tiêu 12 lần nâng tay, 18 bước đi bộ và giờ nhắc 15 giờ 45 đã đi qua. Đây là sự không tương ứng giữa kỳ vọng nhãn cũ và giao diện hiện tại; vẫn phải ghi nhận ca kiểm thử chưa đạt.

Ở nhóm luật giọng nói, ba ca không đạt liên quan đến liên kết hồ sơ và người nhận; hai ca gặp ràng buộc duy nhất trong dữ liệu, một ca không trả về lỗi như kiểm thử kỳ vọng. Mười hai ca còn lại không chạy được phần kiểm tra chính vì bước thiết lập chèn mã người bệnh đã tồn tại. Các trường hợp này cho thấy cần rà soát lại dữ liệu khởi tạo và kỳ vọng của bộ kiểm thử, đồng thời xác minh lại hành vi chọn người nhận. Chưa đủ căn cứ để công bố toàn bộ luồng thông báo giọng nói đã được nghiệm thu.

Chưa có đánh giá trên nhóm người cao tuổi về độ dễ sử dụng, tỷ lệ nhận diện khuôn mặt, độ chính xác phân loại biểu cảm, nhận dạng lời nói hoặc đếm động tác. Chưa đo tác động đối với tuân thủ dùng thuốc, sức khỏe tinh thần và kết quả phục hồi.

### 4. Ghi nhận xử lý một tệp lời nói tiếng Việt

Hồ sơ đo Zipformer hiện có ghi nhận xử lý một tệp âm thanh dài 3,74 giây trên CPU. Ba lượt suy luận lần lượt mất 171 ms, 62 ms và 52 ms; thời gian nạp model ban đầu là 1.958 ms. Đây là số đo lưu trong hồ sơ thử của môi trường phát triển, không phải thời gian từ lúc nhấn micro đến khi hoàn thành một yêu cầu chăm sóc. [9]

Ba lượt dùng cùng một tệp nên chưa đại diện cho các giọng nói hoặc môi trường khác nhau. Hồ sơ chưa có đánh giá tỷ lệ lỗi nhận dạng theo từ hoặc ký tự và chưa có so sánh đối chứng giữa hai bộ nhận dạng. Số liệu này chỉ xác nhận đã có lần nạp và suy luận model thật trên tệp thử, không dùng để kết luận độ chính xác hay mức cải thiện tốc độ cho người dùng.

### 5. Kiểm tra đóng gói và khả năng khởi chạy

Hai gói portable đã được kiểm tra bằng Python đi kèm, kiểm tra khởi động qua EXE, dựng giao diện desktop, truy cập các trang web, đăng nhập quản trị và dừng máy chủ theo quy trình. Kiểm tra còn xác nhận việc từ chối lệnh dừng thiếu thông tin xác thực và phát hiện thay đổi dữ liệu kiểm tra model. Hai ZIP đều vượt kiểm tra CRC. [8]

**Bảng 2. Kết quả đóng gói hai phiên bản giao diện**

| Gói phát hành | Giao diện | Dung lượng ZIP | Phạm vi kiểm tra |
|---|---|---:|---|
| AI_FOR_EXAM_PT.zip | Giao diện mới | 1.003.492.303 byte | Kiểm tra khởi động, giao diện, web và toàn vẹn gói trên máy đóng gói |
| AI_FOR_EXAM_HP.zip | Giao diện cũ | 1.003.486.508 byte | Cùng quy trình kiểm tra như bản PT |

Hồ sơ kiểm tra của gói portable xác nhận các bước trên máy đóng gói; chưa có kiểm chứng trên máy Windows sạch thứ hai, thiết bị camera hoặc micro vật lý khác, hay phiên chạy kéo dài. Kết quả này thuộc hai ZIP đã tạo trước cập nhật Zipformer. Kết quả đóng gói cũng không thay thế những ca kiểm thử nghiệp vụ chưa đạt ở các mục trước.

## PHẦN IV. KẾT LUẬN VÀ KIẾN NGHỊ

### 1. Kết luận

Đề tài đã xây dựng được bản demo liên kết hoạt động của người cao tuổi với người nhà và bác sĩ qua hồ sơ chăm sóc chung. Từ giao diện người cao tuổi, người dùng có thể xem việc trong ngày, ghi nhận lần uống, tập trước camera, chơi trò chơi, nghe nhạc và gửi nhu cầu hỗ trợ. Các cổng web cung cấp nơi theo dõi, cập nhật chỉ định, nhập số đo và trao đổi theo phân công.

Kết quả kiểm tra hỗ trợ nhận định rằng nhiều luồng nghiệp vụ đã hoạt động trong môi trường thử, đặc biệt là đăng ký liên kết hồ sơ, xử lý đơn thuốc, nhập số đo và bổ sung nhạc. Hai gói portable cũng đã vượt qua kiểm tra khởi động và toàn vẹn trên máy đóng gói. Bộ kiểm thử vẫn còn các ca chưa đạt và lỗi thiết lập, chủ yếu ở dữ liệu mẫu, kỳ vọng giao diện và quan hệ người nhận trong luồng giọng nói.

Giá trị thực tiễn hiện thể hiện ở khả năng tổ chức công việc chăm sóc và trao đổi thông tin theo cùng một hồ sơ. Mức giảm công sức chăm sóc hoặc cải thiện sức khỏe chưa được đo; cần tiếp tục đánh giá trước khi đưa ra kết luận về các tác động này.

### 2. Kiến nghị

Trước một đợt sử dụng thử có người cao tuổi, cần xử lý các trường hợp kiểm thử còn lại, xác minh quyền truy cập và người nhận thông báo, thử gói trên máy sạch cùng thiết bị thực. Hồ sơ thử cần được phân biệt với hồ sơ sử dụng, và người tham gia cần được giải thích rõ cách ghi nhận uống thuốc, quan sát biểu cảm cũng như trạng thái yêu cầu hỗ trợ.

Nên bắt đầu bằng thử nghiệm quy mô nhỏ có người phụ trách theo dõi. Tiêu chí đánh giá cần bám vào thao tác cụ thể: người dùng có chọn đúng lần uống, đọc được lịch, hoàn thành việc gửi yêu cầu, nghe được nhạc và hiểu thông báo lỗi hay không. Kết quả này mới cung cấp cơ sở điều chỉnh giao diện và quy trình triển khai.

## PHẦN V. HƯỚNG PHÁT TRIỂN ĐỀ TÀI

### 1. Hoàn thiện độ tin cậy của các luồng đã có

Ưu tiên trước mắt là chuẩn hóa dữ liệu khởi tạo của kiểm thử, cập nhật các kỳ vọng giao diện và kiểm tra lại trường hợp nhiều quan hệ chăm sóc hoặc người nhận thay đổi. Các tình huống mất kết nối, khởi động lại, đổi hồ sơ giữa chừng và gửi lặp cần được thử có kiểm soát để làm rõ khả năng khôi phục.

### 2. Đánh giá trên người sử dụng và thiết bị thực

Đợt thử tiếp theo cần ghi nhận thời gian thao tác, nhu cầu được trợ giúp, lỗi lựa chọn và phản hồi của người cao tuổi. Với giọng nói, cần thu thập mẫu có sự đồng ý, bao gồm cách phát âm và mức tiếng ồn khác nhau. Với bài tập, cần có người quan sát hoặc video được gán nhãn để đối chiếu số lần đếm theo từng động tác và điều kiện camera.

### 3. Mở rộng nguồn số đo và theo dõi chuyên môn

Một hướng tiếp tục nghiên cứu là kết nối thiết bị đo để giảm nhập tay, đồng thời lưu nguồn và thời điểm của số đo. Phần tổng hợp tiến độ có thể được bổ sung theo nhu cầu theo dõi của người chăm sóc và bác sĩ. Đây là hướng phát triển, chưa phải chức năng đã kiểm chứng trong bản demo hiện tại.

### 4. Hoàn thiện triển khai và bảo trì

Cần kiểm tra trên nhiều cấu hình Windows, xây dựng hướng dẫn sao lưu và cập nhật mà vẫn giữ dữ liệu, đo tài nguyên sử dụng và xác định cấu hình phù hợp. Nếu mở cổng web ra ngoài máy chủ cục bộ, phải đánh giá thêm kết nối, xác thực, bảo vệ dữ liệu và phương án xử lý khi dịch vụ ngừng hoạt động. Việc mở rộng cần dựa trên kết quả thử tải và quy trình vận hành cụ thể.

## PHẦN VI. TÀI LIỆU THAM KHẢO VÀ PHỤ LỤC

### 1. Nguồn nội bộ dùng lập báo cáo

Báo cáo sử dụng mã nguồn và hồ sơ kiểm tra của chính demo. Mốc mã nguồn đã đưa lên repository là commit `1b7512e66e0e04ba9d7eca2ffae022a550cec9d9`, nhánh `main`, tại `https://github.com/Gokigenzo/AICareDemo`. Thư mục làm việc có cập nhật Zipformer sau mốc này; phần nhận dạng giọng nói trong báo cáo đã đối chiếu cả cập nhật cục bộ. Kết quả kiểm thử bổ sung ngày 24/10/2026 được lưu riêng trên máy; các tệp release và dữ liệu chạy không nằm trong repository.

| Mã nguồn dẫn | Tài liệu hoặc thành phần | Nội dung dùng làm căn cứ |
|---|---|---|
| [1] | `app/registration_dialog.py`; `services/patient_sync_service.py`; `tests/test_caregiver_desktop_registration_flow.py`; `web/templates/portal_admin.html` | Đăng ký, liên kết người nhà, quản lý và phân công |
| [2] | `app/today_todo_widget.py`; `services/medication_schedule_sync.py`; `services/elder_sync_client.py`; `tests/test_elder_prescription_audio_regression.py`; `tests/test_prescription_cancel_sync.py` | Đơn thuốc, tạo lịch, xác nhận và hủy đơn |
| [3] | `web/api_router.py`; hai cổng người nhà và bác sĩ trong `web/templates/`; `tests/test_vitals_sync_regression.py`; `tests/test_caregiver_clinician_health_sync.py` | Nhập, truy xuất và đồng bộ số đo |
| [4] | `config.py`; `app/dashboard.py`; `modules/rehabilitation/rehab_engine.py`; `tests/test_routine_and_games.py`; `tests/test_caregiver_rehab_config_sync.py` | Ba bài tập, kế hoạch và tiến trình |
| [5] | `services/family_music_service.py`; `services/music_playback.py`; `modules/cognitive_games/`; `tests/test_family_music.py` | Trò chơi, tải nhạc và phát âm thanh |
| [6] | `services/emotion_summary_service.py`; `tests/test_emotion_summary.py` | Tổng hợp thông tin biểu cảm |
| [7] | `app/local_voice_widget.py`; `services/local_voice/`; `services/local_rules/`; `tests/local_rules/` | Nhận giọng nói, luật xử lý, yêu cầu hỗ trợ |
| [8] | `packaging/windows_portable/`; `releases/AI_FOR_EXAM_VALIDATION.json`; `QA_REPORT.txt` trong từng gói | Đóng gói, khởi động và kiểm tra toàn vẹn |
| [9] | `services/local_voice/engine.py`; `services/local_voice/config.py`; `docs/STT_ZIPFORMER.md`; `reports/local_stt/zipformer-benchmark.json` | Cập nhật nhận dạng cục bộ và số đo trên một tệp lời nói |

Các nguồn trên xác nhận việc triển khai và kiểm thử nội bộ. Chúng không thay cho nghiên cứu y khoa về hiệu quả điều trị hoặc khảo sát nhu cầu người cao tuổi.

### 2. Phụ lục A. Hồ sơ kết quả kiểm thử

Hai hồ sơ JUnit được lưu tại:

- `runtime/report-verification/results.xml`: 35 ca, gồm 32 đạt và 3 không đạt.
- `runtime/report-verification-additional/results.xml`: 235 ca, gồm 220 đạt, 3 không đạt và 12 lỗi thiết lập.

Bảng chi tiết theo nhóm và danh sách trường hợp chưa đạt được lưu kèm trong `BANG_CHUNG_KIEM_THU_2026-10-24.json`, cùng thư mục với báo cáo. Kết quả phần mềm không được quy đổi thành tỷ lệ hiệu quả chăm sóc, độ chính xác mô hình hoặc mức hài lòng người dùng.

### 3. Phụ lục B. Luồng trình diễn đề xuất từ các chức năng hiện có

| Bước | Người thao tác | Nội dung trình diễn | Kết quả cần quan sát |
|---:|---|---|---|
| 1 | Người hỗ trợ, quản trị viên | Tạo hồ sơ, đăng ký người nhà, phân công bác sĩ | Mỗi tài khoản truy cập đúng hồ sơ |
| 2 | Bác sĩ | Tạo đơn thử có ngày và giờ hợp lệ | Người nhà xem đơn; ứng dụng có đơn và lịch tương ứng |
| 3 | Người cao tuổi | Xác nhận một lần uống thử | Trạng thái được ghi nhận trên hồ sơ |
| 4 | Người nhà | Nhập một nhóm số đo thử | Người nhà, bác sĩ và ứng dụng đọc được dữ liệu tương ứng |
| 5 | Người cao tuổi | Bắt đầu bài tập trước camera | Bộ đếm và tiến độ thay đổi theo dữ liệu quan sát |
| 6 | Người nhà, người cao tuổi | Tải MP3 hoặc WAV rồi chọn phát trên ứng dụng | Danh mục nhận bài mới; loa phát được khi người dùng chọn |
| 7 | Người cao tuổi, người nhận | Gửi yêu cầu hỗ trợ và tiếp nhận trên cổng web | Phân biệt được yêu cầu đã tạo, tình trạng gửi và việc tiếp nhận |
| 8 | Người vận hành | Đóng chương trình theo hướng dẫn | Các thành phần dừng theo quy trình |

Đây là kịch bản dành cho đợt trình diễn tiếp theo, không phải bản ghi một buổi thử nghiệm với người sử dụng đã diễn ra. Mọi đơn thuốc, số đo và thông tin liên hệ dùng để trình diễn cần được nhận biết rõ là dữ liệu thử.
