# Chỉnh sửa GitHub profile

Profile dùng cửa sổ terminal nền tối, ảnh avatar được vẽ bằng ký tự ASCII và bảng thông tin
lấy cảm hứng từ [ganji759/asciifetch](https://github.com/ganji759/asciifetch).
SVG được tạo bằng mã trong repository và Pillow; không cần API ảnh hay font tải từ mạng.
Đây là bộ dựng SVG tùy biến lấy cảm hứng từ asciifetch. Mỗi ký tự và màu sắc
được tính từ ảnh gốc `assets/avatar.jpg`, không dùng chữ thay thế cho ảnh.

## Đổi nội dung

1. Sửa `profile.json`: thông tin cá nhân, các dòng trong banner (`fields`),
   bảng kỹ năng (`stack`) và bảng màu (`palette`). Dòng `[]` tạo khoảng cách;
   nhãn rỗng `""` tiếp tục giá trị của dòng trước.
2. Chạy từ thư mục repository với Python 3.9 trở lên:

   ```sh
   python -m pip install -r requirements.txt
   python scripts/build_profile.py
   python scripts/build_profile.py --check
   ```

3. Commit cấu hình, ảnh nguồn, `README.md` và hai file SVG trong `assets/`, rồi
   push lên repository `Kaivin22/Kaivin22` để GitHub hiển thị bản mới.

Không sửa trực tiếp `README.md` hoặc SVG: lần build tiếp theo sẽ ghi đè.
Đổi bố cục trong `scripts/build_profile.py`.

## Đổi ảnh ASCII

Thay `assets/avatar.jpg` bằng ảnh mới rồi chạy lại lệnh build. Có thể dùng PNG
bằng cách đổi `portrait.src` trong `profile.json` và commit file ảnh tương ứng.
Ảnh sẽ được căn giữa và cắt vuông; nên chuẩn bị avatar vuông với chủ thể rõ nét.
Ảnh hiện tại là ảnh mèo cam cầm hoa do chủ profile cung cấp.

`portrait.columns` điều chỉnh độ chi tiết (40–120 cột; mặc định 80). Script
giữ đúng tỷ lệ hình khi chuyển sang ô ký tự, hỗ trợ hướng ảnh EXIF và nền trong suốt.
Cập nhật `portrait.description` nếu đổi chủ thể trong ảnh để văn bản thay thế vẫn đúng.
Ảnh nguồn được lưu trong repository để build trên máy và GitHub tạo cùng kết quả.

## Tự động cập nhật

Workflow `Build terminal profile` chạy khi ảnh nguồn, cấu hình, script hoặc dependencies thay đổi trên
`main`, hoặc khi được chạy thủ công trong tab Actions. Workflow build rồi commit
các file đầu ra nếu có thay đổi. Pull request chỉ kiểm tra bản build đã cập nhật.
Nếu repository chặn bot ghi vào `main`, chạy hai lệnh trên và commit thủ công.

Repository chỉ dùng workflow `Build terminal profile` và hai SVG được tạo từ
`profile.json` cùng ảnh nguồn. Workflow tự cài Pillow từ `requirements.txt`.

## Cấu trúc repository

```text
.github/
  CODEOWNERS
  workflows/profile.yml
assets/
  avatar.jpg
  profile-terminal.svg
  profile-terminal-mobile.svg
docs/PROFILE.md
scripts/build_profile.py
profile.json
requirements.txt
README.md
LICENSE
```

`CODEOWNERS` thuộc tài khoản `Kaivin22`. Toàn bộ thông tin hiển thị được cấu hình
trong `profile.json`; ảnh ASCII được tính từ ảnh nguồn trong `assets/`.

## Hiển thị

- `assets/profile-terminal.svg`: bản hai cột cho máy tính.
- `assets/profile-terminal-mobile.svg`: bản xếp dọc cho màn hình tối đa 640 px.
- README có văn bản thay thế, nội dung Markdown và bản text có thể mở rộng.
- SVG chỉ chứa hình học và chữ, không dùng script, `foreignObject`, ảnh hoặc
  font từ bên ngoài. Font monospace sẽ dùng font có sẵn trên thiết bị.

Màu terminal luôn tối ở cả giao diện sáng và tối của GitHub, theo mẫu tham khảo.
Tên, kỹ năng và liên kết lấy từ `profile.json`; profile không dùng thống kê bên ngoài.
