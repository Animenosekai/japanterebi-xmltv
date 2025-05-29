# japanterebi-xmltv


<img src="./assets/sakayanagi_rounded.png" alt="Sakayanagi" align="right" height="220px">

Easily create XMLTV files.

***Plan your watching journey!***

<br>
<br>

[![EPG Update](https://github.com/Animenosekai/japanterebi-xmltv/actions/workflows/update.yaml/badge.svg)](https://github.com/Animenosekai/japanterebi-xmltv/actions/workflows/update.yaml)
[![GitHub — License](https://img.shields.io/github/license/Animenosekai/japanterebi-xmltv)](https://github.com/Animenosekai/japanterebi-xmltv/blob/master/LICENSE)
[![GitHub top language](https://img.shields.io/github/languages/top/Animenosekai/japanterebi-xmltv)](https://github.com/Animenosekai/japanterebi-xmltv)
![Code Size](https://img.shields.io/github/languages/code-size/Animenosekai/japanterebi-xmltv)
![Repo Size](https://img.shields.io/github/repo-size/Animenosekai/japanterebi-xmltv)
![Issues](https://img.shields.io/github/issues/Animenosekai/japanterebi-xmltv)

## Usage

### API

You can use the [https://animenosekai.github.io/japanterebi-xmltv/guide.xml](https://animenosekai.github.io/japanterebi-xmltv/guide.xml) URL as an XMLTV source in any compatible software.

This pre-built XMLTV file contains EPG data for channels from Japan or with Japanese audio.

<https://github.com/Animenosekai/japanterebi-xmltv/blob/a94b1d2fbcfe855a06925950e12127a8c554b0ef/.github/workflows/update.yaml#L27>

This file is updated every hour using [GitHub Actions](https://github.com/Animenosekai/japanterebi-xmltv/actions/workflows/update.yaml).

But you can also build your own XMLTV file using the different scripts provided in this repository.

### Pre-requisites

The different programs located in the [`scripts`](./scripts/) directory require Python 3.7 to run correctly.

The dependencies are listed in the `requirements.txt` file. You can install them by running:

```bash
python -m pip install -r requirements.txt --upgrade
```

It is recommended to use `git` to have the most up-to-date data from the upstream `iptv-org` database.

If you are cloning the repository using `git`, it is recommended to use the `--depth 1` option to only clone the latest commit, which will save you some bandwidth and disk space.

```bash
git clone --depth 1 https://github.com/Animenosekai/japanterebi-xmltv.git
```

### Scripts

#### Filter

The [`filter.py`](./scripts/filter.py) script filters the different channels from the [`iptv-org/database`](https://github.com/iptv-org/database) repository.

To download the repository, you can run the following command:

```bash
git clone --depth 1 -b main https://github.com/iptv-org/database.git
```

##### CLI

You can run the script with the following command:

```bash
python scripts/filter.py --channels <database/data/channels.csv> --feeds <database/data/feeds.csv> <output_path.json>
```

- [`database/data/channels.csv`](https://github.com/iptv-org/database/blob/master/data/channels.csv) is the path to the channels CSV file from the [`iptv-org/database`](https://github.com/iptv-org/database) repository.
- [`database/data/feeds.csv`](https://github.com/iptv-org/database/blob/master/data/feeds.csv) is the path to the feeds CSV file from the [`iptv-org/database`](https://github.com/iptv-org/database) repository.

You can specify :

- `--language` to filter the channels by language
- `--country` to filter the channels by country
- `--category` to filter the channels by category

You can use those options multiple times to filter the channels by multiple criteria.

The different filters add up, and a union is made between the different filters.

You can also directly use the `--add` or `--remove` options to add or remove channels IDs from the list.

Here is an example output :

```json
[
    {
        "id": "ABEMAAnime.jp",
        "name": "ABEMA Anime",
        "alt_names": [
            "ABEMAアニメ"
        ],
        "network": null,
        "owners": [
            "CyberAgent"
        ],
        "country": "JP",
        "subdivision": null,
        "city": "Shibuya-ku",
        "categories": [
            "animation",
            "kids"
        ],
        "is_nsfw": false,
        "launched": 1522533600.0,
        "closed": null,
        "replaced_by": null,
        "website": "https://abema.tv/now-on-air/abema-anime?lang=en",
        "logo": "https://image.p-c2-x.abema-tv.com/image/channels/abema-anime/logo.png?height=96&quality=75&version=20200413&width=256",
        "feeds": [
            "SD"
        ],
        "has_main_feed": true
    }
]
```

Here is the command used in the workflow:

<https://github.com/Animenosekai/japanterebi-xmltv/blob/ff9cdb5ab5d2e9a635ba3e64b5036894fa043ccc/.github/workflows/update.yaml#L26-L27>

##### Python

You can also use the script as a Python module. It provides a way to convert the CSV file to a list of [`Channel`](./scripts/model.py) objects, which can easily be manipulated.

#### Fetcher

The [`fetcher.py`](./scripts/fetcher.py) gathers the different EPG sites which can be used to create the final EPG.

You need to download the [`iptv-org/epg`](https://github.com/iptv-org/epg) repository to get the different EPG sites first.

```bash
git clone --depth 1 -b master https://github.com/iptv-org/epg.git
```

Then you can run the script with the following command:

```bash
python scripts/fetcher.py --input <input_path.json> --sites epg/sites <output_path.xml>
```

The [`input_path.json`](./channels.json) file should contain the list of channels you want to fetch. It should be generated by the [`filter.py`](#filter) script.

Here is the command used in the workflow:

<https://github.com/Animenosekai/japanterebi-xmltv/blob/ff9cdb5ab5d2e9a635ba3e64b5036894fa043ccc/.github/workflows/update.yaml#L34-L35>

The output is an [XML file](./japanterebi.channels.xml) which can be used with the `grab` command from the [`iptv-org/epg`](https://github.com/iptv-org/epg) repository.

```bash
npm run grab -- --channels=<output_path.xml>
```

#### Fixer

Because sometimes the EPG sites return non-escaped `&` characters, the [`fix.py`](./scripts/fix.py) script fixes the XML file by correctly escaping those characters.

You can run the script with the following command:

```bash
python scripts/fix.py --input <input_path.xml> <output_path.xml>
```

Here is the command used in the workflow:

<https://github.com/Animenosekai/japanterebi-xmltv/blob/0425c2dfd581f11e6e2f062805aab1b19baef998/.github/workflows/update.yaml#L51-L52>

#### Merger

Because the `grab` command gathers information from different EPG sites, the final EPG has multiple redundant entries.

The [`merger.py`](./scripts/merger.py) script merges the different EPG entries into a single one.

You can run the script with the following command:

```bash
python scripts/merger.py --input <input_path.xml> <output_path.xml>
```

The [`input_path.xml`](./guide.xml) file should be the output of the `grab` command, or an equivalent XMLTV-formatted file.

Here is the command used in the workflow:

<https://github.com/Animenosekai/japanterebi-xmltv/blob/ff9cdb5ab5d2e9a635ba3e64b5036894fa043ccc/.github/workflows/update.yaml#L51-L52>

#### Minifier

The [`minify.py`](./scripts/minify.py) script simply minfies the XMLTV file.

You can run the script with the following command:

```bash
python scripts/minify.py --input <input_path.xml> <output_path.xml>
```

> [!NOTE]
> Note that it just removes empty lines for now.

Here is the command used in the workflow:

<https://github.com/Animenosekai/japanterebi-xmltv/blob/ff9cdb5ab5d2e9a635ba3e64b5036894fa043ccc/.github/workflows/update.yaml#L53-L54>
