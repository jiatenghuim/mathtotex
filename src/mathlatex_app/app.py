"""Tkinter desktop interface for MathLaTeX."""

from __future__ import annotations

import queue
import sys
import threading
from pathlib import Path
from tkinter import BooleanVar, Canvas, StringVar, Text, Tk, Toplevel, filedialog, messagebox, ttk

from PIL import Image, ImageGrab, ImageTk

from .pipeline import MathLatexPipeline


class SelectionOverlay:
    def __init__(self, parent: Tk, screenshot: Image.Image, callback) -> None:
        self.callback = callback
        self.screenshot = screenshot
        self.start: tuple[int, int] | None = None
        self.rect: int | None = None
        self.window = Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.geometry(f"{screenshot.width}x{screenshot.height}+0+0")
        self.photo = ImageTk.PhotoImage(screenshot)
        self.canvas = Canvas(
            self.window,
            width=screenshot.width,
            height=screenshot.height,
            cursor="crosshair",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        self.canvas.bind("<ButtonPress-1>", self._start)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._finish)
        self.window.bind("<Escape>", lambda _event: self._cancel())
        self.window.focus_force()

    def _start(self, event) -> None:
        self.start = (event.x, event.y)
        self.rect = self.canvas.create_rectangle(
            event.x,
            event.y,
            event.x,
            event.y,
            outline="#00a8ff",
            width=3,
        )

    def _drag(self, event) -> None:
        if self.start is not None and self.rect is not None:
            self.canvas.coords(self.rect, self.start[0], self.start[1], event.x, event.y)

    def _finish(self, event) -> None:
        if self.start is None:
            return
        left, right = sorted((self.start[0], event.x))
        top, bottom = sorted((self.start[1], event.y))
        self.window.destroy()
        if right - left >= 8 and bottom - top >= 8:
            self.callback(self.screenshot.crop((left, top, right, bottom)))
        else:
            self.callback(None)

    def _cancel(self) -> None:
        self.window.destroy()
        self.callback(None)


class MathLatexApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("MathLaTeX - 数学公式识别")
        self.root.geometry("900x560")
        self.root.minsize(700, 430)
        self.pipeline: MathLatexPipeline | None = None
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.status = StringVar(value="就绪：可截图、读取剪贴板或打开图片")
        self.split_lines = BooleanVar(value=True)
        self._build_ui()
        self.root.after(80, self._poll_events)

    def _build_ui(self) -> None:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")

        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        toolbar = ttk.Frame(outer)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="截取屏幕并识别", command=self.capture).pack(side="left")
        ttk.Button(toolbar, text="识别剪贴板图片", command=self.from_clipboard).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(toolbar, text="打开图片", command=self.open_image).pack(side="left", padx=(8, 0))
        ttk.Checkbutton(toolbar, text="自动拆分多行", variable=self.split_lines).pack(
            side="left", padx=(18, 0)
        )
        ttk.Button(toolbar, text="复制 LaTeX", command=self.copy_result).pack(side="right")

        ttk.Label(outer, textvariable=self.status, foreground="#0969da").pack(
            fill="x", pady=(14, 8)
        )
        self.output = Text(
            outer,
            wrap="word",
            undo=True,
            font=("Consolas", 13),
            padx=12,
            pady=12,
        )
        self.output.pack(fill="both", expand=True)

        ttk.Label(
            outer,
            text="提示：按 Esc 可取消截图；多行结果会自动放入 aligned 环境。",
            foreground="#666666",
        ).pack(fill="x", pady=(8, 0))

    def capture(self) -> None:
        self.root.withdraw()
        self.root.after(250, self._capture_after_hide)

    def _capture_after_hide(self) -> None:
        try:
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()
            screenshot = ImageGrab.grab(bbox=(0, 0, width, height))
            SelectionOverlay(self.root, screenshot, self._capture_done)
        except Exception as exc:  # noqa: BLE001 - UI boundary must not terminate.
            self.root.deiconify()
            messagebox.showerror("截图失败", str(exc), parent=self.root)

    def _capture_done(self, image: Image.Image | None) -> None:
        self.root.deiconify()
        self.root.lift()
        if image is not None:
            self._recognize_async(image)

    def from_clipboard(self) -> None:
        try:
            value = ImageGrab.grabclipboard()
        except Exception as exc:  # noqa: BLE001 - clipboard backends vary.
            messagebox.showerror("读取剪贴板失败", str(exc), parent=self.root)
            return
        if isinstance(value, Image.Image):
            self._recognize_async(value)
        elif isinstance(value, list) and value:
            self._load_path(Path(value[0]))
        else:
            messagebox.showinfo("没有图片", "剪贴板中没有可识别的图片。", parent=self.root)

    def open_image(self) -> None:
        selected = filedialog.askopenfilename(
            parent=self.root,
            title="选择包含数学公式的图片",
            filetypes=[
                ("图片", "*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff"),
                ("所有文件", "*.*"),
            ],
        )
        if selected:
            self._load_path(Path(selected))

    def _load_path(self, path: Path) -> None:
        try:
            with Image.open(path) as opened:
                image = opened.convert("RGB")
        except Exception as exc:  # noqa: BLE001 - Pillow exposes many decoder errors.
            messagebox.showerror("无法打开图片", str(exc), parent=self.root)
            return
        self._recognize_async(image)

    def _recognize_async(self, image: Image.Image) -> None:
        self.status.set("正在识别…首次使用会加载模型，请稍候")
        worker = threading.Thread(
            target=self._recognize_worker,
            args=(image.copy(), bool(self.split_lines.get())),
            daemon=True,
        )
        worker.start()

    def _recognize_worker(self, image: Image.Image, split_lines: bool) -> None:
        try:
            if self.pipeline is None:
                self.pipeline = MathLatexPipeline()
            lines = self.pipeline.recognize_image(image, split_lines=split_lines)
            result = self.pipeline.format_latex(lines)
            self.events.put(("success", result))
        except Exception as exc:  # noqa: BLE001 - worker errors are reported in the UI.
            self.events.put(("error", f"{type(exc).__name__}: {exc}"))

    def _poll_events(self) -> None:
        try:
            kind, payload = self.events.get_nowait()
        except queue.Empty:
            pass
        else:
            if kind == "success":
                self.output.delete("1.0", "end")
                self.output.insert("1.0", str(payload))
                self.status.set("识别完成" if payload else "没有识别到公式")
            else:
                self.status.set("识别失败（程序仍可继续使用）")
                messagebox.showerror("识别失败", str(payload), parent=self.root)
        finally:
            self.root.after(80, self._poll_events)

    def copy_result(self) -> None:
        value = self.output.get("1.0", "end-1c")
        if not value:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.root.update()
        self.status.set("LaTeX 已复制到剪贴板")


def main() -> None:
    if "--self-test" in sys.argv:
        from .selftest import run_self_test

        raise SystemExit(0 if run_self_test() else 1)
    root = Tk()
    MathLatexApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
