# BỘ KIỂM THỬ SẴN SÀNG: GIFT TRÚC ANH 27
## Test Ready Specification & Execution Runbook (TEST_READY)

- **Dự án:** Trúc Anh (Na) 27th Birthday Web Album & Certificate of Maturity Level 27
- **Vị trí tài liệu:** `/Users/HenryTran/Desktop/Henry/AntiGravity/06 - Linh Tinh/gift_trucanh_27/TEST_READY.md`
- **Thời điểm công bố:** 2026-10-08T16:09:00Z
- **Đơn vị phát hành:** E2E Testing Track (`test_writer_e2e`)
- **Tập tin kịch bản kiểm thử:** `/Users/HenryTran/Desktop/Henry/AntiGravity/06 - Linh Tinh/gift_trucanh_27/tests/run_all_tests.py`

---

## 1. LỆNH THỰC THI KIỂM THỬ (TEST RUNNER COMMANDS)

### Lệnh chạy mặc định (Báo cáo trực quan theo từng Tier):
```bash
python3 /Users/HenryTran/Desktop/Henry/AntiGravity/06\ -\ Linh\ Tinh/gift_trucanh_27/tests/run_all_tests.py
```
*Hoặc thực thi từ thư mục dự án `gift_trucanh_27`:*
```bash
python3 tests/run_all_tests.py
```

### Lệnh chạy qua Unittest Standard Discovery:
```bash
python3 -m unittest discover tests
```

### Lệnh chạy theo từng Tier riêng biệt:
```bash
python3 tests/run_all_tests.py --tier 1   # Chỉ kiểm tra Feature Coverage
python3 tests/run_all_tests.py --tier 2   # Chỉ kiểm tra Boundaries & Limits
python3 tests/run_all_tests.py --tier 3   # Chỉ kiểm tra Cross-Feature Interactions
python3 tests/run_all_tests.py --tier 4   # Chỉ kiểm tra E2E User Journeys
```

---

## 2. BẢNG PHÂN TẦNG KIỂM THỬ (TIER BREAKDOWN)

Bộ kiểm thử bao gồm **38 test cases tự động độc lập**, được thiết kế theo phương pháp hộp đục (opaque-box testing):

| Tier | Tên Tầng Kiểm Thử | Số Test Cases | Trọng Tâm Khảo Sát | Trạng Thái Baseline (Pha RED) |
| :---:|:---|:---:|:---|:---:|
| **Tier 1** | **Feature Coverage** | 19 | Kiểm tra từng tính năng từ F1 đến F19: 37 ảnh, HEIC, MP3, 2021 cert, Hero, Vinyl, Timeline, Polaroid, Lightbox, Cert 27, Wax seal, Chữ ký, Thư 2026, Pháo hoa, Print CSS, Responsive | 5 PASS, 14 FAIL (Chờ M2 - M4) |
| **Tier 2** | **Boundary & Corner Cases** | 10 | Giới hạn payload $< 15$ MB, mã nguồn $< 120$ KB, file đặc biệt `_MG_2223 (1)` & UUID Instagram, EXIF transposition, audio loop/preload, đường dẫn tương đối, zero broken links, zero placeholders, iOS safe areas | 6 PASS, 4 FAIL (Chờ M2 - M4) |
| **Tier 3** | **Cross-Feature Interactions** | 6 | Tích hợp Hero click $\leftrightarrow$ Audio & Confetti, Polaroid click $\leftrightarrow$ Lightbox open(index), Lightbox phím tắt (Next/Prev/Esc), Audio state $\leftrightarrow$ Vinyl spinning, `@media print` cách ly giao diện, Pháo hoa API | 0 PASS, 6 FAIL (Chờ M2 - M4) |
| **Tier 4** | **Real-World Scenarios** | 3 | Kịch bản 1 (Mở hộp quà sinh nhật & nghe nhạc); Kịch bản 2 (Duyệt dòng thời gian 37 ảnh & xem Lightbox HD); Kịch bản 3 (Chứng nhận Trưởng thành Level 27, con dấu sáp, đọc thư & in A4) | 0 PASS, 3 FAIL (Chờ M2 - M4) |
| **TỔNG** | **Toàn Bộ Test Suite** | **38 tests** | **Bảo chứng chất lượng toàn diện trước khi bàn giao cho Henry** | **11 PASS / 27 FAIL (Sẵn sàng kích hoạt)** |

---

## 3. BẢNG CHECKLIST CHI TIẾT TỪNG TEST CASE (TEST CHECKLIST)

### 📌 Tier 1: Feature Coverage (19 Tests)
- [x] `test_f01_heic_to_jpeg_conversion`: Xác nhận `IMG_8326.HEIC` đã convert sang `images/IMG_8326.jpg` chuẩn JPEG, $\le 1600$px.
- [x] `test_f02_image_resizing_and_compression`: Xác nhận đủ 37 ảnh tối ưu trong `images/`, max dimension $\le 1600$px, tổng dung lượng ảnh $< 12$ MB.
- [x] `test_f03_chronological_metadata_manifest`: Xác nhận `js/gallery-data.js` khai báo đủ 37 ảnh trong 4 chương (2023: 15, 2024: 7, 2025: 11, 2026: 4).
- [x] `test_f04_audio_asset_setup`: Xác nhận `audio/music.mp3` tồn tại, định dạng MP3 stereo 128kbps, dung lượng $\approx 2.79$ MB.
- [x] `test_f05_certificate_2021_asset_extraction`: Xác nhận `images/certificate_2021.png` đã trích xuất từ PDF gốc, dung lượng $> 50$ KB.
- [ ] `test_f06_interactive_hero_intro`: Kiểm tra `#hero`, hộp quà `#gift-box`, và nút CTA mở quà trong `index.html`.
- [ ] `test_f07_audio_unlock_and_confetti`: Kiểm tra thẻ `<audio>`, canvas `#confetti`, và sự kiện click kích hoạt đồng thời.
- [ ] `test_f08_floating_vinyl_record_player`: Kiểm tra đĩa than xoay, cần kim và `@keyframes vinylSpin` trong CSS.
- [ ] `test_f09_flashback_2021_section`: Kiểm tra `#flashback-2021`, ảnh certificate 2021, và trích dẫn lời hứa tuổi 22 của Henry.
- [ ] `test_f10_chronological_memory_timeline`: Kiểm tra `#timeline` và 4 mốc năm 2023, 2024, 2025, 2026.
- [ ] `test_f11_polaroid_photo_cards`: Kiểm tra thẻ Polaroid nghiêng tự nhiên, washi tape, và thuộc tính `loading="lazy"`.
- [ ] `test_f12_fullscreen_hd_lightbox`: Kiểm tra `#lightbox`, nút Next/Prev/Close, bộ đếm ảnh `X/37`, và file `js/lightbox.js`.
- [ ] `test_f13_luxury_certificate_level_27`: Kiểm tra `#certificate-level-27`, viền Rose Gold, tên "Trúc Anh (Na)", và danh hiệu Level 27.
- [ ] `test_f14_3d_wax_seal`: Kiểm tra con dấu sáp nổi đỏ ruby `.wax-seal` và dòng chữ "27th Birthday Official Seal".
- [ ] `test_f15_digital_signature`: Kiểm tra chữ ký số "Henry" và ngày ban hành "17 tháng 9 năm 2026".
- [ ] `test_f16_emotional_2026_letter`: Kiểm tra bức thư cảm xúc 2026 tri ân hành trình 5 năm từ tuổi 22 lên 27.
- [ ] `test_f17_celebration_fireworks`: Kiểm tra canvas pháo hoa và engine `js/fireworks.js`.
- [ ] `test_f18_print_and_save_functionality`: Kiểm tra `@media print` trong CSS và nút kích hoạt in ấn.
- [ ] `test_f19_responsive_layout_and_mobile_polish`: Kiểm tra viewport meta tag `viewport-fit=cover` và media queries responsive.

### 📌 Tier 2: Boundary & Corner Cases (10 Tests)
- [x] `test_total_payload_budget_under_15mb`: Tổng dung lượng thực tế trên đĩa (14.63 MB) và tải web (14.49 MB) thỏa mãn $< 15$ MB.
- [x] `test_code_payload_lightweight`: Dung lượng mã nguồn nhẹ nhàng, đáp ứng chuẩn $< 120$ KB.
- [x] `test_special_character_filename_mg_2223_1`: Tên file `_MG_2223 (1)` được chuẩn hóa sạch sẽ thành `MG_2223_1.jpg`.
- [x] `test_uuid_filename_instagram_photo`: Tên file UUID `A51AE22D...` từ Instagram bảo tồn nguyên vẹn.
- [x] `test_exif_orientation_transpose`: Ảnh chân dung iPhone chụp dọc được xoay chuẩn (chiều cao > chiều rộng).
- [x] `test_zero_placeholder_integrity`: Mã nguồn không chứa placeholder rác (`TODO`, `TBD`, `lorem ipsum`).
- [ ] `test_audio_loop_and_preload_attributes`: Kiểm tra thẻ `<audio>` có `loop` và `preload="auto"`.
- [ ] `test_all_relative_paths`: Kiểm tra 100% đường dẫn trong HTML và CSS là đường dẫn tương đối.
- [ ] `test_zero_broken_links_audit`: Kiểm tra 100% tài nguyên được tham chiếu trong HTML/CSS đều tồn tại trên đĩa.
- [ ] `test_mobile_safe_area_insets`: Kiểm tra CSS hỗ trợ `env(safe-area-inset-top/bottom)` cho iPhone.

### 📌 Tier 3: Cross-Feature Interactions (6 Tests)
- [ ] `test_hero_cta_triggers_audio_and_particles`: Nút bấm Hero gọi đồng thời `audioController.play()` và hiệu ứng confetti.
- [ ] `test_polaroid_card_opens_lightbox_with_index`: Thao tác click thẻ Polaroid mở Lightbox đúng chỉ số ảnh.
- [ ] `test_lightbox_keyboard_shortcuts_wiring`: Lightbox xử lý phím `ArrowRight`, `ArrowLeft`, `Escape`.
- [ ] `test_audio_controller_and_vinyl_sync`: Trình nghe nhạc đồng bộ trạng thái xoay đĩa than khi play/pause.
- [ ] `test_certificate_print_stylesheet_isolation`: Chế độ in `@media print` ẩn sạch toàn bộ web chrome và chỉ in Chứng nhận.
- [ ] `test_fireworks_engine_interface`: Module `fireworks.js` xuất API `window.fireworks.launch()` sẵn sàng hoạt động.

### 📌 Tier 4: Real-World Scenarios (3 Tests)
- [ ] `test_scenario_1_birthday_surprise_discovery`: Mô phỏng quy trình mở hộp quà, bung pháo hoa, phát nhạc và dẫn vào hồi ức.
- [ ] `test_scenario_2_memory_lane_timeline_and_lightbox`: Mô phỏng duyệt trọn vẹn 37 bức ảnh và tương tác Lightbox HD không lỗi.
- [ ] `test_scenario_3_grand_certificate_ceremony_and_print`: Mô phỏng chiêm ngưỡng Chứng nhận Level 27, con dấu sáp, đọc thư và in ấn A4.

---

## 4. KẾT QUẢ THỰC THI BASELINE (BASELINE RESULTS)

Kết quả đo đạc thực tế tại thời điểm khởi tạo hệ thống kiểm thử:

```text
========================================================================
                       TEST EXECUTION SUMMARY
========================================================================
Tier                                          | Total  | Pass   | Fail   | Error  | Rate   
------------------------------------------------------------------------------------
Tier 1: Feature Coverage (Unit / Isolation)   | 19     | 5      | 14     | 0      |  26.3%
Tier 2: Boundary & Corner Cases               | 10     | 6      | 4      | 0      |  60.0%
Tier 3: Cross-Feature Interactions            | 6      | 0      | 6      | 0      |   0.0%
Tier 4: Real-World Scenarios (End-to-End)     | 3      | 0      | 3      | 0      |   0.0%
------------------------------------------------------------------------------------
OVERALL TOTALS                                | 38     | 11     | 27     | 0      |  28.9%
Total Execution Time: 0.040s
========================================================================

[STATUS] TDD RED PHASE: 27 test(s) failing (Waiting for worker milestones).
```

### Đánh giá chất lượng:
- **Tốc độ thực thi:** 0.040 giây (siêu nhanh, không phụ thuộc internet hay npm).
- **Tính ổn định:** 0 lỗi cú pháp (`0 errors`).
- **Phản ánh tiến độ chuẩn mực:** Các tính năng media pipeline của Milestone 1 (M1) đã vượt qua 11 bài kiểm tra (28.9%). Các tính năng giao diện còn lại của M2, M3, M4 đang ở trạng thái RED chờ các worker hiện thực.

---
*Xác nhận ban hành: E2E Testing Track (`test_writer_e2e`). Sẵn sàng cho các worker chạy test liên tục trong quá trình triển khai!*
