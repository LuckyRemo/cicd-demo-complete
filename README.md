# cicd-demo-complete

一个刻意做得很小、但流程完整的 Python 项目，用来练习 GitHub Actions 上的
CI/CD：代码检查、跨版本测试、覆盖率、打包、GitHub Release、Docker 镜像发布。

核心功能只有一个文本统计 CLI，业务逻辑不是重点，流水线才是。

```text
$ cicd-demo-complete "Hello hello, CI/CD world!" --top 3
words:          5
unique words:   4
reading time:   0.03 min
top words:
  hello        2
  ci           1
  cd           1
```

## 目录结构

```text
.
├─ .github/
│  ├─ workflows/
│  │  ├─ ci.yml              # PR / push 到 main 时跑 CI
│  │  └─ release.yml         # 推送 v* tag 时发布 Release + 镜像
│  └─ dependabot.yml         # 每周自动升级依赖和 Actions
├─ src/cicd_demo_complete/
│  ├─ stats.py               # 纯函数：分词、词频、阅读时长
│  ├─ cli.py                 # argparse 命令行入口
│  └─ __main__.py            # 支持 python -m cicd_demo_complete
├─ tests/                    # pytest 测试
├─ Dockerfile                # 多阶段构建，非 root 运行
├─ pyproject.toml            # 打包、pytest、ruff、coverage 配置
└─ README.md
```

## 1. 本地跑通

Windows PowerShell：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

跑测试、检查和打包：

```bash
pytest --cov=cicd_demo_complete --cov-report=term-missing
ruff check .
ruff format --check .
python -m build
```

体验 CLI：

```bash
cicd-demo-complete "Hello hello, CI/CD world!" --top 3
cicd-demo-complete "one two two" --json
echo "alpha beta alpha" | cicd-demo-complete
```

如果 `ruff format --check .` 报格式问题，执行 `ruff format .` 后重新提交即可。

## 2. 推到 GitHub

先在 GitHub 建一个空仓库（不要勾选自动生成 README），然后：

```bash
git init
git add .
git commit -m "chore: bootstrap python ci/cd demo"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

推送后打开仓库的 **Actions** 页，会看到 `CI` 工作流自动运行。

## 3. 读懂 CI

`.github/workflows/ci.yml` 在三种情况下触发：push 到 `main`、提交 PR、手动
`workflow_dispatch`。它包含三个 job：

| Job | 做什么 | 为什么 |
| --- | --- | --- |
| `lint` | `ruff check` + `ruff format --check` | 统一风格，尽早发现低级错误 |
| `test` | Python 3.10 / 3.11 / 3.12 矩阵跑 pytest + coverage | 防止只在某个版本上能跑 |
| `package` | `python -m build` + `twine check` | 每次合并前都确认包能构建、元数据合法 |

几个值得留意的写法：

- `needs: [lint, test]`：前面全绿才构建包，避免浪费。
- `strategy.matrix` + `fail-fast: false`：某个版本失败时，其他版本仍跑完，方便定位。
- `cache: pip`：缓存依赖下载，后续运行更快。
- `concurrency` + `cancel-in-progress`：同一分支连续 push 时取消旧任务，省额度。
- `permissions: contents: read`：默认只读，遵循最小权限原则。
- `upload-artifact`：把 `dist/` 和覆盖率报告留存在 Actions 页面，方便下载。

### 练习：故意把 CI 跑红

1. 把 `tests/test_stats.py` 里的 `assert count_words("one two three") == 3` 改成 `== 4`。
2. `git commit` 并 push。
3. 在 Actions 里看到 `Test (Python 3.10/3.11/3.12)` 三个任务变红，点进去看失败断言。
4. 改回 `3` 再 push，观察变绿。

这一步能让你熟悉失败日志、重跑（Re-run jobs）和 PR 检查状态。

## 4. CD：打 tag 自动发布

`release.yml` 监听 `v*` tag，做两件事：

1. 构建 sdist/wheel，校验元数据，创建 GitHub Release 并附带安装包；
2. 构建 Docker 镜像并推送到 GitHub Container Registry（GHCR）。

发布 `v0.1.0`：

```bash
# 先把 pyproject.toml 里的 version 改成 0.1.0
git add pyproject.toml
git commit -m "chore: release v0.1.0"
git push

git tag v0.1.0
git push origin v0.1.0
```

然后：

- **Releases** 页面会出现 `v0.1.0`，附带 `.whl` 和 `.tar.gz`；
- **Packages** 页面会出现 `cicd-demo-complete` 镜像，标签包括 `0.1.0`、`0.1` 和 `sha-xxxx`。

拉取并运行镜像（把 `<owner>` 换成你的用户名或组织）：

```bash
docker pull ghcr.io/<owner>/<repo>:0.1.0
docker run --rm ghcr.io/<owner>/<repo>:0.1.0 "hello hello world"
```

GHCR 包默认是私有的。要在别的机器拉取，先创建带 `read:packages` 权限的
Personal Access Token，然后 `docker login ghcr.io -u <用户名>`；或者在包的
Settings 里把可见性改成 public。

### 版本号策略

示例使用静态版本号，发布前手动改 `pyproject.toml`。真实项目可以用
`setuptools-scm` 从 tag 自动推导版本，避免 tag 和包版本不一致。

## 5. 可选：发布到 TestPyPI

如果想把“发布 Python 包”也练一遍，使用 PyPI Trusted Publishing，不需要保存
密码。先在 TestPyPI 注册账号并配置 Trusted Publisher（仓库、workflow 文件名、
environment 名要对应），再新增 `.github/workflows/publish-testpypi.yml`：

```yaml
name: Publish to TestPyPI

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: testpypi
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
```

安装测试包时加 `--index-url`（TestPyPI 可能缺少依赖，所以同时保留官方源）：

```bash
python -m pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ cicd-demo-complete
```

## 6. 可选：部署到自己的服务器

真正部署到 VPS 时，把镜像拉到服务器再重启容器即可。仓库 Secrets 里配置
`DEPLOY_HOST`、`DEPLOY_USER`、`DEPLOY_SSH_KEY`，然后在 release 流程后追加：

```yaml
  deploy:
    needs: [github-release, docker]
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            cd /opt/cicd-demo-complete
            docker compose pull
            docker compose up -d
```

这属于第三方 Action，生产环境应固定到 commit SHA 并审查其权限。练手阶段先用
Release + GHCR 就够了。

## 7. 常见坑

- **Actions 页面没有 workflow**：确认 YAML 在 `.github/workflows/` 下，且已推到
  默认分支；PR 里的 workflow 来自源分支。
- **YAML 缩进错误**：workflow 不运行或直接报解析错误，先看 Actions 的报错行号。
- **权限不足**：默认 `GITHUB_TOKEN` 权限较窄；发布 Release 需要 `contents: write`，
  推 GHCR 需要 `packages: write`，已在对应 job 单独声明。
- **镜像名含大写**：Docker 仓库名必须小写，示例里用 `${GITHUB_REPOSITORY,,}` 处理。
- **tag 和版本号不一致**：发布前先改 `pyproject.toml` 的 `version`。
- **私有仓库消耗额度**：矩阵跑三个 Python 版本会成倍消耗 Actions 分钟数，
  练手够用，但要注意账单。

## 8. 下一步练习

- 给 `main` 开分支保护，要求 CI 通过才能合并 PR；
- 把覆盖率上传到 Codecov，并在 PR 里显示覆盖率变化；
- 用 `setuptools-scm` 让版本号跟随 tag；
- 增加 `pip-audit` 或 Dependabot 安全更新；
- 把 `test` 矩阵扩展到 Windows/macOS，体验跨平台 CI；
- 故意让 Docker 构建失败（例如引用不存在的文件），观察 job 依赖关系。

CI 保证“每次改动都可验证”，CD 保证“通过验证的版本能稳定交付”。先把这条链路
跑通，再逐步加安全扫描、环境审批和灰度发布。
