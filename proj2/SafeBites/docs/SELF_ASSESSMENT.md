# 📝 Software Sustainability Evaluation (Project 2) - Self Assessment

This document provides evidence for the sustainability rubric for **SafeBites** (Project 2).

---
<!-- 
## 🌟 Q1 - Software Overview -->

| Category | Question | Yes | No | Evidence |
|----------|---------|-----|----|---------|
| Q1       | Software Overview |  |  |  |
| 1.1      | Does your website and documentation provide a clear, high-level overview of your software? | ✅ | ❌ | See [README.md](../README.md) Overview section |
| 1.2      | Does your website and documentation clearly describe the type of user who should use your software? | ✅ | ❌ | See [README.md](../README.md) Intended Users section |
| 1.3      | Do you publish case studies to show how your software has been used by yourself and others? | ✅ | ❌ | See [README.md](../README.md) Example Use Cases |
| Q2        | Identity                                                                |     |     |                                              |
| 2.1       | Is the name of your project/software unique?                            | ✅   | ❌  | Project name "SafeBites" is distinct         |
| 2.2       | Is your project/software name free from trademark violations?           | ✅   | ❌  | Preliminary searches show no trademark issues|
| Q3        | Availability                                                                                                                   |     |     |                                                                                                |
| 3.1       | Is your software available as a package that can be deployed without building it?                                              | ✅   | ❌  | NA as safebites is a web application.                                |
| 3.2       | Is your software available for free?                                                                                           | ✅   | ❌  | Project is open-source and freely available on [GitHub](https://github.com/the-Shallow/SE-WOLFCAFE) |
| 3.3       | Is your source code publicly available to download, either as a downloadable bundle or via access to a source code repository? | ✅   | ❌  | Source code available in GitHub repository                                                    |
| 3.4       | Is your software hosted in an established, third-party repository like [GitHub](https://github.com), [BitBucket](https://bitbucket.org), [LaunchPad](https://launchpad.net), or [SourceForge](https://sourceforge.net)? | ✅ | ❌  | Hosted on [GitHub](https://github.com/the-Shallow/SE-WOLFCAFE)                                |
| Q4       | Documentation |  |  |  |
| 4.1      | Is your documentation clearly available on your website or within your software? | ✅ | ❌ | See [README.md](../README.md) and [docs/API_DOCS.md](../docs/API_DOCS.md) |
| 4.2      | Does your documentation include a "quick start" guide, that provides a short overview of how to use your software with some basic examples of use? | ✅ | ❌ | See [README.md](../README.md) Setup sections |
| 4.3      | If you provide more extensive documentation, does this provide clear, step-by-step instructions on how to deploy and use your software? | ✅ | ❌ | See [README.md](../README.md) Backend & Frontend Setup sections |
| 4.4      | Do you provide a comprehensive guide to all your software’s commands, functions and options? | ✅ | ❌ | See [docs/API_DOCS.md](../docs/API_DOCS.md) |
| 4.5      | Do you provide troubleshooting information that describes the symptoms and step-by-step solutions for problems and error messages? | ✅ | ❌ | See [README.md](../README.md) & backend logs documentation |
| 4.6      | If your software can be used as a library, package or service by other software, do you provide comprehensive API documentation? | ✅ | ❌ | See [docs/API_DOCS.md](../docs/API_DOCS.md) |
| 4.7      | Do you store your documentation under revision control with your source code? | ✅ | ❌ | All docs are in the `docs/` folder and version-controlled in GitHub |
| 4.8      | Do you publish your release history e.g. release data, version numbers, key features of each release etc. on your web site or in your documentation? | ✅ | ❌ | See [README.md](../README.md) badges and GitHub Releases |
| Q5       | Support |  |  |  |
| 5.1      | Does your software describe how a user can get help with using your software? | ✅ | ❌ | See [README.md](../README.md) Intended Users |
| 5.2      | Does your website and documentation describe what support, if any, you provide to users and developers? | ✅ | ❌ | See [README.md](../README.md) Contact & Contributing sections |
| 5.3      | Does your project have an e-mail address or forum that is solely for supporting users? | ✅ | ❌ | See [GitHub Discussions](https://github.com/the-Shallow/SE-WOLFCAFE/discussions) |
| 5.4      | Are e-mails to your support e-mail address received by more than one person? | ✅ | ❌ | Managed by project contributors (backend team) |
| 5.5      | Does your project have a ticketing system to manage bug reports and feature requests? | ✅ | ❌ | See [GitHub Issues](https://github.com/the-Shallow/SE-WOLFCAFE/issues) |
| 5.6      | Is your project's ticketing system publicly visible to your users, so they can view bug reports and feature requests? | ✅ | ❌ | See [GitHub Issues](https://github.com/the-Shallow/SE-WOLFCAFE/issues) |
| Q6       | Maintainability |  |  |  |
| 6.1      | Is your software’s architecture and design modular? | ✅ | ❌ | See [README.md](../README.md) Architecture Overview & Backend Setup sections |
| 6.2      | Does your software use an accepted coding standard or convention? | ✅ | ❌ | Python: PEP8, JavaScript/React: ESLint + Prettier (see [CONTRIBUTING.md](../CONTRIBUTING.md) Code Style & Best Practices) |
| Q7       | Open Standards |  |  |  |
| 7.1      | Does your software allow data to be imported and exported using open data formats? | ✅ | ❌ | See [README.md](../README.md) Backend Setup & API Documentation (JSON format used for data exchange) |
| 7.2      | Does your software allow communications using open communications protocols? | ✅ | ❌ | Uses standard HTTP/HTTPS REST APIs (see [README.md](../README.md) Backend Setup) |
| Q8       | Portability |  |  |  |
| 8.1      | Is your software cross-platform compatible? | ✅ | ❌ | Works on Windows, macOS, and Linux (see [README.md](../README.md) Local Setup) |
| Q9       | Accessibility |  |  |  |
| 9.1      | Does your software adhere to appropriate accessibility conventions or standards? | ✅ | ❌ | Frontend built with React and TailwindCSS, follows accessible design principles (see [README.md](../README.md) Frontend Setup) |
| 9.2      | Does your documentation adhere to appropriate accessibility conventions or standards? | ✅ | ❌ | Documentation written in markdown, compatible with screen readers, headings structured semantically |
| Q10      | Source Code Management |  |  |  |
| 10.1     | Is your source code stored in a repository under revision control? | ✅ | ❌ | Code hosted on [GitHub](https://github.com/the-Shallow/SE-WOLFCAFE) |
| 10.2     | Is each source code release a snapshot of the repository? | ✅ | ❌ | Releases and commits are tracked on GitHub with snapshots of code |
| 10.3     | Are releases tagged in the repository? | ✅ | ❌ | Releases are tagged using GitHub releases |
| 10.4     | Is there a branch of the repository that is always stable? (i.e. tests always pass, code always builds successfully) | ✅ | ❌ | `main` branch is stable, CI pipeline ensures tests pass |
| 10.5     | Do you back-up your repository? | ✅ | ❌ | GitHub provides versioned backups and repository cloning |
| Q11      | Building & Installing |  |  |  |
| 11.1     | Do you provide publicly-available instructions for building your software from the source code? | ✅ | ❌ | See [README.md](../README.md) Local Setup section |
| 11.2     | Can you build, or package, your software using an automated tool? | ✅ | ❌ | `pip install -r requirements.txt`, `npm install` automate setup |
| 11.3     | Do you provide publicly-available instructions for deploying your software? | ✅ | ❌ | See [README.md](../README.md) Local Setup section |
| 11.4     | Does your documentation list all third-party dependencies? | ✅ | ❌ | See `requirements.txt` and `package.json` |
| 11.5     | Does your documentation list the version number for all third-party dependencies? | ✅ | ❌ | Versions listed in `requirements.txt` and `package.json` |
| 11.6     | Does your software list the web address, and licences for all third-party dependencies and say whether the dependencies are mandatory or optional? | ✅ | ❌ | `requirements.txt` lists packages; npm dependencies in `package.json` |
| 11.7     | Can you download dependencies using a dependency management tool or package manager? | ✅ | ❌ | `pip` and `npm` handle dependency downloads |
| 11.8     | Do you have tests that can be run after your software has been built or deployed to show whether the build or deployment has been successful? | ✅ | ❌ | `pytest` for backend, `npm test` for frontend |
| Q12      | Testing |  |  |  |
| 12.1     | Do you have an automated test suite for your software? | ✅ | ❌ | See `backend/tests/` for pytest suite |
| 12.2     | Do you have a framework to periodically (e.g. nightly) run your tests on the latest version of the source code? | ✅ | ❌ | GitHub Actions workflow configured in `.github/workflows/` |
| 12.3     | Do you use continuous integration, automatically running tests whenever changes are made to your source code? | ✅ | ❌ | GitHub Actions triggers tests on PRs and pushes |
| 12.4     | Are your test results publicly visible? | ✅ | ❌ | See [CI Build](https://github.com/the-Shallow/SE-WOLFCAFE/actions) badges |
| 12.5     | Are all manually-run tests documented? | ✅ | ❌ | Documented in [README.md](../README.md) Testing section |
| Q13      | Community Engagement |  |  |  |
| 13.1     | Does your project have resources (e.g. blog, Twitter, RSS feed, Facebook page, wiki, mailing list) that are regularly updated with information about your software? | ✅ | ❌ | See [GitHub Discussions](https://github.com/the-Shallow/SE-WOLFCAFE/discussions) |
| 13.2     | Does your website state how many projects and users are associated with your project? | ✅ | ❌ | See [README.md](../README.md) Contributors section |
| 13.3     | Do you provide success stories on your website? | ✅ | ❌ | See [README.md](../README.md) Example Use Cases section |
| 13.4     | Do you list your important partners and collaborators on your website? | ✅ | ❌ | See [README.md](../README.md) Contributors section |
| 13.5     | ~Do you list your project's publications on your website or link to a resource where these are available?~ | ✅ | ❌ | N/A (not applicable) |
| 13.6     | Do you list third-party publications that refer to your software on your website or link to a resource where these are available? | ✅ | ❌ | N/A |
| 13.7     | Can users subscribe to notifications to changes to your source code repository? | ✅ | ❌ | GitHub “Watch” feature enabled |
| 13.8     | If your software is developed as an open source project (and, not just a project developing open source software), do you have a governance model? | ✅ | ❌ | Governed via project guidelines in `CONTRIBUTING.md` |
| Q14      | Contributions |  |  |  |
| 14.1     | Do you accept contributions (e.g. bug fixes, enhancements, documentation updates, tutorials) from people who are not part of your project? | ✅ | ❌ | See [CONTRIBUTING.md](../docs/CONTRIBUTING.md) |
| 14.2     | Do you have a contributions policy? | ✅ | ❌ | See [CONTRIBUTING.md](../docs/CONTRIBUTING.md) |
| 14.3     | Is your contributions' policy publicly available? | ✅ | ❌ | See [CONTRIBUTING.md](../docs/CONTRIBUTING.md) |
| 14.4     | Do contributors keep the copyright/IP of their contributions? | ✅ | ❌ | See [LICENSE](../LICENSE) and [CONTRIBUTING.md](../docs/CONTRIBUTING.md) |
| Q15      | Licensing |  |  |  |
| 15.1     | Does your website and documentation clearly state the copyright owners of your software and documentation? | ✅ | ❌ | See [README.md](../README.md) License section |
| 15.2     | Does each of your source code files include a copyright statement? | ✅ | ❌ | N/A |
| 15.3     | Does your website and documentation clearly state the licence of your software? | ✅ | ❌ | See [README.md](../README.md) License section |
| 15.4     | Is your software released under an open source licence? | ✅ | ❌ | See [LICENSE](../LICENSE) |
| 15.5     | Is your software released under an OSI-approved open-source licence? | ✅ | ❌ | See [LICENSE](../LICENSE) |
| 15.6     | Does each of your source code files include a licence header? | ✅ | ❌ | N/A |
| 15.7     | Do you have a recommended citation for your software? | ✅ | ❌ | N/A |
| Q16      | Future Plans |  |  |  |
| 16.1     | Does your website or documentation include a project roadmap (a list of project and development milestones for the next 3, 6 and 12 months)? | ✅ | ❌ | See [README.md](../README.md) Roadmap section |
| 16.2     | Does your website or documentation describe how your project is funded, and the period over which funding is guaranteed? | ✅ | ❌ | N/A |
| 16.3     | Do you make timely announcements of the deprecation of components, APIs, etc.? | ✅ | ❌ | N/A |