# Research Upgrade Folder Comparison

## Scope and method

- Original project: `/Users/pawankumar/Downloads/ai-data-analyst-platform`
- Separate research-upgrade folder: `/Users/pawankumar/Downloads/research-upgrade-files`
- Compared relative paths and SHA-256 content hashes for regular files.
- Excluded `.git`, `.venv`, `venv`, `node_modules`, `target`, `__pycache__`, build outputs (`build`, `dist`, `coverage`, `.vite`, `.next`, `out`), `.DS_Store`, and secret-like files by filename (2 in original, 0 in research folder). Secret contents were not read or included.
- Git status was inspected before comparison. Existing modifications and untracked files in the original project were preserved.
- This is a file/path/content comparison and static reference inspection, not a new test run or runtime verification.

## Summary

| Classification | Files |
|---|---:|
| Present in both and byte-identical | 23 |
| Present in both but different | 19 |
| Only in research-upgrade folder | 2 |
| Only in original project | 109 |
| Original files considered | 151 |
| Research-upgrade files considered | 44 |

The research-upgrade folder remains physically separate. However, key cleaning, forecasting, dataset-health, and UI code is already present in the original project and statically connected through its application APIs. The original is not a byte-for-byte copy of the research folder: 19 shared paths differ, and the original contains substantial pre-existing application code and integration support absent from the upgrade folder.

The 23 identical files are not, by themselves, proof of feature integration. Nineteen are experiment result files; results and documentation are not evidence that the app executes the corresponding feature.

## Static integration references observed

These references show that major feature paths exist in the original application. They establish wiring in source code, not successful runtime behavior:

- `frontend/src/api/client.js` calls the backend dataset cleaning, health-score, health-history, and forecast routes.
- `backend/src/main/java/com/aidataanalyst/controller/DatasetController.java` exposes the matching dataset operations, checks dataset ownership, delegates to `MlServiceClient`, and records health and forecast results.
- `backend/src/main/java/com/aidataanalyst/service/MlServiceClient.java` posts to the ML cleaning, health, and forecasting endpoints.
- `ml-service/app/main.py` registers the cleaning, health, and forecasting routers.
- `frontend/src/pages/Cleaning.jsx` submits records and displays cleaning summary and repair-log fields.
- `frontend/src/pages/Overview.jsx` submits health-score requests and displays health fields and assessment history.
- `frontend/src/pages/Forecasting.jsx` submits forecast requests and renders forecast and model-comparison fields.
- The original project also contains integration support not supplied as files in the research folder, including `DatasetHealthScore`, its repository/persistence service, ownership checking, CSV parsing, database schema, authentication, and application configuration.

This inspection does **not** prove that every API contract works at runtime or that a complete authenticated flow succeeds.

## Classification: present in both and identical (23)

- `backend/src/main/java/com/aidataanalyst/entity/Dataset.java`
- `experiments/dq_sensitivity_benchmark.py`
- `experiments/imputation_benchmark_v1.py`
- `experiments/results/dq_sensitivity_curves.csv`
- `experiments/results/dq_sensitivity_raw.csv`
- `experiments/results/dq_sensitivity_verdict.csv`
- `experiments/results/environment_forecasting.json`
- `experiments/results/environment_imputation.json`
- `experiments/results/forecasting_auto_choices.csv`
- `experiments/results/forecasting_per_series_mase.csv`
- `experiments/results/forecasting_raw.csv`
- `experiments/results/forecasting_significance.csv`
- `experiments/results/forecasting_summary.csv`
- `experiments/results/imputation_raw.csv`
- `experiments/results/imputation_significance.csv`
- `experiments/results/imputation_summary.csv`
- `experiments/results/mnar_detector_raw.csv`
- `experiments/results/mnar_detector_summary.csv`
- `experiments/results/v1_defect_finding/forecasting_benchmark_raw.csv`
- `experiments/results/v1_defect_finding/forecasting_benchmark_summary.csv`
- `experiments/results/v1_defect_finding/imputation_benchmark_raw.csv`
- `experiments/results/v1_defect_finding/imputation_benchmark_summary.csv`
- `ml-service/requirements-dev.txt`

## Classification: present in both but different (19)

- `.gitignore`
- `README.md`
- `backend/src/main/java/com/aidataanalyst/controller/DatasetController.java`
- `experiments/README.md`
- `experiments/common.py`
- `experiments/forecasting_benchmark.py`
- `experiments/imputation_benchmark.py`
- `experiments/mnar_detector_benchmark.py`
- `frontend/src/pages/Cleaning.jsx`
- `frontend/src/pages/Forecasting.jsx`
- `frontend/src/pages/Overview.jsx`
- `ml-service/app/models/schemas.py`
- `ml-service/app/services/cleaning_service.py`
- `ml-service/app/services/forecasting_service.py`
- `ml-service/app/services/health_service.py`
- `ml-service/pytest.ini`
- `ml-service/tests/test_cleaning_service.py`
- `ml-service/tests/test_forecasting_service.py`
- `ml-service/tests/test_health_service.py`

The differing contents mean the research copy should not be treated as a drop-in replacement. In particular, the original `DatasetController` participates in the original backend's auth, ownership, persistence, and other service integrations; the original frontend pages also sit within the existing frontend API/context structure.

## Classification: only in research-upgrade folder (2)

- `RESEARCH.md`
- `experiments/run_all.sh`

These are documentation/runner files, not missing application endpoint implementations. The original project has its own experiment documentation and benchmark runner(s), so compare their behavior and safety before deciding whether either research-only file is useful.

## Classification: only in original project (109)

These files belong to the original app or its integrated extensions and are not present in the research-upgrade folder. Their absence from the upgrade folder does not mean they should be copied or replaced.

<details>
<summary>Full original-only relative-path list</summary>

- `.github/modernize/java-upgrade/.gitignore`
- `.github/modernize/java-upgrade/hooks/scripts/recordToolUse.ps1`
- `.github/modernize/java-upgrade/hooks/scripts/recordToolUse.sh`
- `.vscode/settings.json`
- `backend/Dockerfile`
- `backend/pom.xml`
- `backend/src/main/java/com/aidataanalyst/Application.java`
- `backend/src/main/java/com/aidataanalyst/controller/AuthController.java`
- `backend/src/main/java/com/aidataanalyst/controller/UploadController.java`
- `backend/src/main/java/com/aidataanalyst/dto/AuthResponse.java`
- `backend/src/main/java/com/aidataanalyst/dto/LoginRequest.java`
- `backend/src/main/java/com/aidataanalyst/dto/RefreshTokenRequest.java`
- `backend/src/main/java/com/aidataanalyst/dto/RegisterRequest.java`
- `backend/src/main/java/com/aidataanalyst/entity/ChatMessage.java`
- `backend/src/main/java/com/aidataanalyst/entity/ChatSession.java`
- `backend/src/main/java/com/aidataanalyst/entity/DatasetHealthScore.java`
- `backend/src/main/java/com/aidataanalyst/entity/DatasetVersion.java`
- `backend/src/main/java/com/aidataanalyst/entity/Forecast.java`
- `backend/src/main/java/com/aidataanalyst/entity/RefreshToken.java`
- `backend/src/main/java/com/aidataanalyst/entity/Report.java`
- `backend/src/main/java/com/aidataanalyst/entity/User.java`
- `backend/src/main/java/com/aidataanalyst/entity/Workspace.java`
- `backend/src/main/java/com/aidataanalyst/repository/ChatMessageRepository.java`
- `backend/src/main/java/com/aidataanalyst/repository/ChatSessionRepository.java`
- `backend/src/main/java/com/aidataanalyst/repository/DatasetHealthScoreRepository.java`
- `backend/src/main/java/com/aidataanalyst/repository/DatasetRepository.java`
- `backend/src/main/java/com/aidataanalyst/repository/DatasetVersionRepository.java`
- `backend/src/main/java/com/aidataanalyst/repository/ForecastRepository.java`
- `backend/src/main/java/com/aidataanalyst/repository/RefreshTokenRepository.java`
- `backend/src/main/java/com/aidataanalyst/repository/ReportRepository.java`
- `backend/src/main/java/com/aidataanalyst/repository/UserRepository.java`
- `backend/src/main/java/com/aidataanalyst/repository/WorkspaceRepository.java`
- `backend/src/main/java/com/aidataanalyst/security/JwtAuthFilter.java`
- `backend/src/main/java/com/aidataanalyst/security/JwtService.java`
- `backend/src/main/java/com/aidataanalyst/security/SecurityConfig.java`
- `backend/src/main/java/com/aidataanalyst/service/ChatPersistenceService.java`
- `backend/src/main/java/com/aidataanalyst/service/CsvParser.java`
- `backend/src/main/java/com/aidataanalyst/service/DatasetAccessService.java`
- `backend/src/main/java/com/aidataanalyst/service/DatasetHealthScorePersistenceService.java`
- `backend/src/main/java/com/aidataanalyst/service/DatasetStorageService.java`
- `backend/src/main/java/com/aidataanalyst/service/ForecastPersistenceService.java`
- `backend/src/main/java/com/aidataanalyst/service/MlServiceClient.java`
- `backend/src/main/java/com/aidataanalyst/service/RefreshTokenService.java`
- `backend/src/main/java/com/aidataanalyst/service/ReportGenerationService.java`
- `backend/src/main/java/com/aidataanalyst/service/UserService.java`
- `backend/src/main/java/com/aidataanalyst/service/VersioningService.java`
- `backend/src/main/resources/application.yml`
- `backend/src/test/java/com/aidataanalyst/service/CsvParserTest.java`
- `backend/src/test/java/com/aidataanalyst/service/DatasetAccessServiceTest.java`
- `backend/src/test/java/com/aidataanalyst/service/DatasetHealthScorePersistenceServiceTest.java`
- `db/schema.sql`
- `docker-compose.yml`
- `experiments/forecasting_research_benchmark.py`
- `experiments/imputation_research_benchmark.py`
- `experiments/requirements.txt`
- `experiments/results/forecasting_benchmark_raw.csv`
- `experiments/results/forecasting_benchmark_report.md`
- `experiments/results/forecasting_benchmark_summary.csv`
- `experiments/results/imputation_benchmark_comparisons.csv`
- `experiments/results/imputation_benchmark_raw.csv`
- `experiments/results/imputation_benchmark_report.md`
- `experiments/results/imputation_benchmark_summary.csv`
- `experiments/run_research_benchmarks.sh`
- `experiments/tests/__init__.py`
- `experiments/tests/test_imputation_benchmark.py`
- `frontend/Dockerfile`
- `frontend/index.html`
- `frontend/nginx.conf`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/src/App.jsx`
- `frontend/src/api/DatasetContext.jsx`
- `frontend/src/api/auth.js`
- `frontend/src/api/client.js`
- `frontend/src/main.jsx`
- `frontend/src/pages/Chat.jsx`
- `frontend/src/pages/Insights.jsx`
- `frontend/src/pages/Login.jsx`
- `frontend/src/pages/Register.jsx`
- `frontend/src/pages/Reports.jsx`
- `frontend/src/pages/Upload.jsx`
- `frontend/src/pages/Visualization.jsx`
- `frontend/src/styles.css`
- `frontend/vite.config.js`
- `ml-service/Dockerfile`
- `ml-service/app/__init__.py`
- `ml-service/app/main.py`
- `ml-service/app/models/__init__.py`
- `ml-service/app/routers/__init__.py`
- `ml-service/app/routers/chat.py`
- `ml-service/app/routers/cleaning.py`
- `ml-service/app/routers/forecasting.py`
- `ml-service/app/routers/health.py`
- `ml-service/app/routers/insights.py`
- `ml-service/app/routers/reports.py`
- `ml-service/app/routers/stats.py`
- `ml-service/app/services/__init__.py`
- `ml-service/app/services/chat_service.py`
- `ml-service/app/services/insights_service.py`
- `ml-service/app/services/llm_provider.py`
- `ml-service/app/services/rag_service.py`
- `ml-service/app/services/report_service.py`
- `ml-service/app/services/stats_service.py`
- `ml-service/requirements.txt`
- `ml-service/tests/test_cleaning_imputation.py`
- `reports/project-audit.md`
- `research/implementation-roadmap.md`
- `research/research-matrix.md`
- `research/research-upgrade-status.md`

</details>

## Important gaps and conflicts to review before any merge

1. **The research folder is still separate**, but the key ML implementations and three updated frontend pages have matching relative paths in the original project. Those shared files differ, so do not copy over the original versions blindly.
2. **Backend integration support exists only in the original tree**: health-score entity/repository/persistence, dataset access service, CSV parser, schema, auth, and storage. Those are not part of the 44-file research-upgrade subset. The current controller references several of these original-only classes.
3. **No research-folder counterparts exist for the original app config and packaging files** such as `docker-compose.yml`, `backend/pom.xml`, `application.yml`, frontend package files, or Dockerfiles. The research folder is a partial overlay, not a complete application project.
4. **Two research-only files remain** (`RESEARCH.md` and `experiments/run_all.sh`). The original has separate research documentation and a benchmark runner; their commands and output safety should be reviewed independently.
5. **Generated benchmark outputs overlap substantially and are identical in 19 files.** Treat these as result artifacts only; they do not establish that the application code is integrated or that results are reproducible.
6. This comparison did not inspect `.env` or other excluded secret-like file contents and did not start services, run tests, or connect to any database.

## Conclusion

The research-upgrade folder has not been physically merged away and still contains two unique files. At the same time, the original project contains the main research-upgraded ML and frontend paths, and static references show those paths are wired into the original backend/frontend architecture. The merge status is therefore **partially integrated at the application-source level, not an exact/full folder merge**. Runtime correctness and completeness are not established by this comparison.

No files were moved, copied, overwritten, deleted, or merged. No database or application data was accessed or modified. The only new file from this comparison is this report.
