# FEATURES TODO

- [ ] 1.0 ADD SUPPORT FOR PYTHON AND TYPESCRIPT LIBRARIES
  - [ ] Add Python Library scaffolding
  - [ ] Same with Typescript library
- [ ] 2.0 UPDATE THE `NURT NEW` FLOW TO SUPPORT MULTIPLE PROJECTS OF THE SAME TYPE
  - [ ] Allow `nurt new` to specify how many projects get added to the monorepo
    - Example: 2 python apps, 1 typescript library, 3 webapps, etc.
    - In these cases, `nurt new` should also ask for names for these sub-projects (so the directory names aren't "python1", "python2", etc.)
- [ ] 3.0 CREATE `NURT ADD` TO ADD PROJECT TYPES TO EXISTING MONOREPOS
  - [ ] Add `nurt add` so we can add any new project type to an existing monorepo
- [ ] 4.0 PROPERLY IMPLEMENT THE TEMPLATE-ASSETS SYNC FEATURE (Blocked by: 1.0, 2.0, 3.0)
  - [ ] Correctly implement new `nurt sync template-assets` functionality
    - [ ] When done, and manually reviewed, remove old legacy update-template-from-git.sh script
- [ ] 5.0 CONVERT OLD SCRIPTS TO NURT COMMANDS
  - [ ] Convert `scripts/configure-repo-protections.sh` into a `nurt` feature (maybe call it `nurt secure-repo` or something)
  - [ ] Turn RALPH.sh and the accompanying validate_template.py and visualize_plan.py scripts into `nurt ralph` features
- [ ] 6.0 FINAL TESTS BEFORE RELEASE CANDIDATE 1 (Blocked by 1.0, 2.0, 3.0, 4.0, 5.0)
  - [ ] Thoroughly test all project types (manual step)
