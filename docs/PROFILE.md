# Chỉnh sửa GitHub profile

Profile dùng cửa sổ terminal nền tối, monogram ASCII `K22` và bảng thông tin
lấy cảm hứng từ [ganji759/asciifetch](https://github.com/ganji759/asciifetch).
SVG được tạo bằng mã trong repository; không cần API ảnh, font tải từ mạng
hay cài thư viện Python. Đây là bản thiết kế tùy biến, không phải đầu ra của
công cụ chuyển ảnh chân dung asciifetch.

## Đổi nội dung

1. Sửa `profile.json`: thông tin cá nhân, các dòng trong banner (`fields`),
   bảng kỹ năng (`stack`) và bảng màu (`palette`). Dòng `[]` tạo khoảng cách;
   nhãn rỗng `""` tiếp tục giá trị của dòng trước.
2. Chạy từ thư mục repository với Python 3.9 trở lên:

   ```sh
   python scripts/build_profile.py
   python scripts/build_profile.py --check
   ```

3. Commit `profile.json`, `README.md` và hai file SVG trong `assets/`, rồi
   push lên repository `Kaivin22/Kaivin22` để GitHub hiển thị bản mới.

Không sửa trực tiếp `README.md` hoặc SVG: lần build tiếp theo sẽ ghi đè.
Đổi bố cục hoặc monogram trong `scripts/build_profile.py`.

## Tự động cập nhật

Workflow `Build terminal profile` chạy khi cấu hình hoặc script thay đổi trên
`main`, hoặc khi được chạy thủ công trong tab Actions. Workflow build rồi commit
các file đầu ra nếu có thay đổi. Pull request chỉ kiểm tra bản build đã cập nhật.
Nếu repository chặn bot ghi vào `main`, chạy hai lệnh trên và commit thủ công.

Repository chỉ dùng workflow `Build terminal profile` và hai SVG được tạo từ
`profile.json`. Không cần token của dịch vụ ảnh hay thư viện bên ngoài.

## Cấu trúc repository

```text
.github/
  CODEOWNERS
  workflows/profile.yml
assets/
  profile-terminal.svg
  profile-terminal-mobile.svg
docs/PROFILE.md
scripts/build_profile.py
profile.json
README.md
LICENSE
```

`CODEOWNERS` thuộc tài khoản `Kaivin22`. Toàn bộ thông tin hiển thị được cấu hình
trong `profile.json`; monogram ASCII `K22` nằm trong script dựng SVG.

## Hiển thị

- `assets/profile-terminal.svg`: bản hai cột cho máy tính.
- `assets/profile-terminal-mobile.svg`: bản xếp dọc cho màn hình tối đa 640 px.
- README có văn bản thay thế, nội dung Markdown và bản text có thể mở rộng.
- SVG chỉ chứa hình học và chữ, không dùng script, `foreignObject`, ảnh hoặc
  font từ bên ngoài. Font monospace sẽ dùng font có sẵn trên thiết bị.

Màu terminal luôn tối ở cả giao diện sáng và tối của GitHub, theo mẫu tham khảo.
Tên, kỹ năng và liên kết lấy từ `profile.json`; profile không dùng thống kê bên ngoài.
