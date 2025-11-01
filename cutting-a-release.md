<h1>Cutting a Release<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right' width='128' height='128'></h1>

For maintainers, here are the basic steps when creating a new release of mistletoe.

* set a release version & commit [chore: version <x.y.z>](https://github.com/miyuchina/mistletoe/commit/35dfaa0a95e8abb1cdceb8e449f9590905dca439)
* publish artifacts of the release
    * official documentation: [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
    * install / upgrade the build tool: `$ python -m pip install --upgrade build`
    * make sure there are no old relicts in the local "dist" folder
    * build distribution archives (sdist and Wheel files in "dist/*"): `$ python -m build`
    * upload the distribution archives to PyPi:
        * install / upgrade Twine: `$ python -m pip install --upgrade twine`
        * if unsure, upload to test PyPi and/or test locally - see [docs](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives)
        * do the upload to PyPi: `$ python -m twine upload dist/*`
            * authenticate with your token from PyPi (for details, see docs again)
        * check that you can install locally what you uploaded: `$ python -m pip install mistletoe`
* [create the release in GitHub](https://github.com/miyuchina/mistletoe/releases/new)
    * attach the "dist/*.whl" from the previous step to the release (drag & drop) (source code archives are attached automatically)
    * publish the release, let GitHub create a new Git tag automatically
* commit [chore: next dev version](https://github.com/miyuchina/mistletoe/commit/aa624e0e7015fa9993056bb4016bdec6079122d7)
