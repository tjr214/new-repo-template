# nurt Project Template

This template is meant to be used through the global `nurt` CLI.

## Template Bootstrap (User Flow)

For end users generating a new project from this template, the canonical flow is the global `nurt` CLI.

1. Install `nurt` from git:
   - `uv tool install git+https://github.com/tjr214/new-repo-template.git`
2. Generate a project:
   - `nurt new <project-name>`

## Additional Docs

- For fullstack template setup/auth flow details, see `docs/FULLSTACK_SETUP.md`.
- For mobile/TV setup, caveats, and validation flow details, see `docs/MOBILE_TV_SETUP.md`.
- For CI branch protection and required status checks, see `docs/BRANCH_PROTECTION.md`.
- For preset-combination regression coverage policy, see `docs/REGRESSION_SUITE.md`.
- For dependency upgrade/versioning policy, see `docs/DEPENDENCY_UPGRADE_POLICY.md`.
- For optional signing workflow design, secrets map, and enablement flow, see `docs/OPTIONAL_SIGNING_PIPELINE.md`.
- For phased rollout release gates, see `docs/RELEASE_CHECKLIST.md`.
