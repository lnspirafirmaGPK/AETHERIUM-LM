import flet as ft
import asyncio
import os
import sys

# Ensure app is in path if running from root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import LLMConfig
from app.services.llm_service import validate_llm_config

async def main(page: ft.Page):
    page.title = "AETHERIUM LM - Mobile Console"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = "adaptive"

    # UI Components
    provider_dropdown = ft.Dropdown(
        label="Select Provider",
        options=[
            ft.dropdown.Option("OPENAI"),
            ft.dropdown.Option("ANTHROPIC"),
            ft.dropdown.Option("GOOGLE"),
            ft.dropdown.Option("GROQ"),
            ft.dropdown.Option("OLLAMA"),
        ],
        value="OPENAI",
    )

    model_input = ft.TextField(label="Model Name", value="gpt-4o")
    api_key_input = ft.TextField(label="API Key", password=True, can_reveal_password=True)
    status_text = ft.Text(size=16)
    progress_bar = ft.ProgressBar(visible=False)

    async def handle_validate(e):
        # แสดงสถานะกำลังทำงาน
        progress_bar.visible = True
        status_text.value = "กำลังเชื่อมต่อกับ AI..."
        status_text.color = ft.colors.BLUE_200
        page.update()

        # เรียกใช้ฟังก์ชันที่ปรับแก้ Signature แล้ว
        # validate_llm_config accepts (provider, model_name, api_key, api_base, custom_provider, litellm_params)
        success, msg = await validate_llm_config(
            provider=provider_dropdown.value,
            model_name=model_input.value,
            api_key=api_key_input.value
        )

        progress_bar.visible = False
        if success:
            status_text.value = "✅ การเชื่อมต่อสำเร็จ! พร้อมใช้งาน"
            status_text.color = ft.colors.GREEN_400
        else:
            status_text.value = f"❌ ล้มเหลว: {msg}"
            status_text.color = ft.colors.RED_400
        page.update()

    # จัดวาง Layout
    page.add(
        ft.Column([
            ft.Text("AETHERIUM LM", size=32, weight="bold", color=ft.colors.CYAN_ACCENT),
            ft.Text("Mobile Configuration Console", size=14, italic=True),
            ft.Divider(),
            provider_dropdown,
            model_input,
            api_key_input,
            ft.ElevatedButton(
                "Validate & Save Config",
                on_click=handle_validate,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
            ),
            progress_bar,
            status_text,
        ], spacing=20)
    )

if __name__ == "__main__":
    ft.app(target=main)
