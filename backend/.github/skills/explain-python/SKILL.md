---
name: explain-python
description: 'Giải thích Python bằng tiếng Việt. Dùng khi cần giải thích code Python, cú pháp, kiểu dữ liệu, async, class, lỗi runtime, traceback, hoặc cách một đoạn mã hoạt động.'
argument-hint: 'Mô tả đoạn code, khái niệm, lỗi, hoặc câu hỏi Python cần giải thích'
---

# Explain Python

Dùng skill này khi cần giải thích Python rõ ràng, có cấu trúc, và bằng tiếng Việt. Mục tiêu là giúp người đọc hiểu một đoạn code, một khái niệm, hoặc một lỗi Python theo mức độ từ tổng quan đến chi tiết, thay vì chỉ dịch từng dòng mã.

## Skill Này Tạo Ra Điều Gì

- Một lời giải thích bằng tiếng Việt cho code hoặc khái niệm Python.
- Phần mô tả ý nghĩa tổng thể trước, rồi mới đi vào cơ chế hoạt động chi tiết.
- Giải thích nguyên nhân lỗi, luồng dữ liệu, và các điểm dễ nhầm nếu người dùng đang debug.
- Ví dụ ngắn hoặc diễn giải lại bằng ngôn ngữ đơn giản khi cần.

## Khi Nào Nên Dùng

- Cần giải thích một file Python, một hàm, một class, hoặc một đoạn code ngắn.
- Cần giải thích cú pháp Python như `async/await`, list comprehension, decorator, context manager, generator, hoặc type hints.
- Cần giải thích traceback, exception, hoặc lỗi validation/runtime.
- Cần mô tả sự khác nhau giữa hai cách viết Python.
- Cần giải thích code trong repo cho người đọc nói tiếng Việt.

## Quy Trình

1. Xác định đúng đối tượng cần giải thích.
   Bắt đầu từ file, hàm, class, lỗi, hoặc khái niệm Python mà người dùng nêu ra.

2. Đọc phần code quyết định hành vi.
   Ưu tiên đọc đúng hàm hoặc khối lệnh liên quan trực tiếp thay vì lan rộng sang cả codebase.

3. Xác định mục tiêu của đoạn code.
   Trả lời trước: đoạn này đang cố làm gì, đầu vào là gì, đầu ra là gì, và nó phụ thuộc vào phần nào khác.

4. Giải thích theo thứ tự dễ hiểu.
   Trình bày theo hướng:
   - bức tranh tổng thể
   - luồng chạy chính
   - từng dòng hoặc từng khối quan trọng
   - điểm dễ sai hoặc dễ nhầm

5. Điều chỉnh độ sâu theo yêu cầu.
   - Nếu người dùng hỏi nhanh, trả lời ngắn gọn.
   - Nếu người dùng đang học, giải thích thuật ngữ và thêm ví dụ.
   - Nếu người dùng đang debug, nhấn mạnh nguyên nhân lỗi, điều kiện kích hoạt, và cách kiểm tra.

6. Kết thúc bằng phần chốt hữu ích.
   Tóm tắt lại ý chính, và nếu phù hợp thì gợi ý cách đọc tiếp hoặc cách kiểm chứng hiểu đúng đoạn code.

## Điểm Quyết Định

### Giải Thích Khái Niệm Hay Giải Thích Code

- Nếu người dùng hỏi về một khái niệm như `asyncio`, `dataclass`, hoặc `__init__`, bắt đầu bằng định nghĩa ngắn rồi mới đưa ví dụ.
- Nếu người dùng đưa một đoạn code cụ thể, bắt đầu bằng vai trò của đoạn code đó trong ngữ cảnh hiện tại.

### Mức Độ Chi Tiết

- Với người mới học, tránh giả định nền tảng quá cao; giải thích thuật ngữ ngay khi dùng.
- Với câu hỏi kỹ thuật sâu, giữ câu trả lời chặt chẽ, chính xác, và bám sát hành vi runtime.

### Khi Có Lỗi Hoặc Traceback

- Nêu lỗi xảy ra ở đâu.
- Giải thích vì sao Python sinh ra lỗi đó.
- Chỉ ra dữ liệu hoặc điều kiện nào dẫn tới lỗi.
- Nếu có thể, đưa cách tự kiểm tra hoặc cách sửa hợp lý.

## Tiêu Chí Chất Lượng

- Câu trả lời viết bằng tiếng Việt tự nhiên, không chỉ dịch sát chữ.
- Giải thích đúng hành vi Python, không suy đoán khi chưa đọc đủ code liên quan.
- Đi từ tổng quan đến chi tiết, thay vì chú thích từng dòng ngay từ đầu.
- Phân biệt rõ đâu là cơ chế Python, đâu là logic riêng của codebase.
- Nếu có lỗi, phải nói rõ nguyên nhân và tác động, không chỉ nêu triệu chứng.

## Mẫu Cấu Trúc Trả Lời

Ưu tiên cấu trúc sau khi phù hợp:

1. Đoạn code hoặc khái niệm này dùng để làm gì.
2. Nó hoạt động như thế nào.
3. Các dòng hoặc khối quan trọng cần chú ý.
4. Điểm dễ nhầm hoặc lỗi thường gặp.
5. Tóm tắt ngắn gọn.

## Ví Dụ Prompt

- `/explain-python Giải thích hàm này bằng tiếng Việt`
- `/explain-python Giải thích `async def` hoạt động như thế nào`
- `/explain-python Phân tích traceback Python này và giải thích nguyên nhân`
- `/explain-python Giải thích file backend này cho người mới học Python`