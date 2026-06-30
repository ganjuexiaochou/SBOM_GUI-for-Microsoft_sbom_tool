

# 微软 SBOM 工具可视化生成器 (Microsoft SBOM Tool GUI)

这是一个为微软开源的 **[Microsoft SBOM Tool](https://github.com/microsoft/sbom-tool)** 打造的图形用户界面（GUI）包装程序。

通过该工具，您无需在命令行中记忆和输入复杂的参数，即可通过直观的界面快速为**传统软件项目**、**操作系统镜像**或**物联网（IoT）固件**生成合规的 SPDX 格式软件物料清单（SBOM）。

---

## 🚀 功能特点

* **双场景支持**：针对“传统软件开发”与“IoT/嵌入式固件/OS镜像”提供了不同的参数填写指引。
* **路径一键选择**：无需手动复制路径，支持通过系统文件夹浏览器直接选择目录。
* **实时日志输出**：内置控制台日志框，实时展示 `sbom-tool` 的执行进度与输出结果。
* **多线程防假死**：采用多线程技术，生成期间 GUI 界面不卡顿、不无响应。
* **单文件打包**：支持将 Python 脚本与微软原版 `.exe` 工具打包融合为一个独立的 `.exe` 文件，开箱即用。

---

## 🛠️ 准备工作

在开始之前，请确保您的开发环境中已准备好以下内容：

1. **Python 3.x**：确保已安装 Python 并配置了环境变量。
2. **微软官方 SBOM 工具**：
   * 请前往 **[Microsoft SBOM Tool GitHub Releases](https://github.com/microsoft/sbom-tool/releases)** 下载适用于 Windows 的最新版本（例如 `sbom-tool-win-x64.exe`）。
   * 将下载好的 `sbom-tool-win-x64.exe` 放入您的工作目录中。

---

## 📂 项目目录结构

在打包前，请确保您的工作目录结构如下：

```text
SBOM_GUI_Project/
│
├── sbom_gui.py              # 本项目提供的 Python GUI 脚本
└── sbom-tool-win-x64.exe    # 从微软官方下载的工具
```

---

## 📝 参数填写指南

为了生成准确的 SBOM，请根据您的项目类型参考以下指南填写参数：

### 1. 必填参数 (Required)

| 参数名称 | 命令行参数 | 传统软件项目填写示例 | IoT 固件 / OS 镜像项目填写示例 |
| :--- | :--- | :--- | :--- |
| **构建产物路径** | `-b` | 存放最终生成的 `exe`、`dll`、`jar`、`war` 的目录（如 `dist/` 或 `bin/Release/`）。 | 存放最终烧录文件（`.bin`、`.hex`）或系统镜像（`.img`、`.iso`）的输出目录。 |
| **构建组件/源码路径** | `-bc` | 项目源码根目录，需包含依赖配置文件（如 `package.json`, `pom.xml`, `requirements.txt` 等）。 | 包含固件源码、第三方开源库（`third_party/`）或构建配置（`CMakeLists.txt`、`Yocto recipes`）的根目录。 |
| **产品/软件包名称** | `-pn` | 您的软件名称（如 `MyApp`）。 | 固件或镜像名称（如 `SmartRouter_Firmware`）。 |
| **版本号** | `-pv` | 软件版本（如 `1.0.0`）。 | 固件版本或构建流水线号（如 `v2.1.0_build20231025`）。 |
| **供应商/厂商名称** | `-ps` | 开发团队或公司名称（如 `MyCompany`）。 | 设备制造厂商或组织名称（如 `ACME_Corp`）。 |

### 2. 常用可选参数 (Optional)

* **输出目录路径 (`-m`)**：指定生成的 SBOM 文件（`manifest.spdx.json`）存放位置。**若留空，默认会生成在【构建产物路径】下的 `_manifest` 文件夹中。**
* **命名空间基础 URI (`-nsb`)**：用于唯一标识该 SBOM 的 URI 基础前缀（例如：`https://mycompany.com/sbom`）。

---

## 💻 本地开发与运行

如果您想直接通过 Python 运行该程序：

1. 打开终端（CMD 或 PowerShell），切换到项目目录：
   ```bash
   cd SBOM_GUI_Project
   ```
2. 运行 Python 脚本：
   ```bash
   python sbom_gui.py
   ```

---

## 📦 最终打包发布 (生成独立单文件 EXE)

为了方便分发给测试、合规、安全团队直接使用，我们可以将 Python 脚本和微软的 `sbom-tool-win-x64.exe` 融合打包成一个**完全独立、双击即用**的 `.exe` 文件。

### 步骤 1：安装 PyInstaller
在终端中运行以下命令安装打包工具：
```bash
pip install pyinstaller
```

### 步骤 2：执行打包命令
在项目根目录下，执行以下命令：
```bash
pyinstaller --noconsole --onefile --add-binary "sbom-tool-win-x64.exe;." sbom_gui.py
```

**参数解析：**
* `--noconsole`：运行时隐藏命令行黑窗口，只显示美观的 GUI 界面。
* `--onefile`：将所有依赖项、Python 解释器以及微软工具打包进一个单一的 `.exe` 文件中。
* `--add-binary "sbom-tool-win-x64.exe;."`：**核心步骤**。将微软的二进制工具作为资源嵌入到生成的程序中（`;.` 表示在运行时将其释放到临时根目录，脚本内已通过 `sys._MEIPASS` 动态兼容该路径）。

### 步骤 3：获取成品
打包完成后，您的项目目录下会多出几个文件夹：
* **`dist/`**：**最终的成品存放在这里。** 里面会有一个 `sbom_gui.exe`（约 30MB~50MB 左右，已包含所有运行所需环境）。
* `build/` 和 `sbom_gui.spec`：打包过程的中间产物，可以安全删除。

您现在可以将 `dist/sbom_gui.exe` 发送给任何 Windows 用户，他们无需配置 Python 环境或单独下载微软工具，双击即可直接使用！

---

## 🔗 相关链接

* **微软官方开源仓库**：[Microsoft SBOM Tool (GitHub)](https://github.com/microsoft/sbom-tool)
* **SPDX 规范官网**：[Software Package Data Exchange (SPDX)](https://spdx.dev/)
