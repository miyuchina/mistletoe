<h1>Cutting a Release<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right' width='128' height='128'></h1>

For maintainers, here are the basic steps when creating a new release of mistletoe.

* set a release version & commit [chore: version <x.y.z>](https://github.com/miyuchina/mistletoe/commit/72e35ff22e823083915ed0327c5f479afec539fa)
* publish artifacts of the release
    * official documentation: [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
    * install / upgrade the build tool: `$ python -m pip install --upgrade build`
    * make sure there are no old relicts in the local "dist" folder
    * build the Wheel artifact ("dist/*.whl"): `$ python -m build`
    * upload the distribution archives to PyPi:
        * install / upgrade Twine: `$ python -m pip install --upgrade twine`
        * if unsure, upload to test PyPi and/or test locally - see [docs](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives)
        * do the upload to PyPi: `$ python -m twine upload dist/*`
            * for the username, use `__token__`, for the password, use your token from PyPi (see docs again how to do that)
        * check that you can install locally what you uploaded: `$ python -m pip install mistletoe`
* [create the release in GitHub](https://github.com/miyuchina/mistletoe/releases/new)
    * attach the "dist/*.whl" from the previous step to the release (drag & drop) (source code archives are attached automatically)
    * publish the release, let GitHub create a new Git tag automatically
* commit [chore: next dev version](https://github.com/miyuchina/mistletoe/commit/d91f21a487b72529a584b8958bffaed864dd67d7)
