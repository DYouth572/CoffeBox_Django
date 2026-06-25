# Hướng Dẫn Chạy Dự Án Bằng Docker

Tài liệu này dùng để chạy dự án Django `vat_coffee_box` trên máy khác bằng Docker.

## Yêu Cầu

- Cài Docker Desktop hoặc Docker Engine.
- Máy nhận source code cần có toàn bộ thư mục dự án, gồm `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `manage.py`, `apps/`, `config/`, `static/`.
- Nếu muốn giữ dữ liệu hiện tại, gửi kèm `db.sqlite3` và thư mục `media/`.

## Chạy Nhanh

Mở terminal tại thư mục gốc dự án rồi chạy:

```bash
docker compose up --build
```

Sau khi container chạy xong, mở:

```text
http://127.0.0.1:8000/
```

Giao diện quản trị custom:

```text
http://127.0.0.1:8000/portal/
```

Django Admin mặc định:

```text
http://127.0.0.1:8000/admin/
```

## Tài Khoản Admin

Nếu `db.sqlite3` đã có sẵn tài khoản admin/staff thì đăng nhập bằng tài khoản đó.

Nếu chạy với database mới, tạo tài khoản admin bằng lệnh:

```bash
docker compose exec web python manage.py createsuperuser
```

Sau đó đăng nhập lại tại `/portal/` hoặc `/admin/`.

## Dữ Liệu Và Ảnh Upload

File `docker-compose.yml` đang mount:

```text
./data  -> /app/data
./media -> /app/media
```

Vì vậy:

- `data/db.sqlite3` giữ dữ liệu SQLite sau khi chạy Docker.
- `media/` giữ ảnh upload như avatar, box, sản phẩm.
- Nếu source có `db.sqlite3` ở thư mục gốc, container sẽ tự copy sang `data/db.sqlite3` trong lần chạy đầu.
- Khi gửi sang máy khác, gửi kèm `db.sqlite3` và `media/` nếu muốn giữ dữ liệu cũ.

## Lệnh Hay Dùng

Chạy nền:

```bash
docker compose up --build -d
```

Xem log:

```bash
docker compose logs -f web
```

Dừng container:

```bash
docker compose down
```

Chạy migrate thủ công:

```bash
docker compose exec web python manage.py migrate
```

Thu static thủ công:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

## Biến Môi Trường

Có thể chỉnh trong `docker-compose.yml`:

```yaml
DJANGO_DEBUG: "1"
DJANGO_SECRET_KEY: "doi-secret-key-khi-deploy"
DJANGO_ALLOWED_HOSTS: "localhost,127.0.0.1,ten-mien-cua-ban"
DJANGO_DB_NAME: "/app/data/db.sqlite3"
```

Khi deploy thật, nên đặt `DJANGO_DEBUG: "0"` và đổi `DJANGO_SECRET_KEY`.

## Ghi Chú

- Container tự chạy `migrate` và `collectstatic` khi khởi động.
- Cổng mặc định là `8000`.
- Nếu cổng `8000` đã bị dùng, đổi dòng `"8000:8000"` thành ví dụ `"8080:8000"`, rồi mở `http://127.0.0.1:8080/`.
