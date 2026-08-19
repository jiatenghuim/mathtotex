from tkinter import Tk

from mathlatex_app.app import MathLatexApp


def test_copy_button_keeps_direct_action_and_has_hover_formats() -> None:
    root = Tk()
    root.withdraw()
    try:
        app = MathLatexApp(root)
        labels = [
            app.copy_menu.entrycget(index, "label")
            for index in range(app.copy_menu.index("end") + 1)
        ]

        assert app.copy_button.cget("command")
        assert app.copy_button.bind("<Enter>")
        assert labels == [
            "复制原始内容",
            r"\ → \\ 转义反斜杠",
            "$...$ 行内公式",
            "$$...$$ 独立公式",
            r"\(...\) 行内公式",
            r"\[...\] 独立公式",
            "JSON 字符串",
        ]
    finally:
        root.destroy()
