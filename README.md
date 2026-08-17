# MathLaTeX

MathLaTeX 是一个完全离线的 Windows 截图数学公式识别工具。它可以框选屏幕、
读取剪贴板图片或打开本地图片，并生成可复制的 LaTeX。多行截图会按行拆分并输出
`aligned` 环境。

这个仓库是独立重写版本，包含完整应用源码，不包含旧版可执行文件中来源不明的代码。
应用源码采用 MIT License；公式识别模型和所有运行依赖的来源、许可证列在
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 中。

## 功能

- 鼠标框选屏幕并识别
- 识别剪贴板图片和本地图片
- 自动拆分多行公式
- 完全离线推理，不上传截图
- 识别异常显示错误窗口，不会让整个程序直接退出

## 从源码运行

需要 64 位 Windows 和 Python 3.10–3.13。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
powershell -ExecutionPolicy Bypass -File .\scripts\download_models.ps1
.\.venv\Scripts\python.exe -m mathlatex_app
```

首次下载的模型约 120 MB。下载完成后，识别过程不需要网络。
若要复现 v0.1.0 的 Windows 构建依赖版本，可以改用
`.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt`，随后执行
`.\.venv\Scripts\python.exe -m pip install -e . --no-deps`。

## 构建便携版

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_portable.ps1
```

产物位于 `dist\mathlatex`。整个文件夹可以复制到另一台 64 位 Windows 电脑，
双击 `mathlatex.exe` 即可运行；目标电脑不需要安装 Python。

构建后可执行端到端自检（退出码 0 表示模型实际识别成功）：

```powershell
Start-Process .\dist\mathlatex\mathlatex.exe -ArgumentList "--self-test" -Wait -PassThru
```

## 模型

默认从 `models\mfr` 读取三个文件：

- `encoder_model.onnx`
- `decoder_model.onnx`
- `tokenizer.json`

也可以用环境变量 `MATHLATEX_MODELS` 指定包含 `mfr` 子目录的模型根目录。

## 已知限制

- 当前截图框选覆盖主显示器；剪贴板和打开图片不受此限制。
- 行拆分适合浅色背景、深色公式。复杂排版可关闭“自动拆分多行”，将整张图作为一个公式识别。
- OCR 模型可能产生错误，请在正式文档中检查输出。

## 许可证

应用源码：MIT License，见 [`LICENSE`](LICENSE)。第三方组件：见
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
