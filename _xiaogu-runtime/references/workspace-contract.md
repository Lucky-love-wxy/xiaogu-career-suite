# 工作区契约

```text
career-workspace/
├── profile/candidate-profile.md
├── jobs/raw/<job_id>.json
├── jobs/decoded/<job_id>.json
├── resumes/<job_id>/<version>/
├── applications/
├── interviews/transcripts/
├── interviews/reviews/
├── knowledge/cards/
├── actions/
└── _workspace/state.json
```

岗位状态只允许：

```text
collected → reviewing → shortlisted → resume_ready → applied → interview → offer
                                                                  ├→ rejected
                                                                  └→ withdrawn
offer → accepted | declined
```

终止态不能静默回退。要重新申请同一职位时创建新的申请记录，保留旧记录。

每个事实保存来源类别：`jd_disclosed`、`candidate_confirmed`、`transcript_fact`、`written_material`、`inference`、`unknown`。推断和未知不得写进候选人事实主档。
