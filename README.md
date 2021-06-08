<h1 align="center">
  linuxmuster-linuxclient7
</h1>

<p align="center">
  <a href="https://github.com/linuxmuster/linuxmuster-linuxclient7/releases/latest"><img src="https://img.shields.io/github/v/release/linuxmuster/linuxmuster-linuxclient7?logo=github&logoColor=white" alt="GitHub release"/></a>
  <a href="https://github.com/linuxmuster/linuxmuster-linuxclient7/actions/workflows/release.yml"><img src="https://github.com/linuxmuster/linuxmuster-linuxclient7/workflows/Build%20Release/badge.svg" /></a>
  <a href="https://ask.linuxmuster.net"><img src="https://img.shields.io/discourse/users?logo=discourse&amp;logoColor=white&amp;server=https%3A%2F%2Fask.linuxmuster.net" alt="Community Forum" /></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg" /></a>
</p>

## Features    
Package for Ubuntu clients to connect to the linuxmuster.net 7 active directory server.  
This is the new version of the linuxmuster-client-adsso package.  
For full documentation, take a look at the [wiki](https://github.com/linuxmuster/linuxmuster-linuxclient7/wiki).

## Maintainance Details
    
Linuxmuster.net official | ![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+)  NO*
:---: | :---: 
[Community support](https://ask.linuxmuster.net) | ![#c5f015](https://via.placeholder.com/15/c5f015/000000?text=+)  YES**
Actively developed | ![#c5f015](https://via.placeholder.com/15/c5f015/000000?text=+)  YES
Maintainer organisation |  Netzint GmbH  
Primary maintainer | dorian@itsblue.de / andreas.till@netzint.de  
    
\* Even though this is not an official package, pull requests and issues are being looked at.  
** The linuxmuster community consits of people who are nice and happy to help. They are not directly involved in the development though, and might not be able to help in any case.

## Version schema:
- General: `major.minor.patch`
- Pre-releases (release candidates) must end with `-rcXX` where `XX` is the number of the pre-release
  - So, before version `7.1.1` is released, there may be versions `7.1.1-rc01`, `7.1.1-rc02`, and so on
- Releases are always prefixed with `release`.
  - So, once version `7.1.1` is ready, it is published as `7.1.1-release`
- This concept ensures that stable releases are always evaluated as a higher version number than pre-releases.
