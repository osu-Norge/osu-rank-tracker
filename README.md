<div align="center">
  <h1>osu! Rank Tracker</h1>

<p>A Discord bot that keeps track of members' osu! ranks and updates their roles accordingly.</p>
</div>

⚠️ <b>This bot is not made with scalability in mind. It is made for the purpose of being used in the osu!Norge Discord server. If you decide to use this code, and you don't have the correct role setup, it will break.</b> ⚠️

<br>

<h3>Table of Contents</h3>

* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Setup](#setup)
* [Built With](#built-with)
* [Contributing](#contributing)
* [Authors](#authors)
* [License](#license)
* [Acknowledgments](#acknowledgments)

<br>

<h2 align="center">Getting Started</h2>

<h3>Prerequisites</h3>

* A [MongoDB](https://github.com/mongodb/mongo) Database

<h3>Setup</h3>

<details>
  <summary>Manual</summary>

<h3>Additional prerequisites</h3>

* [Python](https://github.com/python/cpython) 3.6+

<h3>Installation</h3>

*Assming that you have set your Python 3 path to `python` and you have set up a database.*

* Install the required Python modules:
  ```
  python -m pip install -r requirements.txt
  ```

* Go to the `src/config` directory & rename the [config.yaml.example](src/config/config.yaml.example) file to `config.yaml`. Replace the values within the config file with your own.

* Return to the [src](src) directory

* Run the bot

  ```cmd
  python src/run.py
  ```
</details>

<details>
  <summary>Docker (not available ATM)</summary>
  
Example docker-compose.yml

NOTE: `config.yaml` needs to exist on the host as a file

```yml
  osu-bot:
    container_name: osu-bot
    image: osu-Norge/osu_rank_tracker
    networks:
      - internal
    volumes:
      - ./config.yaml:/app/data/config.yaml
```
  
</details>

<h2 align="center">Built With</h2>

* [Discord.py](https://github.com/Rapptz/discord.py)
* [PyMongo](https://github.com/mongodb/mongo-python-driver)
<br><br>
...and all the other modules listed in the [requirements.txt](requirements.txt) file.

<br>

<h2 align="center">Contributing</h2>

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

<br>

<h2 align="center">Authors</h2>

* [LBlend](https://github.com/LBlend) - *Initial work*

Click [here](https://github.com/osu-Norge/osu-rank-tracker/contributors) to see the full list of contributors.

<br>

<h2 align="center">License</h2>

Mozilla Public License 2.0 - Please read [LICENSE](LICENSE) for details.

<br>

<h2 align="center">Acknowledgments</h2>

We want to thank the following people:

* [Ev-1](https://github.com/Ev-1) for coming up with a better way to calculate which role that should be given based on the rank - ([code](src/cogs/utils/OsuUtils.py#L49))
* [Roxedus](https://github.com/Roxedus) for adding Docker support
* [PurpleBooth](https://github.com/PurpleBooth) for creating the [README template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) used to write what you're looking at right now :)

and these people for their indirect contributions to the project. Their code is not necessary in order for the bot to operate however their code is used in the production version of the bot and they deserve credit nonetheless:

* [nitros12](https://github.com/nitros12) for writing the [Eval.py](src/cogs/Eval.py) cog - ([original code](https://gist.github.com/nitros12/2c3c265813121492655bc95aa54da6b9))
* [EvieePy](https://github.com/EvieePy) for writing a template for the [Errors.py](src/cogs/Errors.py) cog - ([original code](https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612))

<br>

##
<div align="center">
  <h3>Project developed by</h3>
  <a href="https://discord.gg/Y7zyjGU"><img src="https://raw.githubusercontent.com/osu-Norge/assets/master/banner.png"></a>
</div>


