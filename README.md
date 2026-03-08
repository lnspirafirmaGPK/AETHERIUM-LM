# AETHERIUM-LM

AETHERIUM-LM คือโปรเจกต์สำหรับทดลองระบบให้เหตุผล (reasoning) และการเชื่อมต่อ LLM แบบ asynchronous โดยมี 2 ส่วนหลัก:

- **Backend services (`app/`)** สำหรับจัดการค่าคอนฟิก LLM, การเข้าถึงฐานข้อมูล และ helper สำหรับเรียกใช้งานโมเดล
- **Reasoning engine (`cogitator_x/`)** สำหรับสร้างและประเมินเส้นทางความคิดด้วย MCTS + Process Reward Model

## โครงสร้างสำคัญ

- `app/config.py` — ค่าคอนฟิกระบบ (database URL, global LLM configs, API keys)
- `app/db.py` — SQLAlchemy models และ async session factory
- `app/services/llm_service.py` — ฟังก์ชัน validate LLM config, embeddings และการเลือก LLM ตาม search space
- `cogitator_x/` — แกนประมวลผล reasoning
- `tests/` — ชุดทดสอบหน่วยสำหรับ reasoning และ llm service

## การรันแบบเร็ว

1. ติดตั้ง dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. รันทดสอบ
   ```bash
   pytest -q
   ```

## หมายเหตุ

- ค่า `GLOBAL_LLM_CONFIGS` ใน `app/config.py` เป็นค่าเริ่มต้นสำหรับระบบและใช้รหัสติดลบเพื่อแยกจากค่าที่อยู่ในฐานข้อมูล
- ฝั่ง UI demo อยู่ใน `main.py` (Flet) เพื่อทดสอบ flow การโต้ตอบเบื้องต้น
