# Changelog

## [1.1.0](https://github.com/osu-Norge/osu-rank-tracker/compare/1.0.0...1.1.0) (2026-11-04)


### Features

* **database:** apply schema changes through numbered migrations ([f54a4be](https://github.com/osu-Norge/osu-rank-tracker/commit/f54a4beed66bba0046414a7e93a2aece536872a7)), closes [#19](https://github.com/osu-Norge/osu-rank-tracker/issues/19)
* describe slash command parameters ([74f05f5](https://github.com/osu-Norge/osu-rank-tracker/commit/74f05f5aded0dee187436663b427625790f02908))
* show human names in autocomplete role type menu ([dd4aafc](https://github.com/osu-Norge/osu-rank-tracker/commit/dd4aafc0933ef79f792c72fd2680f8607cc35a7e))
* show usernames in blacklists w/ paginator ([266f3f4](https://github.com/osu-Norge/osu-rank-tracker/commit/266f3f49370662985847ec92fc199e218c34c67e))
* show whitelisted coutnries with flags and names ([f998116](https://github.com/osu-Norge/osu-rank-tracker/commit/f998116b57c49746d4f3f6f685c077d16326a93f))


### Bug Fixes

* cache user ranks across servers ([df0e415](https://github.com/osu-Norge/osu-rank-tracker/commit/df0e4153817be66ca65526b6cbddc82bfef983df))
* check osu! API credentials on boot ([abb588e](https://github.com/osu-Norge/osu-rank-tracker/commit/abb588ea5fa5c668bc9f1a511a2ecd450d6815dd)), closes [#2](https://github.com/osu-Norge/osu-rank-tracker/issues/2)
* create guild row on join ([327c6d4](https://github.com/osu-Norge/osu-rank-tracker/commit/327c6d4febb6ae174545e7920260310aa94d50b9))
* don't reset cooldown on cooldown errors ([b2248c2](https://github.com/osu-Norge/osu-rank-tracker/commit/b2248c2a7acbca66714df96b5a2a3323daaa7bcf))
* error_fatal calls passing ctx ([e33119d](https://github.com/osu-Norge/osu-rank-tracker/commit/e33119dab1b03d86afc3e23e1bd2154c33ae6996))
* expand dockerignore ([ba31976](https://github.com/osu-Norge/osu-rank-tracker/commit/ba319764a685809a17f6114763434858643deddd))
* guild leave command ([4a5f38f](https://github.com/osu-Norge/osu-rank-tracker/commit/4a5f38fbdf8d5dd3cece46c7152ff0ae64967adb))
* handle deleted/restricted osu users for blacklist ([a2767d5](https://github.com/osu-Norge/osu-rank-tracker/commit/a2767d53d6007131d5054276f3ab99c813279a9f))
* handle slash command errors without a command ([af2b860](https://github.com/osu-Norge/osu-rank-tracker/commit/af2b860afb95c45744efc6c0a241838221a3d2a7))
* handle unknown blacklist osu users ([fa3e790](https://github.com/osu-Norge/osu-rank-tracker/commit/fa3e7908aa012f052852e2a0db0e82a9ffb925a2))
* handle unloaded cogs for load/unload/reload commands ([c0139f0](https://github.com/osu-Norge/osu-rank-tracker/commit/c0139f09997c222949d40ed424ee76b14626737a))
* keep background loops running after unexpected errors ([4a26c3e](https://github.com/osu-Norge/osu-rank-tracker/commit/4a26c3e05824055cbbd42c6b0eb863d923bd01ab))
* log to console and log/ ([5c8671a](https://github.com/osu-Norge/osu-rank-tracker/commit/5c8671ac79c5681a9c396b061f6f40bb29b37adc))
* make custommsg send the whole message without using " ([9f7629b](https://github.com/osu-Norge/osu-rank-tracker/commit/9f7629b76f90836c6fb5dcd683f4e15c5b9f0ae9))
* mount the config instead of copying it into the image ([3cd806d](https://github.com/osu-Norge/osu-rank-tracker/commit/3cd806d42300bc90b661ff5d2ea37b4fe0220d09))
* raise the actual error on token renewal fail ([8d33396](https://github.com/osu-Norge/osu-rank-tracker/commit/8d33396e56e3ba62e5e894652594169665126b8f))
* reload all cogs in spite of one failing ([d4f6eb6](https://github.com/osu-Norge/osu-rank-tracker/commit/d4f6eb6f207e84209a5873c2eec8faed4df0d2b3))
* remove duplicate slash commands left by dev mode ([e368357](https://github.com/osu-Norge/osu-rank-tracker/commit/e36835762e3062acc4a1d6fe4f474bff2d98024c))
* rename missing_perms to missing_permissions ([19a102b](https://github.com/osu-Norge/osu-rank-tracker/commit/19a102b5ba6506eab47ca7d56b714553aac4b39f))
* report HTTP status on get_me_user fail ([f48069a](https://github.com/osu-Norge/osu-rank-tracker/commit/f48069af015fb605c4b3da068ffc51b3d245eafe))
* send slash command errors as followups when already responded ([93c3823](https://github.com/osu-Norge/osu-rank-tracker/commit/93c382331eb6b309c3a38457eb9747e86f4dc89b))
* share one aiohttp session for all requests ([aaa719b](https://github.com/osu-Norge/osu-rank-tracker/commit/aaa719ba08128d9e65a866eb22826a109f8fbf6e))
* show blacklisted usernames without backslashes and IDs ([e660b4d](https://github.com/osu-Norge/osu-rank-tracker/commit/e660b4d00f3710ab305dabc88900dce515d01828))
* show docker field in botinfo when running docker ([d4caecf](https://github.com/osu-Norge/osu-rank-tracker/commit/d4caecf5c1c8a18af97a009942ee89356b67c21c))
* shut down cleanly on SIGTERM ([967a75f](https://github.com/osu-Norge/osu-rank-tracker/commit/967a75f5ffbe1bb925be972b18393a0ec27fc80e))
* stop NoPrivateMessage and DisabledCommand errors falling through ([b160db9](https://github.com/osu-Norge/osu-rank-tracker/commit/b160db95bcd69521f937ffb959dc3c4e06dd022a))
* store verification expiry in UTC ([704d9f4](https://github.com/osu-Norge/osu-rank-tracker/commit/704d9f4cf66e42995a55dceb1f1529e3cff82809))
* update ranks every 12 hours ([b5c068c](https://github.com/osu-Norge/osu-rank-tracker/commit/b5c068c026f47ab44411535f57614d83bf125992))
* use async db connection pool ([2d10b9a](https://github.com/osu-Norge/osu-rank-tracker/commit/2d10b9aa3b14b0ff2eec53db4dd3867fc4310350))
* use new help command for cogs without subcommands ([a5de3c5](https://github.com/osu-Norge/osu-rank-tracker/commit/a5de3c5f6a4141e523b8f3546178d5453f311083))
* use ON CONFLICT in queries ([c2e4e11](https://github.com/osu-Norge/osu-rank-tracker/commit/c2e4e11a7e7d547b725092b91f44cd8cd84aef77))


### Documentation

* add notes about privileged intents ([c6ea42e](https://github.com/osu-Norge/osu-rank-tracker/commit/c6ea42e215ab9dd12e554ea814aa4fbfe545e07a))
* make docstrings consistent ([4eefc26](https://github.com/osu-Norge/osu-rank-tracker/commit/4eefc26fcf60ff50e580a1d9eaaf7aa668e5e927))
