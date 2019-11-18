<div align="center">
  <h1>osu! Rank Tracker</h1>

<p>A Discord bot that keeps track of members' osu! ranks and updates their roles accordingly.</p>
</div>

⚠️ <b>This bot is not made with scalability in mind. It is made for the purpose of being used in the osu!Norge Discord server. If you decide to use this code, and you don't have the same role setup as the osu!Norge Discord, it will break.</b> ⚠️

<br>

<h3>Table of Contents</h3>

* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installing & Running](#installing--running)
* [Built With](#built-with)
* [Contributing](#contributing)
* [Authors](#authors)
* [License](#license)
* [Acknowledgments](#acknowledgments)

<br>

<h2 align="center">Getting Started</h2>

<h3>Prerequisites</h3>

* [Python](https://github.com/python/cpython) 3.6 or newer
* A [MongoDB](https://github.com/mongodb/mongo) Database

<br>

<h3>Installing & Running</h3>

*Assming that you have set your Python 3 path to `python` and you have set up a database.*

* Install the required Python modules:
  ```
  python -m pip install -r requirements.txt
  ```

* Rename the [config.yaml.example](https://github.com/osu-Norge/osu-rank-tracker/blob/master/config.yaml.example) file to `config.yaml` and replace the values inside the file with your own.

* Run the bot
  ```
  python run.py
  ```

<br>

<h2 align="center">Built With</h2>

* [Discord.py](https://github.com/Rapptz/discord.py)
* [PyMongo](https://github.com/mongodb/mongo-python-driver)
<br><br>
...and all the other modules listed in the [requirements.txt](https://github.com/osu-Norge/osu-rank-tracker/blob/master/requirements.txt) file.

<br>

<h2 align="center">Contributing</h2>

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

<br>

<h2 align="center">Authors</h2>

* [LBlend](https://github.com/LBlend) - *Initial work*

Click [here](https://github.com/osu-Norge/osu-rank-tracker/contributors) to see the full list of contributors.

<br>

<h2 align="center">License</h2>

Mozilla Public License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.

<br>

<h2 align="center">Acknowledgments</h2>

We want to thank the following people:

* [Ev-1](https://github.com/Ev-1) for coming up with a better way to calculate which role that should be given based on the rank - ([code](https://github.com/osu-Norge/osu-rank-tracker/blob/master/cogs/utils/OsuUtils.py#L42))
* [PurpleBooth](https://github.com/PurpleBooth) for creating the [README template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) used to write what you're looking at right now :)

and these people for their indirect contributions to the project. Their code is not necessary in order for the bot to operate however their code is used in the production version of the bot and they deserve credit nonetheless:

* [nitros12](https://github.com/nitros12) for writing the [Eval.py](https://github.com/osu-Norge/osu-rank-tracker/blob/master/cogs/Eval.py) cog - ([original code](https://gist.github.com/nitros12/2c3c265813121492655bc95aa54da6b9))
* [EvieePy](https://github.com/EvieePy) for writing a template for the [Errors.py](https://github.com/osu-Norge/osu-rank-tracker/blob/master/cogs/Errors.py) cog - ([original code](https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612))

<br>

##
<div align="center">
  <h3>Project developed by</h3>
  <a href="https://discord.gg/Y7zyjGU"><img src="https://raw.githubusercontent.com/osu-Norge/assets/master/banner.png"></a>
</div>


