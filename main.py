
import flet as ft
import asyncio

# =============================================================================
# ChatMessage Control
# =============================================================================

class ChatMessage(ft.Row):
    """A control representing a single chat message."""
    def __init__(self, message: str, user_name: str, message_type: str):
        super().__init__()
        self.vertical_alignment = "start"
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(user_name),
            ),
            ft.Column(
                [
                    ft.Text(user_name, weight="bold"),
                    ft.Text(message, selectable=True, width=400, overflow="auto"),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize() if user_name else ""

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER, ft.colors.BLUE, ft.colors.BROWN, ft.colors.CYAN,
            ft.colors.GREEN, ft.colors.INDIGO, ft.colors.LIME, ft.colors.ORANGE,
            ft.colors.PINK, ft.colors.PURPLE, ft.colors.RED, ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

# =============================================================================
# Main App Function
# =============================================================================

async def main(page: ft.Page):
    """Main function to build the Flet chat application."""
    page.title = "AETHERIUM - Chat"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = "stretch"
    page.vertical_alignment = "start"
    page.padding = 20

    # --- File Picker Logic ---
    async def handle_file_picker_result(e: ft.FilePickerResultEvent):
        if not e.files:
            return

        file_name = e.files[0].name
        chat_view.controls.append(ChatMessage(f"File attached: {file_name}", "You", "user"))
        await page.update_async()

        bot_response_placeholder = ChatMessage("...", "Aetherium Bot", "bot")
        chat_view.controls.append(bot_response_placeholder)
        await page.update_async()

        await asyncio.sleep(1.5)
        bot_response_placeholder.controls[1].controls[1].value = f"I have received your file: \"{file_name}\"."
        await page.update_async()

    file_picker = ft.FilePicker(on_result=handle_file_picker_result)
    page.overlay.append(file_picker)

    # --- Chat UI Components ---
    chat_view = ft.ListView(
        expand=True, spacing=15, auto_scroll=True, divider_thickness=0,
    )

    new_message_field = ft.TextField(
        hint_text="Type a message...",
        autofocus=True,
        expand=True,
        border_color=ft.colors.WHITE24,
        border_radius=10,
        on_submit=lambda e: send_message_click(e),
    )

    # --- Send Message Logic ---
    async def send_message_click(e):
        user_message = new_message_field.value
        if not user_message:
            return

        chat_view.controls.append(ChatMessage(user_message, "You", "user"))
        new_message_field.value = ""
        await page.update_async()

        bot_response_placeholder = ChatMessage("...", "Aetherium Bot", "bot")
        chat_view.controls.append(bot_response_placeholder)
        await page.update_async()

        await asyncio.sleep(1.5)
        bot_response_placeholder.controls[1].controls[1].value = f"This is a simulated response to: \"{user_message}\""
        await page.update_async()

    # --- Page Layout ---
    page.add(
        ft.Container(
            content=chat_view,
            border=ft.border.all(1, ft.colors.WHITE24),
            border_radius=15,
            padding=15,
            expand=True,
        ),
        ft.Row(
            controls=[
                new_message_field,
                ft.IconButton(
                    icon=ft.icons.ATTACH_FILE_ROUNDED,
                    tooltip="Attach a file",
                    on_click=lambda _: file_picker.pick_files(allow_multiple=False),
                    icon_color=ft.colors.CYAN_ACCENT,
                ),
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                    icon_color=ft.colors.CYAN_ACCENT,
                ),
            ],
            vertical_alignment="center",
        ),
    )
    await page.update_async()

# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    ft.run(target=main)
