### Version schema:
- General: `major.minor.patch` ([semver](https://semver.org/))
- Pre-releases (release candidates) must end with `~XX` where `XX` is the number of the pre-release
  - So, before version `7.1.1` is released, there may be versions `7.1.1~01`, `7.1.1~02`, and so on
- Releases don't have a suffix.
  - So, once version `7.1.1` is ready, it is published as `7.1.1`
- This concept ensures that stable releases are always evaluated as a higher version number than pre-releases.

### The following steps have to be followed to create a release:
1. Update the changelog file
3. commit all changes
4. Do a git push: `git push`
6. Create a git tag in the format v+VERSION (eg. v7.0.0): `git tag vVERSION`
7. Push tags: `git push --tags`

### In case of a mistake, the tag can be deleted:
1. Locally: `git tag -d vVERSION`
2. Remotely: `git push --delete origin vVERSION`