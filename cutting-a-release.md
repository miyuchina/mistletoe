<h1>Cutting a Release<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right' width='128' height='128'></h1>

Releases are built and published by `.github/workflows/release.yml`. Pull requests
and branch pushes build and validate distributions. Pushing a `v*` tag to
`miyuchina/mistletoe` also publishes those validated files to PyPI and GitHub.
Forks cannot publish through this workflow.

## One-time setup

* Create the `pypi` GitHub Actions environment in `miyuchina/mistletoe` and restrict
  its deployment tags to `v*`. Configure any desired required reviewers.
* Add a [trusted publisher](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
  to the existing `mistletoe` PyPI project with these values:
    * owner: `miyuchina`
    * repository: `mistletoe`
    * workflow filename: `release.yml`
    * environment: `pypi`
* Enable [immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)
  in the GitHub repository settings. The workflow uploads all assets to a draft
  before publishing it, so it also works when immutability is enabled.

PyPI publishing uses GitHub's OIDC identity rather than an API token and includes
PyPI attestations. The workflow also creates GitHub provenance attestations for
the wheel and source distribution. No PyPI secret is needed.

## Publish a release

1. Set `mistletoe.__version__` to the release version, for example `1.7.0`, and
   commit the change. Wait for the tests and distribution checks to pass.
2. Create and push a matching tag on that commit:

   ```sh
   git tag -a v1.7.0 -m 'Release 1.7.0'
   git push upstream v1.7.0
   ```

   The version after `v` must exactly match the version in the built package
   metadata. Tagging does not change the package version automatically.
3. Monitor the Release workflow and approve the `pypi` deployment if the
   environment requires it. It builds the wheel and sdist separately, validates
   both, attests them, and publishes the same files to both destinations.
4. Check the [PyPI project](https://pypi.org/project/mistletoe/) and
   [GitHub release](https://github.com/miyuchina/mistletoe/releases). GitHub release
   notes are generated automatically; both the wheel and sdist are attached.
   Verify installation in a fresh environment with
   `python -m pip install mistletoe==1.7.0`.
5. Commit the next development version.

## Failed runs and retries

PyPI and GitHub publishing run independently after validation and attestation;
check both destinations before retrying a failed job. Rerun only the failed jobs
when one destination has already succeeded. Published files are never overwritten.

The GitHub job refuses to overwrite any existing release, including a draft. If a
run leaves a draft, inspect its assets and generated notes before completing it
manually or deleting the unpublished draft and retrying the failed job. Once a
release is published with immutability enabled, its tag and assets cannot be
changed; corrections require a new version.
