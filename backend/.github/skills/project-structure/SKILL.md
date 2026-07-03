---
name: project-structure
description: 'Tạo hoặc review cấu trúc dự án FastAPI theo domain/bounded context. Dùng khi cần tổ chức src theo từng domain, tách router/schemas/models/service/dependencies/config, và kiểm soát cross-domain imports.'
argument-hint: 'Mô tả domain, bounded context, hoặc cấu trúc dự án bạn muốn tạo/review'
---

# Project Structure

Dùng skill này khi cần thiết kế hoặc review cấu trúc dự án theo domain thay vì theo file type. Mục tiêu là giữ mỗi bounded context trong một package riêng, tách rõ trách nhiệm và giữ import giữa các domain thật rõ ràng.

## Skill Này Tạo Ra Điều Gì

- Một đề xuất cấu trúc thư mục theo domain.
- Một bản tách lớp rõ ràng giữa router, schema, model, service, dependency và config.
- Quy tắc import giữa các domain để tránh coupling ngầm.
- Một checklist ngắn để kiểm tra xem cấu trúc đó có dễ mở rộng và dễ test hay không.

## Khi Nào Nên Dùng

- Bắt đầu một FastAPI backend mới.
- Thêm bounded context mới vào dự án hiện có.
- Review lại cách tổ chức code giữa nhiều domain.
- Chuẩn hóa cách đặt file như `router.py`, `schemas.py`, `service.py`, `dependencies.py`.
- Kiểm tra việc import chéo giữa các domain có bị rối hoặc ẩn phụ thuộc hay không.

## Quy Trình Ngắn

1. Xác định domain hoặc bounded context.
   Ví dụ: `auth/`, `posts/`, `notifications/`, `aws/`.

2. Tách phần dùng chung và phần theo domain.
   `config.py`, `database.py`, `models.py`, `exceptions.py` là phần global hoặc shared.

3. Xác định trách nhiệm của từng file trong domain.
   - `router.py`: API endpoints
   - `schemas.py`: Pydantic models
   - `models.py`: ORM models
   - `service.py`: business logic
   - `dependencies.py`: route dependencies
   - `config.py`: settings theo domain
   - `constants.py`: constants và error codes
   - `exceptions.py`: domain-specific exceptions
   - `utils.py`: helper functions

4. Kiểm tra hướng import.
   Cross-domain import phải dùng module rõ ràng, không import vòng hoặc import mơ hồ.

5. Review khả năng mở rộng.
   Nếu một domain phình ra, có thể thêm file con nhưng vẫn giữ một package cho bounded context.

6. Chốt lại cấu trúc tối thiểu nhưng đủ rõ.
   Ưu tiên cấu trúc dễ đọc, dễ test, và dễ tách trách nhiệm hơn là chia file quá sớm.

## Quy Tắc Thiết Kế

### Tổ Chức Theo Domain

- Ưu tiên package theo bounded context, không tổ chức theo loại file toàn cục.
- Mỗi domain là một package riêng dưới `src/`.
- Giữ các thành phần liên quan sát nhau trong cùng domain.

### Phân Ranh Trách Nhiệm

- Router chỉ nên lo HTTP layer.
- Schema chỉ nên lo dữ liệu vào/ra.
- Service chứa business logic.
- Dependencies chỉ lo cung cấp phụ thuộc cho route.
- Config và constants nên rõ ràng, không để logic nghiệp vụ lẫn vào.

### Cross-Domain Imports

- Luôn import rõ module, không dùng import mơ hồ.
- Không dùng `from src.auth import *`.
- Nên viết theo kiểu:

```python
from src.auth import constants as auth_constants
from src.notifications import service as notification_service
from src.posts.constants import ErrorCode as PostsErrorCode
```

### Shared vs Domain-Scoped

- Đưa phần dùng chung thật sự vào root-level modules như `src/config.py`, `src/database.py`, `src/models.py`, `src/exceptions.py`.
- Nếu logic chỉ dùng trong một bounded context, để nó trong package domain đó.

## Checklist Nhanh

1. Mỗi bounded context có một package riêng chưa?
2. Router, schema, model, service đã tách đúng vai trò chưa?
3. Có logic nghiệp vụ nào đang nằm sai layer không?
4. Import chéo giữa các domain có rõ ràng và nhất quán không?
5. Shared code có thật sự là shared code không?
6. Cấu trúc này có dễ test và dễ mở rộng không?

## Tiêu Chí Chất Lượng

- Cấu trúc dự án phản ánh domain thật, không phản ánh ngẫu nhiên theo file type.
- Trách nhiệm giữa các layer rõ ràng và không chồng chéo.
- Import chéo được kiểm soát và đọc là hiểu ngay.
- Shared code không bị lạm dụng.
- Mỗi domain có thể phát triển độc lập tương đối.

## Kết Quả Mong Đợi Khi Trả Lời

Khi dùng skill này, câu trả lời nên có:

1. Cấu trúc thư mục đề xuất.
2. Phân công trách nhiệm cho từng file.
3. Quy tắc import giữa các domain.
4. Điểm rủi ro nếu cấu trúc bị phình hoặc bị coupling.
5. Chỉ ra phần nào nên shared, phần nào nên để trong domain.

## Ví Dụ Prompt

- `/project-structure Tạo cấu trúc dự án FastAPI theo domain như mẫu này`
- `/project-structure Review xem cấu trúc src hiện tại có đúng bounded context không`
- `/project-structure Gợi ý cách tách auth, posts, notifications thành các package riêng`
- `/project-structure Kiểm tra cross-domain imports có đang bị mơ hồ không`