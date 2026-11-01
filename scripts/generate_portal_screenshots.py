#!/usr/bin/env python3
"""
Script generating UI screenshots for:
1. docs/screenshots/caregiver_portal.png
2. docs/screenshots/clinician_portal.png
3. docs/screenshots/rehab_flow_6a.png
Uses PyQt5 offscreen rendering.
"""

import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QTextEdit, QSizePolicy, QLineEdit
)
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QSize


def init_app():
    return QApplication.instance() or QApplication(sys.argv)


def create_card(title: str, accent_color: str = "#2563eb") -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
        }}
    """)
    layout = QVBoxLayout(card)
    layout.setSpacing(10)
    layout.setContentsMargins(14, 14, 14, 14)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(f"""
        font-size: 14px;
        font-weight: bold;
        color: {accent_color};
        border-bottom: 2px solid {accent_color};
        padding-bottom: 4px;
    """)
    layout.addWidget(title_lbl)
    return card, layout


class BloodPressureVisualChartWidget(QWidget):
    """
    Dedicated Vector Graphic Visual Chart for Blood Pressure Vitals.
    Renders dual-component lines (Systolic/Diastolic), target safe bands,
    discrete data points, pulse ties, and explicit gap representation on missing days (no zero-fill).
    """
    def __init__(self, is_clinician: bool = False, parent=None):
        super().__init__(parent)
        self.is_clinician = is_clinician
        self.setMinimumHeight(320 if is_clinician else 245)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = self.width()
        h = self.height()

        # Background rounded box
        painter.setPen(QPen(QColor("#e2e8f0"), 1))
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawRoundedRect(0, 0, w, h, 8, 8)

        # Plot margins
        pad_l = 48
        pad_r = 20
        pad_t = 42
        pad_b = 38
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        # Y scale: 50 to 170 mmHg
        min_y = 50
        max_y = 170

        def get_y(val):
            return pad_t + plot_h - ((val - min_y) / (max_y - min_y)) * plot_h

        # Header Legend & Status
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        # Red dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#ef4444")))
        painter.drawEllipse(pad_l, 14, 10, 10)
        painter.setPen(QColor("#1e293b"))
        painter.drawText(pad_l + 14, 23, "Tâm thu (SYS)")

        # Blue dot
        painter.setBrush(QBrush(QColor("#3b82f6")))
        painter.drawEllipse(pad_l + 105, 14, 10, 10)
        painter.drawText(pad_l + 119, 23, "Tâm trương (DIA)")

        # Target range indicator
        painter.setBrush(QBrush(QColor(34, 197, 94, 50)))
        painter.setPen(QPen(QColor("#22c55e"), 1, Qt.DashLine))
        painter.drawRect(pad_l + 230, 15, 14, 8)
        painter.setPen(QColor("#15803d"))
        painter.drawText(pad_l + 248, 23, "Dải an toàn (<130/85)")

        # Status badge on right
        painter.setPen(QColor("#16a34a"))
        status_txt = "Gần nhất: 125/82 mmHg (Ổn định)" if not self.is_clinician else "Gần nhất: 125/82 mmHg (Omron Auto)"
        painter.drawText(w - pad_r - 210, 23, status_txt)

        # Draw Target Safe Band: SYS 90-130, DIA 60-85 -> Combined 60 to 130 mmHg
        y_130 = get_y(130)
        y_60 = get_y(60)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(34, 197, 94, 18)))
        painter.drawRect(pad_l, int(y_130), int(plot_w), int(y_60 - y_130))

        painter.setPen(QPen(QColor(34, 197, 94, 80), 1, Qt.DashLine))
        painter.drawLine(pad_l, int(y_130), int(pad_l + plot_w), int(y_130))
        painter.setPen(QPen(QColor(59, 130, 246, 80), 1, Qt.DashLine))
        y_85 = get_y(85)
        painter.drawLine(pad_l, int(y_85), int(pad_l + plot_w), int(y_85))

        # Grid lines & Y labels
        painter.setFont(QFont("Segoe UI", 8))
        for y_val in [60, 80, 100, 120, 140, 160]:
            y_pos = int(get_y(y_val))
            painter.setPen(QPen(QColor("#f1f5f9"), 1))
            painter.drawLine(pad_l, y_pos, int(pad_l + plot_w), y_pos)
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(5, y_pos + 4, 38, 12, Qt.AlignRight, str(y_val))

        # Y unit
        painter.setPen(QColor("#64748b"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.drawText(5, pad_t - 5, "mmHg")

        # 5 slots on X:
        # Slot 0: 02/10 -> 132 / 85
        # Slot 1: 03/10 -> 130 / 84
        # Slot 2: 04/10 -> [MISSING DAY GAP - KHÔNG ĐIỀN 0]
        # Slot 3: 05/10 -> 128 / 84
        # Slot 4: 06/10 -> 125 / 82
        x_slots = [
            pad_l + int((0 / 4) * plot_w),
            pad_l + int((1 / 4) * plot_w),
            pad_l + int((2 / 4) * plot_w),
            pad_l + int((3 / 4) * plot_w),
            pad_l + int((4 / 4) * plot_w),
        ]

        # Draw shaded column for missing day 04/10
        gap_w = int(plot_w / 4 * 0.72)
        gap_x = int(x_slots[2] - gap_w / 2)
        painter.setPen(QPen(QColor("#cbd5e1"), 1, Qt.DashLine))
        painter.setBrush(QBrush(QColor(241, 245, 249, 140)))
        painter.drawRoundedRect(gap_x, int(pad_t), gap_w, int(plot_h), 4, 4)
        painter.setPen(QColor("#94a3b8"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.drawText(gap_x, int(pad_t + plot_h / 2 - 8), gap_w, 20, Qt.AlignCenter, "[Khuyết số đo]")
        painter.setFont(QFont("Segoe UI", 7))
        painter.drawText(gap_x, int(pad_t + plot_h / 2 + 8), gap_w, 15, Qt.AlignCenter, "Không nối qua điểm 0")

        # X-axis date labels
        x_labels = ["02/10", "03/10", "04/10", "05/10", "06/10"]
        painter.setFont(QFont("Segoe UI", 8))
        for i, (xs, lbl) in enumerate(zip(x_slots, x_labels)):
            painter.setPen(QColor("#64748b"))
            painter.drawText(xs - 25, int(pad_t + plot_h + 16), 50, 14, Qt.AlignCenter, lbl)

        # Segment 1: Slot 0 -> Slot 1
        # Segment 2: Slot 3 -> Slot 4
        # Systolic (Red) lines
        painter.setPen(QPen(QColor("#ef4444"), 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(x_slots[0], int(get_y(132)), x_slots[1], int(get_y(130)))
        painter.drawLine(x_slots[3], int(get_y(128)), x_slots[4], int(get_y(125)))

        # Diastolic (Blue) lines
        painter.setPen(QPen(QColor("#3b82f6"), 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(x_slots[0], int(get_y(85)), x_slots[1], int(get_y(84)))
        painter.drawLine(x_slots[3], int(get_y(84)), x_slots[4], int(get_y(82)))

        # Data points data
        data_points = [
            (0, 132, 85, "132", "85"),
            (1, 130, 84, "130", "84"),
            (3, 128, 84, "128", "84"),
            (4, 125, 82, "125", "82"),
        ]

        for slot_idx, sys_v, dia_v, sys_str, dia_str in data_points:
            xs = x_slots[slot_idx]
            ys_s = int(get_y(sys_v))
            ys_d = int(get_y(dia_v))

            # Pulse tie (dotted vertical bar)
            painter.setPen(QPen(QColor("#cbd5e1"), 1.5, Qt.DotLine))
            painter.drawLine(xs, ys_s, xs, ys_d)

            # Systolic circle
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.setBrush(QBrush(QColor("#ef4444")))
            painter.drawEllipse(xs - 5, ys_s - 5, 10, 10)

            # Systolic label
            painter.setPen(QColor("#dc2626"))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.drawText(xs - 20, ys_s - 16, 40, 12, Qt.AlignCenter, sys_str)

            # Diastolic circle
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.setBrush(QBrush(QColor("#3b82f6")))
            painter.drawEllipse(xs - 5, ys_d - 5, 10, 10)

            # Diastolic label
            painter.setPen(QColor("#2563eb"))
            painter.drawText(xs - 20, ys_d + 7, 40, 12, Qt.AlignCenter, dia_str)

            if self.is_clinician and slot_idx == 4:
                painter.setPen(QColor("#7c3aed"))
                painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
                painter.drawText(xs - 25, ys_s - 26, 50, 10, Qt.AlignCenter, "n=2 mẫu")


def build_caregiver_portal() -> QWidget:
    w = QWidget()
    w.resize(1380, 1050)
    w.setStyleSheet("background-color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif;")

    main_layout = QVBoxLayout(w)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(12)

    # Top Header
    header = QFrame()
    header.setStyleSheet("background-color: #1e3a8a; border-radius: 8px; padding: 14px;")
    h_layout = QHBoxLayout(header)
    
    title_box = QVBoxLayout()
    app_title = QLabel("CỔNG THÔNG TIN NGƯỜI NHÀ (CAREGIVER PORTAL)")
    app_title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold;")
    sub_title = QLabel("Hệ thống trợ lý theo dõi sức khỏe và phục hồi chức năng người cao tuổi")
    sub_title.setStyleSheet("color: #93c5fd; font-size: 12px;")
    title_box.addWidget(app_title)
    title_box.addWidget(sub_title)
    h_layout.addLayout(title_box)

    h_layout.addStretch()

    user_info = QLabel("👤 Người nhà: Nguyễn Văn Anh | Vai trò: Con trai\nBệnh nhân đang xem: Bà Nguyễn Thị Mai (ID: pat-001)")
    user_info.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; background-color: #1e40af; padding: 8px; border-radius: 6px;")
    h_layout.addWidget(user_info)
    main_layout.addWidget(header)

    # Navigation Tab Bar (Gộp Tổng quan & Chỉ số sức khỏe thành một tab)
    tab_bar = QFrame()
    tab_bar.setStyleSheet("background-color: #e2e8f0; border-radius: 8px; padding: 4px;")
    tb_layout = QHBoxLayout(tab_bar)
    tb_layout.setContentsMargins(6, 4, 6, 4)
    tb_layout.setSpacing(8)
    tabs = [
        ("📊 Tổng quan & Chỉ số sức khỏe", True),
        ("🩺 Nhập chỉ số sức khỏe", False),
        ("💊 Nhắc thuốc hôm nay", False),
        ("🚨 Hộp thư cảnh báo", False),
        ("🧠 Nhật ký tinh thần", False),
        ("🏋️ Phục hồi chức năng", False),
        ("📝 Gửi báo cáo", False),
    ]
    for title, is_active in tabs:
        btn = QPushButton(title)
        if is_active:
            btn.setStyleSheet("background-color: #1e3a8a; color: #ffffff; font-weight: bold; padding: 7px 14px; border-radius: 6px; font-size: 12px; border: none;")
        else:
            btn.setStyleSheet("background-color: transparent; color: #475569; font-weight: 500; padding: 7px 14px; border-radius: 6px; font-size: 12px; border: none;")
        tb_layout.addWidget(btn)
    tb_layout.addStretch()
    main_layout.addWidget(tab_bar)

    # Hotline Banner (Section 9 Requirement)
    hotline_card = QFrame()
    hotline_card.setStyleSheet("background-color: #fef2f2; border: 2px solid #ef4444; border-radius: 8px; padding: 12px;")
    hotline_layout = QHBoxLayout(hotline_card)
    
    hl_text_box = QVBoxLayout()
    hl_title = QLabel("🚨 ĐƯỜNG DÂY NÓNG: GỌI BÁC SĨ TRONG GIỜ TRỰC (08:00 - 17:00)")
    hl_title.setStyleSheet("color: #b91c1c; font-size: 14px; font-weight: bold;")
    hl_sub = QLabel(
        "Bác sĩ phụ trách: BS. Lê Văn Cường (Khoa Nội Tim Mạch - Phụ trách ca trực)\n"
        "Trạng thái: ĐANG TRONG GIỜ TRỰC | Lưu ý: Không cam kết hỗ trợ 24/7. Ngoài giờ vui lòng gọi 115."
    )
    hl_sub.setStyleSheet("color: #7f1d1d; font-size: 12px;")
    hl_text_box.addWidget(hl_title)
    hl_text_box.addWidget(hl_sub)
    hotline_layout.addLayout(hl_text_box)

    hotline_layout.addStretch()

    # Call button: Disabled due to unverified demo phone (Requirement 9)
    btn_call = QPushButton("GỌI BÁC SĨ (000-000-000)\n[DEMO - NÚT BỊ VÔ HIỆU HÓA]")
    btn_call.setEnabled(False)
    btn_call.setStyleSheet("""
        background-color: #cbd5e1;
        color: #64748b;
        font-weight: bold;
        font-size: 12px;
        border-radius: 6px;
        padding: 10px 18px;
        border: 1px solid #94a3b8;
    """)
    hotline_layout.addWidget(btn_call)

    btn_115 = QPushButton("DỰ PHÒNG: GỌI CẤP CỨU 115\n(ĐÃ XÁC NHẬN SẴN SÀNG)")
    btn_115.setStyleSheet("""
        background-color: #dc2626;
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        border-radius: 6px;
        padding: 10px 18px;
    """)
    hotline_layout.addWidget(btn_115)
    main_layout.addWidget(hotline_card)

    # 4 Metric Summary Boxes (Gộp trong Tổng quan & Chỉ số sức khỏe)
    metric_row = QHBoxLayout()
    metric_row.setSpacing(12)
    metric_defs = [
        ("Huyết áp đo mới nhất", "125 / 82 mmHg", "06/10 08:30 (Omron Smart)", "#0284c7"),
        ("Nhịp tim đo mới nhất", "75 bpm", "06/10 08:30 (Bình thường)", "#059669"),
        ("Lịch uống thuốc hôm nay", "1 / 2 liều", "Đã uống sáng, còn cữ tối", "#d97706"),
        ("Phục hồi chức năng (16:00)", "10 / 10 lần", "Camera AI xác nhận đủ chỉ tiêu", "#7c3aed"),
    ]
    for lbl, val, sub, color in metric_defs:
        m_box = QFrame()
        m_box.setStyleSheet(f"background: white; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 4px solid {color}; padding: 8px 12px;")
        mb_layout = QVBoxLayout(m_box)
        mb_layout.setContentsMargins(6, 6, 6, 6)
        mb_layout.setSpacing(3)
        l_lbl = QLabel(lbl)
        l_lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        l_val = QLabel(val)
        l_val.setStyleSheet("color: #0f172a; font-size: 18px; font-weight: 800;")
        l_sub = QLabel(sub)
        l_sub.setStyleSheet("color: #94a3b8; font-size: 11px;")
        mb_layout.addWidget(l_lbl)
        mb_layout.addWidget(l_val)
        mb_layout.addWidget(l_sub)
        metric_row.addWidget(m_box)
    main_layout.addLayout(metric_row)

    # 4-card Grid
    grid = QGridLayout()
    grid.setSpacing(14)

    # Card 1: Huyết áp & Sinh hiệu (Biểu đồ đồ họa trực quan 2 thành phần gộp trong Tổng quan)
    c1, l1 = create_card("1. BIỂU ĐỒ SINH HIỆU HUYẾT ÁP (TRỰC QUAN HÓA TRONG TỔNG QUAN)", "#0284c7")
    chart_widget = BloodPressureVisualChartWidget(is_clinician=False)
    l1.addWidget(chart_widget)
    lbl_c1_note = QLabel("✓ Trực quan hóa dữ liệu xu hướng: Tâm thu (đỏ) & Tâm trương (xanh). Ngày thiếu giữ khoảng trống, tuyệt đối không điền số 0.")
    lbl_c1_note.setStyleSheet("color: #0369a1; font-size: 11px; font-style: italic;")
    l1.addWidget(lbl_c1_note)
    grid.addWidget(c1, 0, 0)

    # Card 2: Nhắc thuốc & Tuân thủ
    c2, l2 = create_card("2. NHẮC THUỐC & XÁC NHẬN TUÂN THỦ", "#16a34a")
    med_box = QVBoxLayout()
    med_item = QLabel("💊 Amlodipine 5mg (1 viên) - Lịch uống: 08:00 hằng ngày")
    med_item.setStyleSheet("font-size: 12px; font-weight: bold; color: #15803d;")
    med_status = QLabel("Trạng thái: [ĐÃ XÁC NHẬN - CONFIRMED] (Lúc 08:05)")
    med_status.setStyleSheet("font-size: 12px; color: #166534; font-weight: 500;")
    med_note = QLabel(
        "⚠️ Nhãn cảnh báo an toàn: Xác nhận từ xa là thông tin tự khai báo,\n"
        "không chứng minh việc nuốt thuốc thực tế."
    )
    med_note.setStyleSheet("font-size: 11px; color: #854d0e; background-color: #fefce8; padding: 6px; border-radius: 4px;")
    med_box.addWidget(med_item)
    med_box.addWidget(med_status)
    med_box.addWidget(med_note)
    l2.addLayout(med_box)

    btn_row = QHBoxLayout()
    btn_taken = QPushButton("✓ Đã uống (Tự khai báo)")
    btn_taken.setStyleSheet("background-color: #22c55e; color: white; padding: 6px; border-radius: 4px; font-weight: bold;")
    btn_snooze = QPushButton("⏰ Nhắc lại sau 15p")
    btn_snooze.setStyleSheet("background-color: #eab308; color: white; padding: 6px; border-radius: 4px; font-weight: bold;")
    btn_help = QPushButton("🆘 Cần trợ giúp")
    btn_help.setStyleSheet("background-color: #ef4444; color: white; padding: 6px; border-radius: 4px; font-weight: bold;")
    btn_row.addWidget(btn_taken)
    btn_row.addWidget(btn_snooze)
    btn_row.addWidget(btn_help)
    l2.addLayout(btn_row)
    grid.addWidget(c2, 0, 1)

    # Card 3: Phục hồi chức năng Mục 6A
    c3, l3 = create_card("3. PHỤC HỒI CHỨC NĂNG CÓ CAMERA XÁC THỰC (MỤC 6A)", "#7c3aed")
    rehab_info = QLabel(
        "Bài tập: Nâng cánh tay (Arm Raise) | Giờ nhắc: 16:00 (Asia/Ho_Chi_Minh)\n"
        "Chỉ tiêu snapshot phiên: 10 lần | Camera AI xác thực: 10/10 lần"
    )
    rehab_info.setStyleSheet("font-size: 12px; color: #4c1d95; font-weight: 500;")
    l3.addWidget(rehab_info)

    pbar = QProgressBar()
    pbar.setValue(100)
    pbar.setStyleSheet("""
        QProgressBar {
            border: 1px solid #c4b5fd;
            border-radius: 6px;
            text-align: center;
            height: 22px;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: #8b5cf6;
        }
    """)
    l3.addWidget(pbar)

    rehab_status_badge = QLabel("TRẠNG THÁI: [camera_verified_completed - HOÀN THÀNH XÁC THỰC]")
    rehab_status_badge.setStyleSheet("color: #ffffff; background-color: #6d28d9; padding: 6px; border-radius: 4px; font-weight: bold; font-size: 11px;")
    l3.addWidget(rehab_status_badge)

    rehab_guard = QLabel("✓ Khóa Idempotency kích hoạt: Chống đếm trùng khung hình. Khi mất dấu -> chuyển verification_unavailable.")
    rehab_guard.setStyleSheet("color: #5b21b6; font-size: 11px; font-style: italic;")
    l3.addWidget(rehab_guard)
    grid.addWidget(c3, 1, 0)

    # Card 4: Tinh thần & Hộp thoại Trò chuyện với Bác sĩ
    c4, l4 = create_card("4. THEO DÕI TINH THẦN & HỘP THOẠI TRÒ CHUYỆN VỚI BÁC SĨ", "#d97706")
    emotion_box = QLabel(
        "• Camera AI nhận diện biểu cảm: Vui vẻ (0.82) | Bình thường (0.18)\n"
        "• Người bệnh tự khai tâm trạng: 'Vui vẻ, tinh thần thoải mái'\n"
        "(Phân tách độc lập giữa suy luận biểu cảm máy học và tâm trạng tự khai báo)"
    )
    emotion_box.setStyleSheet("font-size: 11px; color: #92400e; background-color: #fffbeb; padding: 6px; border-radius: 4px;")
    l4.addWidget(emotion_box)

    chat_box = QVBoxLayout()
    chat_box.setSpacing(4)
    cg_b = QFrame()
    cg_b.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px;")
    cg_b_l = QVBoxLayout(cg_b)
    cg_b_l.setContentsMargins(5, 5, 5, 5)
    cg_h = QLabel("👤 Bạn (Người nhà - 09:30) [Mức độ: Bình thường]:")
    cg_h.setStyleSheet("color: #d97706; font-size: 10px; font-weight: bold;")
    cg_txt = QLabel("Bà ăn ngủ tốt, sau khi tập bài 16:00 hơi mỏi vai nhưng đã hồi phục sau 15 phút.")
    cg_txt.setStyleSheet("color: #1e293b; font-size: 10.5px;")
    cg_b_l.addWidget(cg_h)
    cg_b_l.addWidget(cg_txt)
    chat_box.addWidget(cg_b)

    doc_b = QFrame()
    doc_b.setStyleSheet("background-color: #eef2ff; border: 1px solid #c7d2fe; border-radius: 6px; padding: 6px;")
    doc_b_l = QVBoxLayout(doc_b)
    doc_b_l.setContentsMargins(5, 5, 5, 5)
    doc_h = QLabel("👨‍⚕️ BS. Lê Văn Cường (09:45) [Phản hồi lâm sàng]:")
    doc_h.setStyleSheet("color: #4338ca; font-size: 10px; font-weight: bold;")
    doc_txt = QLabel("Đã ghi nhận, cho bà nghỉ ngơi thêm và uống nhiều nước ấm nhé.")
    doc_txt.setStyleSheet("color: #1e1b4b; font-size: 10.5px;")
    doc_b_l.addWidget(doc_h)
    doc_b_l.addWidget(doc_txt)
    chat_box.addWidget(doc_b)
    l4.addLayout(chat_box)
    grid.addWidget(c4, 1, 1)

    main_layout.addLayout(grid)
    return w


def build_caregiver_vitals_entry_portal() -> QWidget:
    w = QWidget()
    w.resize(1440, 1050)
    w.setStyleSheet("background-color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif;")

    main_layout = QVBoxLayout(w)
    main_layout.setContentsMargins(18, 18, 18, 18)
    main_layout.setSpacing(12)

    # Top Brand Header
    header = QFrame()
    header.setStyleSheet("background-color: #1e3a8a; border-radius: 8px; padding: 12px 16px;")
    h_layout = QHBoxLayout(header)
    
    title_box = QVBoxLayout()
    app_title = QLabel("CỔNG NGƯỜI NHÀ (CAREGIVER PORTAL)")
    app_title.setStyleSheet("color: #ffffff; font-size: 17px; font-weight: bold;")
    sub_title = QLabel("Hệ thống Chăm Sóc Người Cao Tuổi & Phục Hồi Chức Năng Thông Minh")
    sub_title.setStyleSheet("color: #93c5fd; font-size: 11.5px;")
    title_box.addWidget(app_title)
    title_box.addWidget(sub_title)
    h_layout.addLayout(title_box)
    h_layout.addStretch()

    badge = QLabel("● Đang kết nối trực tiếp (SSE)")
    badge.setStyleSheet(
        "background-color: #10b981; color: #ffffff; font-weight: bold; font-size: 12px; "
        "padding: 6px 14px; border-radius: 12px; margin-right: 12px;"
    )
    h_layout.addWidget(badge)

    user_info = QLabel("👤 Người nhà: hiu (Chăm sóc cụ: bach - patient_001)")
    user_info.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; background-color: #1e40af; padding: 8px 12px; border-radius: 6px;")
    h_layout.addWidget(user_info)
    main_layout.addWidget(header)

    # Navigation Tab Bar
    tab_bar = QFrame()
    tab_bar.setStyleSheet("background-color: #e2e8f0; border-radius: 8px; padding: 4px;")
    tb_layout = QHBoxLayout(tab_bar)
    tb_layout.setContentsMargins(6, 4, 6, 4)
    tb_layout.setSpacing(8)
    tabs = [
        ("📊 Tổng quan & Chỉ số sức khỏe", False),
        ("🩺 Nhập chỉ số sức khỏe", True),
        ("💊 Nhắc thuốc hôm nay", False),
        ("🚨 Hộp thư cảnh báo", False),
        ("🧠 Nhật ký tinh thần", False),
        ("🏋️ Phục hồi chức năng", False),
        ("💬 Trò chuyện & Ghi nhận Bác sĩ", False),
    ]
    for title, is_active in tabs:
        btn = QPushButton(title)
        if is_active:
            btn.setStyleSheet("background-color: #2878F0; color: #ffffff; font-weight: bold; padding: 8px 16px; border-radius: 6px; font-size: 13px; border: none;")
        else:
            btn.setStyleSheet("background-color: transparent; color: #475569; font-weight: 500; padding: 8px 16px; border-radius: 6px; font-size: 13px; border: none;")
        tb_layout.addWidget(btn)
    tb_layout.addStretch()
    main_layout.addWidget(tab_bar)

    # Form Card: Nhập chỉ số theo dõi sức khỏe
    form_card, form_layout = create_card("🩺 NHẬP CHỈ SỐ THEO DÕI SỨC KHỎE (ĐỒNG BỘ HAI CHIỀU TỨC THÌ)", "#2878F0")
    
    # Disclaimer box
    disc = QLabel("💡 Hướng dẫn: Người nhà đo và nhập các chỉ số định kỳ (Huyết áp, Nhịp tim, SpO2, Đường huyết, Thân nhiệt). Dữ liệu sẽ lập tức được đồng bộ lên máy tính bảng người già và màn hình theo dõi của Bác sĩ phụ trách.")
    disc.setStyleSheet("background-color: #eff6ff; border-left: 4px solid #2878F0; padding: 10px 14px; border-radius: 6px; color: #1e3a8a; font-size: 12.5px;")
    form_layout.addWidget(disc)

    # Form 3 Columns Grid
    cols_layout = QHBoxLayout()
    cols_layout.setSpacing(14)

    # Col 1: Time & Device
    c1 = QFrame()
    c1.setStyleSheet("background-color: #f8fafc; border: 1.5px solid #dfe8f3; border-radius: 8px; padding: 12px;")
    l1 = QVBoxLayout(c1)
    l1.addWidget(QLabel("⏱️ Thời điểm & Thiết bị đo"))
    l1.itemAt(0).widget().setStyleSheet("font-weight: bold; color: #14233F; font-size: 13px;")
    l1.addWidget(QLabel("Thời gian đo:"))
    l1.addWidget(QLineEdit("2026-10-07 18:30"))
    l1.addWidget(QLabel("Thiết bị / Nguồn đo:"))
    l1.addWidget(QLineEdit("Máy đo huyết áp bắp tay Omron & Kẹp SpO2"))
    l1.addWidget(QLabel("Ghi chú lâm sàng:"))
    l1.addWidget(QLineEdit("Đo sau khi nghỉ ngơi 15 phút, người cao tuổi tỉnh táo, vừa uống nước ấm"))
    cols_layout.addWidget(c1)

    # Col 2: Blood Pressure & Heart Rate
    c2 = QFrame()
    c2.setStyleSheet("background-color: #f8fafc; border: 1.5px solid #dfe8f3; border-radius: 8px; padding: 12px;")
    l2 = QVBoxLayout(c2)
    l2.addWidget(QLabel("❤️ Huyết áp & Nhịp tim"))
    l2.itemAt(0).widget().setStyleSheet("font-weight: bold; color: #14233F; font-size: 13px;")
    
    bp_inputs = QHBoxLayout()
    bp_inputs.addWidget(QLabel("SYS (Tâm thu):"))
    bp_inputs.addWidget(QLineEdit("122"))
    bp_inputs.addWidget(QLabel("DIA (Tâm trương):"))
    bp_inputs.addWidget(QLineEdit("78"))
    l2.addLayout(bp_inputs)

    bp_badge = QLabel("✅ Huyết áp bình thường (122/78 mmHg)")
    bp_badge.setStyleSheet("background-color: #e6f7f2; color: #167D62; font-weight: bold; padding: 6px 10px; border-radius: 6px; font-size: 12px;")
    l2.addWidget(bp_badge)

    hr_row = QHBoxLayout()
    hr_row.addWidget(QLabel("Nhịp tim (Pulse):"))
    hr_row.addWidget(QLineEdit("72 bpm"))
    l2.addLayout(hr_row)
    l2.addWidget(QLabel("✅ Nhịp tim bình thường (Dải tham chiếu: 60 - 90 bpm)"))
    cols_layout.addWidget(c2)

    # Col 3: SpO2, Glucose, Temp
    c3 = QFrame()
    c3.setStyleSheet("background-color: #f8fafc; border: 1.5px solid #dfe8f3; border-radius: 8px; padding: 12px;")
    l3 = QVBoxLayout(c3)
    l3.addWidget(QLabel("🩺 SpO2, Đường huyết & Thân nhiệt"))
    l3.itemAt(0).widget().setStyleSheet("font-weight: bold; color: #14233F; font-size: 13px;")

    spo2_row = QHBoxLayout()
    spo2_row.addWidget(QLabel("SpO2 (%):"))
    spo2_row.addWidget(QLineEdit("98%"))
    spo2_badge = QLabel("✅ An toàn")
    spo2_badge.setStyleSheet("background-color: #e6f7f2; color: #167D62; font-weight: bold; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
    spo2_row.addWidget(spo2_badge)
    l3.addLayout(spo2_row)

    glu_row = QHBoxLayout()
    glu_row.addWidget(QLabel("Đường huyết:"))
    glu_row.addWidget(QLineEdit("102 mg/dL (Lúc đói)"))
    l3.addLayout(glu_row)

    temp_row = QHBoxLayout()
    temp_row.addWidget(QLabel("Thân nhiệt:"))
    temp_row.addWidget(QLineEdit("36.6 °C"))
    temp_badge = QLabel("✅ Bình thường")
    temp_badge.setStyleSheet("background-color: #e6f7f2; color: #167D62; font-weight: bold; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
    temp_row.addWidget(temp_badge)
    l3.addLayout(temp_row)
    cols_layout.addWidget(c3)

    form_layout.addLayout(cols_layout)

    # Action buttons
    act_row = QHBoxLayout()
    act_row.addStretch()
    btn_reset = QPushButton("🔄 Nhập lại / Làm mới")
    btn_reset.setStyleSheet("background: white; border: 1.5px solid #cbd5e1; padding: 8px 16px; border-radius: 6px; font-weight: 600;")
    btn_save = QPushButton("💾 Lưu & Đồng bộ chỉ số sức khỏe")
    btn_save.setStyleSheet("background: #2878F0; color: white; border: none; padding: 10px 24px; border-radius: 6px; font-weight: bold; font-size: 13px;")
    act_row.addWidget(btn_reset)
    act_row.addWidget(btn_save)
    form_layout.addLayout(act_row)
    main_layout.addWidget(form_card)

    # Table Card: Lịch sử các lần đo gần nhất
    table_card, table_layout = create_card("📋 LỊCH SỬ CÁC LẦN ĐO GẦN NHẤT (ĐỒNG BỘ TỨC THÌ)", "#14233F")
    tbl = QTableWidget(5, 7)
    tbl.setHorizontalHeaderLabels([
        "Thời gian đo", "Huyết áp (SYS/DIA)", "Nhịp tim", "SpO2", "Đường huyết", "Thân nhiệt", "Người nhập & Ghi chú"
    ])
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    tbl.verticalHeader().setVisible(False)
    tbl.setRowHeight(0, 36)
    
    rows_data = [
        ("2026-10-07 18:30", "125/82 mmHg (Bình thường)", "76 bpm", "98% (An toàn)", "108 mg/dL", "36.7 °C", "hiu (Người nhà) — Sau khi đi dạo"),
        ("2026-10-07 18:05", "122/78 mmHg (Bình thường)", "72 bpm", "98% (An toàn)", "102 mg/dL", "36.6 °C", "hiu (Người nhà) — Cụ cảm thấy khỏe"),
        ("2026-10-07 17:09", "133/77 mmHg (Tiền tăng HA)", "78 bpm", "97% (An toàn)", "112 mg/dL", "36.8 °C", "hiu (Người nhà) — Vừa uống nước"),
        ("2026-10-06 08:30", "125/82 mmHg (Bình thường)", "75 bpm", "98% (An toàn)", "99 mg/dL", "36.5 °C", "Omron Smart Device"),
        ("2026-10-05 19:15", "128/80 mmHg (Bình thường)", "74 bpm", "99% (An toàn)", "105 mg/dL", "36.6 °C", "Người nhà đo thủ công"),
    ]
    for r_idx, r_vals in enumerate(rows_data):
        for c_idx, val in enumerate(r_vals):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignCenter if c_idx < 6 else Qt.AlignLeft | Qt.AlignVCenter)
            tbl.setItem(r_idx, c_idx, item)
    table_layout.addWidget(tbl)
    main_layout.addWidget(table_card)

    return w


def build_clinician_portal() -> QWidget:
    w = QWidget()
    w.resize(1440, 1080)
    w.setStyleSheet("background-color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif;")

    main_layout = QVBoxLayout(w)
    main_layout.setContentsMargins(18, 18, 18, 18)
    main_layout.setSpacing(10)

    # Mandatory Simulation Notice Banner
    sim_banner = QFrame()
    sim_banner.setStyleSheet("background-color: #fef3c7; border: 2px solid #f59e0b; border-radius: 8px; padding: 10px 14px;")
    sb_layout = QHBoxLayout(sim_banner)
    sb_text = QLabel(
        "⚠️ CHẾ ĐỘ MÔ PHỎNG / TÀI KHOẢN BÁC SĨ DEMO:\n"
        "Tài khoản bác sĩ này là tài khoản demo phục vụ thử nghiệm và kiểm thử hệ thống. "
        "Mọi chỉ định, hướng dẫn và đơn thuốc mang tính minh họa kỹ thuật, KHÔNG xuất ra người thật, "
        "KHÔNG thay thế phác đồ điều trị y tế chính thức."
    )
    sb_text.setStyleSheet("color: #b45309; font-size: 11.5px; font-weight: bold;")
    sb_layout.addWidget(sb_text)
    main_layout.addWidget(sim_banner)

    # Clinician Header
    header = QFrame()
    header.setStyleSheet("background-color: #0f172a; border-radius: 8px; padding: 12px 16px;")
    h_layout = QHBoxLayout(header)
    
    title_box = QVBoxLayout()
    app_title = QLabel("CỔNG BÁC SĨ ĐIỀU TRỊ (CLINICIAN PORTAL)")
    app_title.setStyleSheet("color: #ffffff; font-size: 17px; font-weight: bold;")
    sub_title = QLabel("Bệnh viện Lão khoa Trung Ương — Quản lý Care Team & Theo dõi Lâm sàng từ xa")
    sub_title.setStyleSheet("color: #94a3b8; font-size: 11.5px;")
    title_box.addWidget(app_title)
    title_box.addWidget(sub_title)
    h_layout.addLayout(title_box)

    h_layout.addStretch()

    user_info = QLabel("👨‍⚕️ BS. Lê Văn Cường (Mô phỏng Demo)\nCare Team: Phụ trách chuyên khoa Tim mạch & Lão khoa")
    user_info.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; background-color: #1e293b; padding: 8px 12px; border-radius: 6px;")
    h_layout.addWidget(user_info)
    main_layout.addWidget(header)

    # App Two-Column Layout: Left Persistent Sidebar + Right Main Area
    two_col_layout = QHBoxLayout()
    two_col_layout.setSpacing(16)

    # ==========================
    # LEFT PERSISTENT SIDEBAR: PATIENT LIST & GREEN DOT INDICATOR
    # ==========================
    sidebar = QFrame()
    sidebar.setFixedWidth(310)
    sidebar.setStyleSheet("background-color: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 10px; padding: 12px;")
    side_layout = QVBoxLayout(sidebar)
    side_layout.setContentsMargins(10, 10, 10, 10)
    side_layout.setSpacing(10)

    side_title_box = QHBoxLayout()
    side_title = QLabel("DANH SÁCH BỆNH NHÂN CỦA BÁC SĨ")
    side_title.setStyleSheet("color: #0f172a; font-size: 12px; font-weight: 800; text-transform: uppercase;")
    side_count = QLabel("2 BN")
    side_count.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold;")
    side_title_box.addWidget(side_title)
    side_title_box.addStretch()
    side_title_box.addWidget(side_count)
    side_layout.addLayout(side_title_box)

    side_desc = QLabel("Bác sĩ phụ trách theo dõi ca trực")
    side_desc.setStyleSheet("color: #94a3b8; font-size: 11px; margin-bottom: 4px;")
    side_layout.addWidget(side_desc)

    # Patient 1 Card (Active)
    p1_card = QFrame()
    p1_card.setStyleSheet("background-color: #eff6ff; border: 1.5px solid #1b63cc; border-radius: 8px; padding: 10px;")
    p1_l = QVBoxLayout(p1_card)
    p1_l.setContentsMargins(8, 8, 8, 8)
    p1_l.setSpacing(4)
    p1_h = QHBoxLayout()
    p1_name = QLabel("👴 Cụ Hoàng Anh")
    p1_name.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a;")
    p1_tag = QLabel("[Đang chọn]")
    p1_tag.setStyleSheet("color: #1b63cc; font-size: 10px; font-weight: bold;")
    p1_h.addWidget(p1_name)
    p1_h.addStretch()
    p1_h.addWidget(p1_tag)
    p1_l.addLayout(p1_h)

    p1_sub = QLabel("ID: patient_001 | 81 tuổi | Nam\nBác sĩ phụ trách tim mạch")
    p1_sub.setStyleSheet("color: #475569; font-size: 11px;")
    p1_l.addWidget(p1_sub)
    p1_status = QLabel("✓ Huyết áp ổn định: 125/82 mmHg")
    p1_status.setStyleSheet("color: #059669; font-size: 10.5px; font-weight: bold;")
    p1_l.addWidget(p1_status)
    side_layout.addWidget(p1_card)

    # Patient 2 Card (Has New Update with Pulsing Green Dot)
    p2_card = QFrame()
    p2_card.setStyleSheet("background-color: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 8px; padding: 10px;")
    p2_l = QVBoxLayout(p2_card)
    p2_l.setContentsMargins(8, 8, 8, 8)
    p2_l.setSpacing(4)
    p2_h = QHBoxLayout()
    p2_name = QLabel("👵 Cụ Mai Hương")
    p2_name.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a;")
    # Pulsing Green Indicator Dot for New Update
    p2_dot = QLabel("🟢 CẬP NHẬT MỚI")
    p2_dot.setStyleSheet("color: #059669; background-color: #d1fae5; border: 1px solid #a7f3d0; border-radius: 10px; padding: 2px 6px; font-size: 10px; font-weight: 800;")
    p2_h.addWidget(p2_name)
    p2_h.addStretch()
    p2_h.addWidget(p2_dot)
    p2_l.addLayout(p2_h)

    p2_sub = QLabel("ID: patient_002 | 76 tuổi | Nữ\nBác sĩ theo dõi đường huyết")
    p2_sub.setStyleSheet("color: #475569; font-size: 11px;")
    p2_l.addWidget(p2_sub)
    p2_alert = QLabel("⚠️ Có 1 cảnh báo thuốc quá hạn chưa xử lý")
    p2_alert.setStyleSheet("color: #dc2626; font-size: 10.5px; font-weight: bold;")
    p2_l.addWidget(p2_alert)
    side_layout.addWidget(p2_card)

    side_note = QLabel("📌 Khi bệnh nhân có cập nhật mới (báo cáo, số đo, cảnh báo trong 24h), hệ thống tự động gắn chấm xanh 🟢 vào hàng tương ứng.")
    side_note.setWordWrap(True)
    side_note.setStyleSheet("color: #64748b; font-size: 10.5px; font-style: italic; background: #f1f5f9; padding: 8px; border-radius: 6px; margin-top: 10px;")
    side_layout.addWidget(side_note)

    side_layout.addStretch()
    two_col_layout.addWidget(sidebar)

    # ==========================
    # RIGHT MAIN CONTENT AREA
    # ==========================
    right_content = QVBoxLayout()
    right_content.setSpacing(10)

    # Navigation Tab Bar
    tab_bar = QFrame()
    tab_bar.setStyleSheet("background-color: #e2e8f0; border-radius: 8px; padding: 4px;")
    tb_layout = QHBoxLayout(tab_bar)
    tb_layout.setContentsMargins(6, 4, 6, 4)
    tb_layout.setSpacing(8)
    tabs = [
        ("📊 Tổng quan & Chỉ số sinh tồn", True),
        ("💊 Đơn thuốc & Điều chỉnh phiên bản", False),
        ("💬 Trò chuyện & Phản hồi Người nhà", False),
        ("💡 Lời khuyên chuyên môn", False),
    ]
    for title, is_active in tabs:
        btn = QPushButton(title)
        if is_active:
            btn.setStyleSheet("background-color: #0f172a; color: #ffffff; font-weight: bold; padding: 6px 12px; border-radius: 6px; font-size: 12px; border: none;")
        else:
            btn.setStyleSheet("background-color: transparent; color: #475569; font-weight: 500; padding: 6px 12px; border-radius: 6px; font-size: 12px; border: none;")
        tb_layout.addWidget(btn)
    tb_layout.addStretch()
    right_content.addWidget(tab_bar)

    # 6 Metric Summary Boxes
    metric_row = QHBoxLayout()
    metric_row.setSpacing(8)
    metric_defs = [
        ("Huyết áp đo mới nhất", "125 / 82 mmHg", "06/10 08:30 (SYS/DIA)", "#0284c7"),
        ("Nhịp tim đo mới nhất", "75 bpm", "06/10 08:30 (Ổn định)", "#7c3aed"),
        ("Đường huyết mới nhất", "115 mg/dL", "06/10 07:00 (~6.4 mmol/L)", "#ea580c"),
        ("SpO2 đo mới nhất", "98 %", "06/10 08:30 (Bình thường)", "#059669"),
        ("Báo cáo người nhà", "0 chưa đọc", "Đã phản hồi toàn bộ", "#d97706"),
        ("Cảnh báo thuốc", "0 quá hạn", "Tuân thủ tốt", "#b91c1c"),
    ]
    for lbl, val, sub, color in metric_defs:
        m_box = QFrame()
        m_box.setStyleSheet(f"background: white; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 4px solid {color}; padding: 6px 8px;")
        mb_layout = QVBoxLayout(m_box)
        mb_layout.setContentsMargins(4, 4, 4, 4)
        mb_layout.setSpacing(2)
        l_lbl = QLabel(lbl)
        l_lbl.setStyleSheet("color: #64748b; font-size: 9.5px; font-weight: 600; text-transform: uppercase;")
        l_val = QLabel(val)
        l_val.setStyleSheet("color: #0f172a; font-size: 14.5px; font-weight: 800;")
        l_sub = QLabel(sub)
        l_sub.setStyleSheet("color: #94a3b8; font-size: 10px;")
        mb_layout.addWidget(l_lbl)
        mb_layout.addWidget(l_val)
        mb_layout.addWidget(l_sub)
        metric_row.addWidget(m_box)
    right_content.addLayout(metric_row)

    # 4-card Grid
    grid = QGridLayout()
    grid.setSpacing(12)

    # Card 1: Theo dõi Sinh hiệu qua Biểu đồ Lâm sàng (PHÓNG TO & ĐA CHỈ SỐ)
    c1, l1 = create_card("1. BIỂU ĐỒ CHỈ SỐ SINH TỒN LÂM SÀNG (ĐA ĐIỂM / TỔNG HỢP NGÀY — PHÓNG TO)", "#0369a1")

    # Vital Metric Sub-Tab Selector Row
    vital_sel_row = QHBoxLayout()
    vital_sel_row.setSpacing(6)
    v_tabs = [
        ("🔴 Huyết áp (BP)", True),
        ("🟣 Nhịp tim (HR)", False),
        ("🟠 Đường huyết (Glucose)", False),
        ("🔵 SpO2", False),
        ("🌡️ Thân nhiệt (Temp)", False),
    ]
    for v_title, v_active in v_tabs:
        v_btn = QPushButton(v_title)
        if v_active:
            v_btn.setStyleSheet("background-color: #4338ca; color: #ffffff; font-weight: bold; padding: 5px 10px; border-radius: 6px; font-size: 11px; border: none;")
        else:
            v_btn.setStyleSheet("background-color: #f1f5f9; color: #334155; font-weight: 600; padding: 5px 10px; border-radius: 6px; font-size: 11px; border: 1px solid #cbd5e1;")
        vital_sel_row.addWidget(v_btn)
    vital_sel_row.addStretch()
    l1.addLayout(vital_sel_row)

    chart_widget = BloodPressureVisualChartWidget(is_clinician=True)
    l1.addWidget(chart_widget)
    lbl_v_note = QLabel("✓ Đầy đủ biểu đồ nhịp tim, đường huyết, SpO2 & huyết áp. Dải mục tiêu an toàn bóng mờ, không nối qua ngày thiếu.")
    lbl_v_note.setStyleSheet("color: #0284c7; font-size: 10.5px; font-style: italic;")
    l1.addWidget(lbl_v_note)
    grid.addWidget(c1, 0, 0)

    # Card 2: Quản lý Đơn thuốc có Phiên bản, Huỷ đơn & Nhập thuốc mới ngoài danh mục
    c2, l2 = create_card("2. ĐƠN THUỐC, ĐIỀU CHỈNH PHIÊN BẢN & HUỶ ĐƠN", "#15803d")
    rx_info = QLabel(
        "• Đơn thuốc hiện hành: Amlodipine 5mg (1 viên/ngày lúc 08:00) — [v2 ACTIVE]\n"
        "• Đơn thuốc cũ: Amlodipine 2.5mg [v1 SUPERSEDED — Lưu vết bất biến]\n"
        "• Tính năng mới: Bác sĩ tự nhập biệt dược mới (Losartan, Coversyl...) & lưu danh mục"
    )
    rx_info.setStyleSheet("font-size: 11px; color: #166534; background-color: #f0fdf4; padding: 7px; border-radius: 4px;")
    l2.addWidget(rx_info)

    rx_action_box = QHBoxLayout()
    rx_action_box.setSpacing(8)
    btn_cancel_rx = QPushButton("🚫 Ngưng hiệu lực đơn này")
    btn_cancel_rx.setStyleSheet("background-color: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; padding: 7px 10px; border-radius: 4px; font-weight: bold; font-size: 11px;")
    btn_edit_rx = QPushButton("➕ Nhập thuốc mới & Tạo bản sửa đổi (v3)")
    btn_edit_rx.setStyleSheet("background-color: #16a34a; color: white; border: none; padding: 7px 10px; border-radius: 4px; font-weight: bold; font-size: 11px;")
    rx_action_box.addWidget(btn_cancel_rx)
    rx_action_box.addWidget(btn_edit_rx)
    l2.addLayout(rx_action_box)

    rx_guard = QLabel("✓ Khi ngưng hiệu lực hoặc sửa đơn: Chỉ huỷ liều tương lai, 100% lịch sử đã uống được bảo lưu vĩnh viễn.")
    rx_guard.setStyleSheet("color: #15803d; font-size: 10.5px; font-style: italic;")
    l2.addWidget(rx_guard)
    grid.addWidget(c2, 0, 1)

    # Card 3: Hộp thoại Trò chuyện & Phản hồi Người nhà
    c3, l3 = create_card("3. HỘP THOẠI TRÒ CHUYỆN & PHẢN HỒI NGƯỜI NHÀ", "#4338ca")
    
    # Chat thread preview
    chat_box = QVBoxLayout()
    chat_box.setSpacing(6)

    # Caregiver Bubble (Left)
    cg_bubble = QFrame()
    cg_bubble.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px;")
    cg_b_l = QVBoxLayout(cg_bubble)
    cg_b_l.setContentsMargins(6, 6, 6, 6)
    cg_header = QLabel("👤 Người nhà (Nguyễn Văn Tuấn) — 09:30 [Mức độ: Bình thường]")
    cg_header.setStyleSheet("color: #d97706; font-size: 10.5px; font-weight: bold;")
    cg_body = QLabel("Cụ Hoàng Anh hôm nay ăn ngủ tốt. Sau khi tập bài nâng tay 16:00 cụ hơi mỏi nhẹ nhưng đã hồi phục sau 15 phút.")
    cg_body.setStyleSheet("color: #1e293b; font-size: 11px;")
    cg_b_l.addWidget(cg_header)
    cg_b_l.addWidget(cg_body)
    chat_box.addWidget(cg_bubble)

    # Doctor Reply Bubble (Right)
    doc_bubble = QFrame()
    doc_bubble.setStyleSheet("background-color: #eef2ff; border: 1px solid #c7d2fe; border-radius: 8px; padding: 8px;")
    doc_b_l = QVBoxLayout(doc_bubble)
    doc_b_l.setContentsMargins(6, 6, 6, 6)
    doc_h = QLabel("👨‍⚕️ BS. Lê Văn Cường — 09:45 [Phản hồi lâm sàng]")
    doc_h.setStyleSheet("color: #4338ca; font-size: 10.5px; font-weight: bold;")
    doc_b = QLabel("Đã ghi nhận tình trạng cụ. Bác sĩ khuyên cho cụ nghỉ ngơi, uống đủ nước ấm và duy trì bài tập vừa sức.")
    doc_b.setStyleSheet("color: #1e1b4b; font-size: 11px;")
    doc_b_l.addWidget(doc_h)
    doc_b_l.addWidget(doc_b)
    chat_box.addWidget(doc_bubble)

    l3.addLayout(chat_box)

    chat_input_row = QHBoxLayout()
    chat_input = QLineEdit()
    chat_input.setPlaceholderText("Nhập tin nhắn / ý kiến phản hồi chuyên môn...")
    chat_input.setStyleSheet("padding: 6px; font-size: 11px; border: 1px solid #cbd5e1; border-radius: 4px;")
    btn_chat_send = QPushButton("💬 Gửi phản hồi")
    btn_chat_send.setStyleSheet("background-color: #4338ca; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 11px;")
    chat_input_row.addWidget(chat_input)
    chat_input_row.addWidget(btn_chat_send)
    l3.addLayout(chat_input_row)

    grid.addWidget(c3, 1, 0)

    # Card 4: Giám sát Phục hồi Mục 6A
    c4, l4 = create_card("4. GIÁM SÁT TUÂN THỦ PHỤC HỒI CHỨC NĂNG (MỤC 6A)", "#6d28d9")
    rehab_clin = QLabel(
        "• Bài tập kê toa: Nâng cánh tay (Arm Raise) | Giờ nhắc: 16:00\n"
        "• Chỉ tiêu snapshot: 10 lần | Đã xác nhận qua camera: 10/10 lần\n"
        "• Kết quả phiên: [camera_verified_completed - Hoàn thành có xác thực]\n"
        "• Camera độ tin cậy: 98.6% (Tỷ lệ khớp nhận diện: 99.1%)\n"
        "• Xử lý mất dấu: Chống đếm lặp, tự chuyển verification_unavailable khi che khuất"
    )
    rehab_clin.setStyleSheet("font-size: 11px; color: #4c1d95; background-color: #faf5ff; padding: 8px; border-radius: 4px;")
    l4.addWidget(rehab_clin)
    grid.addWidget(c4, 1, 1)

    right_content.addLayout(grid)
    two_col_layout.addLayout(right_content)

    main_layout.addLayout(two_col_layout)
    return w


def build_rehab_flow_6a() -> QWidget:
    w = QWidget()
    w.resize(1380, 950)
    w.setStyleSheet("background-color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif;")

    main_layout = QVBoxLayout(w)
    main_layout.setContentsMargins(24, 24, 24, 24)
    main_layout.setSpacing(16)

    # Title Banner
    header = QFrame()
    header.setStyleSheet("background-color: #581c87; border-radius: 8px; padding: 14px;")
    h_box = QVBoxLayout(header)
    t = QLabel("QUY TRÌNH PHỤC HỒI CHỨC NĂNG XÁC THỰC QUA CAMERA (MỤC 6A)")
    t.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
    sub = QLabel("Kiến trúc máy trạng thái FSM, Snapshot chỉ tiêu, Khóa chống đếm lặp và Xử lý mất quan sát")
    sub.setStyleSheet("color: #e9d5ff; font-size: 12px;")
    h_box.addWidget(t)
    h_box.addWidget(sub)
    main_layout.addWidget(header)

    # 4 Sequential Steps
    steps = [
        (
            "BƯỚC 1: LẬP LỊCH & CHỐT CHỈ TIÊU (SNAPSHOT)",
            "#3b82f6",
            [
                "• Lịch nhắc hằng ngày được kích hoạt đúng ~16:00 (múi giờ bệnh nhân Asia/Ho_Chi_Minh).",
                "• Chốt snapshot chỉ tiêu bài tập vào phiên: target_count_snapshot = 10.",
                "• Tính bất biến: Kể cả khi bác sĩ cập nhật phác đồ giữa phiên, chỉ tiêu phiên đang chạy không đổi.",
                "• Trạng thái ban đầu: SCHEDULED -> IN_PROGRESS khi camera phát hiện bệnh nhân."
            ]
        ),
        (
            "BƯỚC 2: AI PHÂN TÍCH CHUYỂN ĐỘNG & CHỐNG ĐẾM LẶP (IDEMPOTENCY)",
            "#8b5cf6",
            [
                "• Mô hình Pose MediaPipe trích xuất góc khớp (Vai, Khuỷu tay, Cổ tay).",
                "• FSM trạng thái động tác: DOWN (khởi đầu) -> MOVING_UP -> UP_HOLD -> DOWN (hoàn thành 1 rep).",
                "• Khóa chống đếm lặp (Idempotency Key): patient_001_rep_N_timestamp gắn cho mỗi rep.",
                "• Khung hình rung lắc hoặc lặp lại cùng một nhịp bị loại bỏ với nhãn duplicate_ignored = True."
            ]
        ),
        (
            "BƯỚC 3: CHUYỂN TRẠNG THÁI NGUYÊN TỬ & XỬ LÝ SỰ CỐ QUAN SÁT",
            "#10b981",
            [
                "• NHÁNH HOÀN THÀNH: Khi verified_count >= target_count_snapshot (10/10 reps):",
                "  -> Chuyển trạng thái nguyên tử sang 'camera_verified_completed'.",
                "• NHÁNH MẤT QUAN SÁT / CHE KHUẤT: Khi camera bị che hoặc bệnh nhân rời khung hình:",
                "  -> Chuyển trạng thái sang 'verification_unavailable'.",
                "  -> TUYỆT ĐỐI KHÔNG đánh dấu hoàn thành giả mạo!"
            ]
        ),
        (
            "BƯỚC 4: ĐỒNG BỘ DỮ LIỆU & BÁO CÁO CỔNG NGƯỜI NHÀ / BÁC SĨ",
            "#f59e0b",
            [
                "• Lưu trữ bền vững vào PostgreSQL/SQLite: bảng rehab_sessions và rehab_events.",
                "• Ghi nhận audit trail: actor = camera_ai, timestamp_utc, snapshot thông số.",
                "• Cổng Người nhà: Cập nhật tiến độ hoàn thành bài tập 16:00, huy hiệu xác thực camera.",
                "• Cổng Bác sĩ: Thống kê số lần tập đạt chuẩn, thời gian thực hiện, cảnh báo nếu gián đoạn."
            ]
        ),
    ]

    for title, color, points in steps:
        step_frame = QFrame()
        step_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #fafafa;
                border-left: 6px solid {color};
                border-top: 1px solid #e5e7eb;
                border-right: 1px solid #e5e7eb;
                border-bottom: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        s_layout = QVBoxLayout(step_frame)
        s_layout.setSpacing(6)

        s_title = QLabel(title)
        s_title.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px;")
        s_layout.addWidget(s_title)

        for pt in points:
            p_lbl = QLabel(pt)
            p_lbl.setStyleSheet("color: #374151; font-size: 11px;")
            s_layout.addWidget(p_lbl)

        main_layout.addWidget(step_frame)

    return w


def build_login_portal() -> QWidget:
    w = QWidget()
    w.resize(600, 720)
    w.setStyleSheet("background: radial-gradient(circle at 50% 20%, #1A3668 0%, #0D1C38 100%); font-family: 'Segoe UI', Arial, sans-serif;")

    main_layout = QVBoxLayout(w)
    main_layout.setContentsMargins(40, 40, 40, 40)
    main_layout.setAlignment(Qt.AlignCenter)

    card = QFrame()
    card.setStyleSheet("background-color: #ffffff; border-radius: 16px; padding: 24px; border: 1px solid #dfe8f3;")
    c_layout = QVBoxLayout(card)
    c_layout.setSpacing(12)

    # Brand
    icon_box = QHBoxLayout()
    icon_box.addStretch()
    lbl_icon = QLabel("🏥")
    lbl_icon.setStyleSheet("background-color: #1d5bb8; font-size: 26px; border-radius: 12px; padding: 8px 12px;")
    icon_box.addWidget(lbl_icon)
    icon_box.addStretch()
    c_layout.addLayout(icon_box)

    lbl_title = QLabel("HỆ THỐNG TRỢ LÝ Y TẾ TỪ XA")
    lbl_title.setAlignment(Qt.AlignCenter)
    lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
    c_layout.addWidget(lbl_title)

    lbl_sub = QLabel("Theo dõi Sinh hiệu, Nhắc thuốc & Phục hồi chức năng")
    lbl_sub.setAlignment(Qt.AlignCenter)
    lbl_sub.setStyleSheet("font-size: 11px; color: #64748b; margin-bottom: 8px;")
    c_layout.addWidget(lbl_sub)

    # Role Segmented Switcher (FPT style)
    switcher = QFrame()
    switcher.setStyleSheet("background-color: #e8eef5; border-radius: 20px; padding: 3px;")
    sw_layout = QHBoxLayout(switcher)
    sw_layout.setContentsMargins(4, 4, 4, 4)
    sw_layout.setSpacing(4)

    btn_care = QPushButton("👨‍👩‍👧 Người nhà & Gia đình")
    btn_care.setStyleSheet("background-color: #ffffff; color: #1d5bb8; font-weight: bold; border-radius: 16px; padding: 8px 14px; font-size: 12px; border: none;")
    btn_doc = QPushButton("👨‍⚕️ Bác sĩ điều trị")
    btn_doc.setStyleSheet("background-color: transparent; color: #64748b; font-weight: 500; border-radius: 16px; padding: 8px 14px; font-size: 12px; border: none;")
    sw_layout.addWidget(btn_care)
    sw_layout.addWidget(btn_doc)
    c_layout.addWidget(switcher)

    lbl_cap = QLabel("Đăng nhập dành cho Người nhà & Người chăm sóc bệnh nhân")
    lbl_cap.setAlignment(Qt.AlignCenter)
    lbl_cap.setStyleSheet("font-size: 11px; color: #64748b; font-style: italic;")
    c_layout.addWidget(lbl_cap)

    # Form Fields
    c_layout.addWidget(QLabel("Email hoặc Số điện thoại Người nhà"))
    inp_email = QLineEdit()
    inp_email.setPlaceholderText("Ví dụ: contact-a2e402b0@example.com")
    inp_email.setText("contact-a2e402b0@example.com")
    inp_email.setStyleSheet("padding: 8px; border: 1.5px solid #dfe8f3; border-radius: 6px; font-size: 12px;")
    c_layout.addWidget(inp_email)

    c_layout.addWidget(QLabel("Mật Khẩu"))
    inp_pw = QLineEdit()
    inp_pw.setEchoMode(QLineEdit.Password)
    inp_pw.setText("••••••••")
    inp_pw.setStyleSheet("padding: 8px; border: 1.5px solid #dfe8f3; border-radius: 6px; font-size: 12px;")
    c_layout.addWidget(inp_pw)

    btn_login = QPushButton("Đăng Nhập Cổng Người Nhà")
    btn_login.setStyleSheet("background-color: #1d5bb8; color: white; font-weight: bold; padding: 10px; border-radius: 8px; font-size: 13px; margin-top: 6px;")
    c_layout.addWidget(btn_login)

    # Caregiver Register Box
    reg_box = QFrame()
    reg_box.setStyleSheet("background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 10px;")
    rb_layout = QVBoxLayout(reg_box)
    lbl_reg_t = QLabel("Chưa có tài khoản Người nhà trong hệ thống?")
    lbl_reg_t.setAlignment(Qt.AlignCenter)
    lbl_reg_t.setStyleSheet("font-size: 11px; color: #334155;")
    lbl_reg_btn = QLabel("👉 Bấm vào đây để Đăng Ký Tài Khoản Mới")
    lbl_reg_btn.setAlignment(Qt.AlignCenter)
    lbl_reg_btn.setStyleSheet("font-size: 12px; font-weight: bold; color: #1d5bb8;")
    rb_layout.addWidget(lbl_reg_t)
    rb_layout.addWidget(lbl_reg_btn)
    c_layout.addWidget(reg_box)

    # Quick demo accounts
    lbl_q = QLabel("⚡ CHỌN NHANH TÀI KHOẢN NGƯỜI NHÀ DEMO:")
    lbl_q.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; margin-top: 6px;")
    c_layout.addWidget(lbl_q)

    btn_q1 = QPushButton("👨‍👩‍👦 Nguyễn Văn Tuấn (Chăm sóc Cụ Hoàng Anh)")
    btn_q1.setStyleSheet("background-color: #f1f5f9; text-align: left; padding: 6px 10px; border-radius: 6px; font-size: 11px;")
    c_layout.addWidget(btn_q1)

    btn_q2 = QPushButton("👩‍👧 Lê Thị Lan (Chăm sóc Cụ Mai Hương)")
    btn_q2.setStyleSheet("background-color: #f1f5f9; text-align: left; padding: 6px 10px; border-radius: 6px; font-size: 11px;")
    c_layout.addWidget(btn_q2)

    main_layout.addWidget(card)
    return w


def main():
    app = init_app()
    out_dir = Path("docs/screenshots")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Caregiver Portal
    cg = build_caregiver_portal()
    cg.show()
    app.processEvents()
    cg_path = out_dir / "caregiver_portal.png"
    cg.grab().save(str(cg_path))
    print(f"Saved: {cg_path}")

    # 2. Clinician Portal
    cl = build_clinician_portal()
    cl.show()
    app.processEvents()
    cl_path = out_dir / "clinician_portal.png"
    cl.grab().save(str(cl_path))
    print(f"Saved: {cl_path}")

    # 3. Rehab Flow 6A
    rf = build_rehab_flow_6a()
    rf.show()
    app.processEvents()
    rf_path = out_dir / "rehab_flow_6a.png"
    rf.grab().save(str(rf_path))
    print(f"Saved: {rf_path}")

    # 4. Login Portal
    lp = build_login_portal()
    lp.show()
    app.processEvents()
    lp_path = out_dir / "login_portal.png"
    lp.grab().save(str(lp_path))
    print(f"Saved: {lp_path}")


if __name__ == "__main__":
    main()


