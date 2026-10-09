# HỆ THỐNG KIỂM THỬ TỰ ĐỘNG GIFT TRÚC ANH 27
## E2E Opaque-Box Test Architecture & Quality Specification (TEST_INFRA)

- **Dự án:** Trúc Anh (Na) 27th Birthday Static Web Album & Certificate of Maturity Level 27
- **Vị trí tài liệu:** `/Users/HenryTran/Desktop/Henry/AntiGravity/06 - Linh Tinh/gift_trucanh_27/TEST_INFRA.md`
- **Phiên bản:** 1.0.0
- **Thời điểm thiết lập:** 2026-10-08
- **Đơn vị thiết kế:** E2E Testing Track (`test_writer_e2e`)
- **Mã kịch bản kiểm thử:** `/Users/HenryTran/Desktop/Henry/AntiGravity/06 - Linh Tinh/gift_trucanh_27/tests/run_all_tests.py`

---

## I. TRIẾT LÝ KIỂM THỬ (TESTING PHILOSOPHY)

Hệ thống kiểm thử này được thiết kế theo 4 nguyên tắc cốt lõi:

1. **Opaque-Box Testing (Kiểm thử hộp đục theo hợp đồng yêu cầu):**
   - Bộ test không can thiệp hay phụ thuộc vào chi tiết hiện thực nội bộ của code, mà thẩm định trực tiếp sản phẩm dựa trên **bản yêu cầu gốc** (`ORIGINAL_REQUEST.md`), **thiết kế dự án** (`PROJECT.md`) và **báo cáo khảo sát thực nghiệm** (`explorer_survey_1`, `explorer_survey_2`, `explorer_survey_3`).
   - Mọi tiêu chí đánh giá đều đo lường được một cách độc lập: sự tồn tại của file trên đĩa, định dạng chuẩn (JPEG, PNG, MP3), kích thước ảnh $\le 1600$px, tổng payload $< 15$ MB, DOM tree trong HTML, token màu Rose Gold trong CSS, API methods trong JavaScript, và các hành trình người dùng E2E.

2. **The Iron Law of TDD (Quy tắc Thép TDD & Vòng đời Red-Green-Refactor):**
   - Bộ test được kích hoạt ngay từ giai đoạn bắt đầu (Pha RED). Test báo FAIL một cách chính xác đối với các tính năng và module chưa được xây dựng (M2, M3, M4), đồng thời báo PASS ngay tức thì đối với các tài nguyên đã hoàn tất (M1).
   - Khi các worker hoàn thiện từng milestone, bộ test sẽ chuyển dần sang trạng thái GREEN mà không cần sửa đổi mã test.

3. **MBB Rigor & Zero Facade (Kỷ luật MBB & Nghiêm cấm ngụy tạo kết quả):**
   - Tuyệt đối không chấp nhận các bài test hình thức (facade tests) luôn pass mà không kiểm tra logic thực tế.
   - Kiểm tra định lượng nghiêm ngặt: đúng 37 ảnh, đúng 4 chương niên đại (2023: 15, 2024: 7, 2025: 11, 2026: 4), EXIF transposition cho ảnh chân dung, không broken links, và zero placeholder (`TODO`, `TBD`, `lorem ipsum`).

4. **Zero-Build Portability & Relative Paths (Tính khả chuyển & Đường dẫn tương đối):**
   - Toàn bộ ứng dụng web hoạt động độc lập không cần Node.js hay bundler.
   - 100% đường dẫn trong HTML, CSS, JS phải là đường dẫn tương đối (`./images/...`, `./audio/...`, `./css/...`, `./js/...`), không chứa đường dẫn tuyệt đối hệ điều hành (`/Users/...`) hay root-relative (`/images/...`).

---

## II. MA TRẬN ÁNH XẠ TÍNH NĂNG SANG CÁC TẦNG TEST (FEATURE-TO-TIER MATRIX)

Dựa trên bảng kiểm kê 20 tính năng trong `PROJECT.md`, hệ thống test được phân tầng thành 4 Tiers:

| STT | Mã Tính Năng | Tên Tính Năng | Milestone | Tầng Test | Phương Pháp Kiểm Chứng Tự Động |
|:---:|:---:|:---|:---:|:---:|:---|
| 01 | **F1** | HEIC to JPEG conversion | M1 | **Tier 1** | Kiểm tra `IMG_8326.jpg` tồn tại, định dạng JPEG, kích thước $\le 1600$px, dung lượng $> 10$ KB |
| 02 | **F2** | Image resizing & compression | M1 | **Tier 1, 2** | Kiểm tra đủ 37 ảnh tối ưu trong `images/`, max dimension $\le 1600$px, tổng dung lượng ảnh $< 12$ MB |
| 03 | **F3** | Chronological metadata manifest | M1 | **Tier 1** | Phân tích `js/gallery-data.js`, validate mảng 37 ảnh, 4 chương niên đại: 2023 (15), 2024 (7), 2025 (11), 2026 (4) |
| 04 | **F4** | Audio asset setup | M1 | **Tier 1** | Kiểm tra `audio/music.mp3` tồn tại, header MPEG/ID3 hợp lệ, dung lượng $\approx 2.79$ MB |
| 05 | **F5** | 2021 Certificate asset extraction | M1 | **Tier 1** | Kiểm tra `images/certificate_2021.png` tồn tại, header PNG hợp lệ, dung lượng $> 50$ KB |
| 06 | **F6** | Interactive Hero intro | M2 | **Tier 1** | Quét DOM trong `index.html`: `#hero`, hộp quà `#gift-box`/`envelope`, nút CTA mở quà |
| 07 | **F7** | User-gesture audio unlock & confetti | M2 | **Tier 1, 3** | Quét thẻ `<audio>`, canvas hạt starlight/confetti `#confetti`, và sự kiện click kích hoạt đồng thời |
| 08 | **F8** | Floating vinyl record player | M2 | **Tier 1, 3** | Quét markup đĩa than, cần kim, `@keyframes vinylSpin`, và trạng thái đồng bộ quay/dừng khi nghe nhạc |
| 09 | **F9** | 2021 Flashback section | M3 | **Tier 1** | Quét `#flashback-2021`, ảnh certificate 2021, trích dẫn lời hứa tuổi 22 của Henry, modal đọc thư |
| 10 | **F10** | Chronological memory timeline | M3 | **Tier 1** | Quét cấu trúc `#timeline`, trục thời gian phát sáng, 4 cột mốc năm 2023, 2024, 2025, 2026 |
| 11 | **F11** | Polaroid photo cards | M3 | **Tier 1** | Quét cấu trúc thẻ Polaroid, góc nghiêng so le (`rotate`), băng dính washi, `loading="lazy"` |
| 12 | **F12** | Full-Screen HD Lightbox | M3 | **Tier 1, 3** | Quét `#lightbox`, nút Next/Prev/Close, bộ đếm ảnh `X/37`, phím tắt bàn phím và API `open(index)` |
| 13 | **F13** | Luxury Certificate Level 27 | M4 | **Tier 1** | Quét `#certificate-level-27`, khung viền đôi Rose Gold, tên "Trúc Anh (Na)", danh hiệu Level 27 |
| 14 | **F14** | 3D Wax Seal | M4 | **Tier 1** | Quét con dấu sáp nổi đỏ ruby `.wax-seal`, khắc chữ "27th Birthday Official Seal" |
| 15 | **F15** | Digital signature | M4 | **Tier 1** | Quét chữ ký tay "Henry" và ngày ban hành "Sài Gòn, Ngày 17 tháng 9 năm 2026" |
| 16 | **F16** | Emotional 2026 Letter | M4 | **Tier 1** | Quét nội dung bức thư 2026 đầy cảm xúc vinh danh chặng đường 5 năm từ 22 lên 27 tuổi |
| 17 | **F17** | Celebration fireworks | M4 | **Tier 1, 3** | Quét `#fireworks-canvas`, engine `js/fireworks.js`, API kích hoạt pháo hoa ăn mừng |
| 18 | **F18** | Print & Save functionality | M4 | **Tier 1, 3** | Quét `@media print` trong CSS, nút bấm in, cơ chế ẩn thanh điều hướng và chỉ in chứng nhận A4 |
| 19 | **F19** | Responsive layout & mobile polish | M4 | **Tier 1, 2** | Quét `<meta name="viewport" ... viewport-fit=cover>`, media queries CSS, iOS safe area insets |
| 20 | **F20** | E2E test verification & hardening | M5 | **Tất cả Tiers** | Thực thi `tests/run_all_tests.py`, đạt 100% tỷ lệ pass trên toàn bộ 38 test cases |

---

## III. KIẾN TRÚC BỘ TEST 4 TẦNG (TEST ARCHITECTURE SPECIFICATION)

### 1. Tier 1: Feature Coverage (Độ Bao Phủ Từng Tính Năng Cô Lập) - 19 Tests
- Tập tin thực thi: `tests/test_tier1_features.py`
- Mục tiêu: Kiểm tra sự tồn tại và tính hợp chuẩn của từng thành phần giao diện, tài nguyên media và mã nguồn độc lập theo hợp đồng trong `PROJECT.md`.
- Các hàm kiểm thử:
  - `test_f01_heic_to_jpeg_conversion`
  - `test_f02_image_resizing_and_compression`
  - `test_f03_chronological_metadata_manifest`
  - `test_f04_audio_asset_setup`
  - `test_f05_certificate_2021_asset_extraction`
  - `test_f06_interactive_hero_intro`
  - `test_f07_audio_unlock_and_confetti`
  - `test_f08_floating_vinyl_record_player`
  - `test_f09_flashback_2021_section`
  - `test_f10_chronological_memory_timeline`
  - `test_f11_polaroid_photo_cards`
  - `test_f12_fullscreen_hd_lightbox`
  - `test_f13_luxury_certificate_level_27`
  - `test_f14_3d_wax_seal`
  - `test_f15_digital_signature`
  - `test_f16_emotional_2026_letter`
  - `test_f17_celebration_fireworks`
  - `test_f18_print_and_save_functionality`
  - `test_f19_responsive_layout_and_mobile_polish`

### 2. Tier 2: Boundary & Corner Cases (Ranh Giới, Ngoại Lệ & Kỷ Luật Số Liệu) - 10 Tests
- Tập tin thực thi: `tests/test_tier2_boundaries.py`
- Mục tiêu: Kiểm soát các giới hạn kỹ thuật khắt khe, ngăn ngừa lỗi góc chết (edge cases) và kiểm tra bảo vệ chất lượng.
- Các hàm kiểm thử:
  - `test_total_payload_budget_under_15mb`: Tổng dung lượng tải toàn trang (37 ảnh + audio + mã nguồn) nghiêm ngặt $< 15$ MB (15,728,640 bytes).
  - `test_code_payload_lightweight`: Toàn bộ mã HTML + CSS + JS $< 120$ KB nhằm đảm bảo tốc độ tải tức thì.
  - `test_special_character_filename_mg_2223_1`: Tên file gốc `_MG_2223 (1).JPG` có dấu cách và ngoặc đơn được xử lý an toàn, không bị lỗi mã hóa URL.
  - `test_uuid_filename_instagram_photo`: Tên file UUID `A51AE22D...` từ Instagram được bảo tồn toàn vẹn.
  - `test_exif_orientation_transpose`: Ảnh chụp dọc trên iPhone (EXIF orientation = 6 như `IMG_4385`, `IMG_6484`, `IMG_7825`) được xoay đúng chuẩn chiều cao > chiều rộng.
  - `test_audio_loop_and_preload_attributes`: Thẻ `<audio>` có thuộc tính `loop` và `preload="auto"` để phát nhạc lặp lại liền mạch.
  - `test_all_relative_paths`: 100% đường dẫn trong HTML và CSS là đường dẫn tương đối, không có `/Users/...` hay đường dẫn gốc `/`.
  - `test_zero_broken_links_audit`: Trích xuất toàn bộ `src`, `href`, `url(...)`, xác minh 100% file đều tồn tại trên đĩa.
  - `test_zero_placeholder_integrity`: 0 lần xuất hiện của các từ khóa cẩu thả: `TODO`, `TBD`, `FIXME`, `lorem ipsum`, `placeholder.com`.
  - `test_mobile_safe_area_insets`: CSS hỗ trợ iOS safe area insets (`env(safe-area-inset-top/bottom)`).

### 3. Tier 3: Cross-Feature Interactions (Tương Tác & Tích Hợp Đa Thành Phần) - 6 Tests
- Tập tin thực thi: `tests/test_tier3_interactions.py`
- Mục tiêu: Xác thực việc truyền tín hiệu và đồng bộ hóa trạng thái giữa các thành phần frontend.
- Các hàm kiểm thử:
  - `test_hero_cta_triggers_audio_and_particles`: Nút bấm mở quà kích hoạt phát nhạc đồng bộ với hiệu ứng pháo hoa giấy trên canvas trong ngữ cảnh cử chỉ người dùng.
  - `test_polaroid_card_opens_lightbox_with_index`: Thao tác bấm vào thẻ ảnh Polaroid truyền chính xác chỉ số ảnh (index) vào `window.lightbox.open(index)`.
  - `test_lightbox_keyboard_shortcuts_wiring`: Lightbox lắng nghe sự kiện bàn phím: Mũi tên phải (Next), Mũi tên trái (Prev), Escape (Đóng).
  - `test_audio_controller_and_vinyl_sync`: Trình điều khiển âm thanh đồng bộ trực quan đĩa than: nhạc phát thì đĩa xoay và cần kim hạ; nhạc dừng thì đĩa ngừng xoay.
  - `test_certificate_print_stylesheet_isolation`: Định dạng `@media print` ẩn toàn bộ giao diện web (Hero, Timeline, Lightbox, Vinyl player) và chỉ giữ lại Chứng nhận Tốt nghiệp Trưởng thành Level 27.
  - `test_fireworks_engine_interface`: Module `fireworks.js` xuất API kích hoạt `window.fireworks.launch()` sẵn sàng được gọi.

### 4. Tier 4: Real-World Application Scenarios (Hành Trình Trải Nghiệm Người Dùng Thực Tế) - 3 Tests
- Tập tin thực thi: `tests/test_tier4_scenarios.py`
- Mục tiêu: Mô phỏng toàn bộ trải nghiệm từ đầu đến cuối của Trúc Anh khi nhận quà sinh nhật.
- Các kịch bản:
  - `test_scenario_1_birthday_surprise_discovery`: Mở trang $\rightarrow$ Khám phá hộp quà $\rightarrow$ Nhạc vang lên $\rightarrow$ Pháo hoa giấy bay $\rightarrow$ Đĩa than xoay $\rightarrow$ Cuộn tới Hồi ức 2021.
  - `test_scenario_2_memory_lane_timeline_and_lightbox`: Duyệt 4 chương niên đại $\rightarrow$ Hiển thị 37 bức ảnh Polaroid $\rightarrow$ Mở Lightbox $\rightarrow$ Điều hướng ảnh kế tiếp / ảnh trước $\rightarrow$ Không một liên kết ảnh nào bị lỗi 404.
  - `test_scenario_3_grand_certificate_ceremony_and_print`: Chạm mốc Chứng nhận Trưởng thành Level 27 $\rightarrow$ Chiêm ngưỡng viền Rose Gold & Con dấu sáp 3D $\rightarrow$ Đọc chữ ký & Thư cảm xúc 2026 $\rightarrow$ Kích hoạt pháo hoa chúc mừng $\rightarrow$ Sẵn sàng in/lưu PDF A4.

---

## IV. CƠ CHẾ BÁO CÁO & NGƯỠNG CHẤP NHẬN (QUALITY GATES)

### 1. Lệnh thực thi kiểm thử
```bash
# Thực thi toàn bộ bộ test với báo cáo trực quan
python3 tests/run_all_tests.py

# Thực thi qua cơ chế discovery chuẩn của Python
python3 -m unittest discover tests

# Chạy riêng từng Tier
python3 tests/run_all_tests.py --tier 1
python3 tests/run_all_tests.py --tier 2
python3 tests/run_all_tests.py --tier 3
python3 tests/run_all_tests.py --tier 4
```

### 2. Tiêu chuẩn bàn giao (Pass Threshold)
- **Giai đoạn M1 (Hiện tại - Baseline):** 11/38 tests PASS (các tài nguyên ảnh, audio, metadata đã hoàn thành; 27 tests còn lại báo FAIL một cách sạch sẽ, đúng chuẩn TDD RED phase).
- **Giai đoạn M5 (Hoàn thành dự án):** **38/38 tests (100%) PHẢI PASS**. Exit code của runner trả về `0`.

---
*Tài liệu được ban hành chính thức bởi E2E Testing Track (`test_writer_e2e`).*
