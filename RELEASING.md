# Releasing mhcgnomes

The release process is documented in [docs/releasing.md](docs/releasing.md),
also published at <https://pirl-unc.github.io/mhcgnomes/releasing/>.

In short: every pull request bumps `mhcgnomes/version.py`. After it merges,
run `./deploy.sh` from a clean, up-to-date `main` (`--fetch` fetches `origin`
first; `--dry-run` prints the tag and push commands instead of running them).
It runs lint and tests, builds, pushes the `v<version>` tag, and checks that
the version reached PyPI.
