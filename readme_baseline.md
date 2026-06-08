第一版新增了独立的 `prepare` 阶段，当前只做“资源识别 + 环境规划 + readiness 总结”，不会自动下载数据、不会安装依赖、也不会改 repo，比较适合先在本地/服务器上安全试跑。

主要改动：

- 新增 prepare 数据模型：[models.py](D:/vsCode/kaivuAgent/xiaolong/kaivu-agent-ts/laboratory/autosota_lab/models.py)
  - `ResourceSpec`
  - `ResourceManifest`
  - `EnvironmentPlan`
  - `PrepareReport`
  - `PaperConfig` 增加 `paper_pdf_path`、`resource_root`、`setup_commands`、`pre_eval_commands`、`auto_prepare`

- 新增 prepare 编排器：[prepare.py](D:/vsCode/kaivuAgent/xiaolong/kaivu-agent-ts/laboratory/autosota_lab/prepare.py)
  - `Preparer.run()`
  - 顺序执行：
    - `resource_discovery`
    - `environment_planning`
    - `readiness_check`

- 新增 Agent 包装：[agents.py](D:/vsCode/kaivuAgent/xiaolong/kaivu-agent-ts/laboratory/autosota_lab/agents.py)
  - `AgentResource`
  - `AgentInit`

- 新增 prepare prompts：[prompts.py](D:/vsCode/kaivuAgent/xiaolong/kaivu-agent-ts/laboratory/autosota_lab/prompts.py)
  - `resource_discovery_prompt`
  - `environment_planning_prompt`
  - `readiness_check_prompt`

- CLI 接入：[cli.py](D:/vsCode/kaivuAgent/xiaolong/kaivu-agent-ts/laboratory/autosota_lab/cli.py)
  - 新增命令：
    ```bash
    autosota-lab prepare <paper_name>
    ```

- onboard 接入配置字段：[onboard.py](D:/vsCode/kaivuAgent/xiaolong/kaivu-agent-ts/laboratory/autosota_lab/onboard.py)
  - 支持 `--paper-pdf`
  - 支持 `--resource-root`
  - 支持多次传 `--setup-command`
  - 支持多次传 `--pre-eval-command`

<!-- 验证过：

```bash
python -m py_compile laboratory\autosota_lab\models.py laboratory\autosota_lab\prompts.py laboratory\autosota_lab\agents.py laboratory\autosota_lab\prepare.py laboratory\autosota_lab\cli.py laboratory\autosota_lab\onboard.py
python -m autosota_lab.cli --help
python -m autosota_lab.prepare --help
```

也跑了一个临时 `onboard + prepare --dry-run`，流程能正常生成 run 目录和 fallback prepare 产物。 -->

服务器上可以这样试：

```bash
cd /home/xiaolong/workspace/kaivu-agent-ts/laboratory
pip install -e .

autosota-lab onboard my-paper \
  --repo /home/xiaolong/workspace/kaivu-agent-ts/laboratory/paper_repos/xxx \
  --eval-command "python eval.py" \
  --primary-metric accuracy \
  --metric-direction higher \
  --resource-root /home/xiaolong/workspace/kaivu-agent-ts/laboratory/resources

autosota-lab prepare my-paper \
  --code-agent codex
```

第一版还没把 `prepare` 自动插入 `optimize`，这是有意的：先单独调 prepare 的输出质量，等资源清单和环境计划稳定后，再接到 `baseline_setup` 前面。