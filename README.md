# CCG Report Center

This application is a reporting dashboard for the Commission of
Counter Ghoul to aid them in their quest of eliminating ghouls
in the fictional universe of Tokyo Ghoul.

It is our phase 4 project submission for the DNA 2025 course.

# Authors

| Name | Email | Roll Number |
| :--: | :---: | :---------: |
| Shrawani Nanda | shrawani.nanda@students.iiit.ac.in | 2024101111 |
| Aarnav Pai | aarnav.pai@research.iiit.ac.in | 2024115013 |
| Neha Prabhu | neha.prabhu@students.iiit.ac.in | 2024101058 |

# Features

This application serves as a web-based reporting database and information management
system for use by the CCG in the mini-world of "Tokyo Ghoul". It allows users to view,
create, and manage data about the series' key entities and events.

- **Authentication**: A simple secret-phrase-based login system to protect data-modifying actions.
- **Dashboard**: A homepage displaying summary statistics for ghouls, investigators, and humans.
- **Entity Management (CRUD)**:
    - **Ghouls**: View list, filter by ward, view detailed profiles (including special types like Chimera or One-Eyed), and update information.
    - **Investigators**: View list and detailed profiles (showing quinques, encounters, and kill records).
    - **Humans**: View list and detailed profiles.
    - **Wards**: View and create new city wards.
    - **Quinques**: View list, see detailed profiles, transfer ownership, and upgrade with kagunes from deceased ghouls.
- **Event Reporting**: Log, view, and manage various event types including general reports, ghoul murders, investigator-ghoul encounters, and investigator killings of ghouls.
- **Rich Data Relationships**: The application displays interconnected data, such as showing a ghoul's known murders, an investigator's kill list, or the specific investigator who killed a deceased character.

# Description of Routes

Route Descriptions:
- **GET /**: Main dashboard showing entity counts.
- **GET /ghouls**: Lists all ghouls, with an optional `?ward=<id>` filter.
- **GET /ghouls/{id}**: Detailed profile for a specific ghoul.
- **POST /ghouls/{id}/update**: Updates a ghoul's information.
- **GET /wards**: Lists all wards.
- **GET /wards/new**: Form to create a new ward.
- **POST /wards/new**: Submits the new ward form.
- **GET /investigators**: Lists all investigators.
- **GET /investigators/{id}**: Detailed profile for a specific investigator.
- **GET /humans**: Lists all humans.
- **GET /humans/{id}**: Detailed profile for a specific human.
- **GET /quinque**: Lists all quinques.
- **GET /quinque/{id}**: Detailed profile for a specific quinque, including upgrade history.
- **GET /quinque/{id}/transfer**: Form to transfer a quinque to another investigator.
- **POST /quinque/{id}/transfer**: Submits the quinque transfer form.
- **GET /quinque/{id}/upgrade**: Form to upgrade a quinque with a new kagune.
- **POST /quinque/{id}/upgrade**: Submits the quinque upgrade form.
- **GET /report**: Lists all general-purpose reports.
- **GET /report/new**: Form to create a new general report.
- **POST /report/new**: Submits the new report form.
- **GET /report/delete**: Page to select a report for deletion.
- **POST /report/delete**: Deletes the selected report.
- **GET /report/murder**: Lists all recorded ghoul murders.
- **GET /report/murder/new**: Form to report a new ghoul murder.
- **POST /report/murder/new**: Submits the new murder report.
- **GET /report/murder/{mur_id}/{vic_id}**: Details of a specific murder.
- **GET /report/encounter**: Lists all recorded encounters.
- **GET /report/encounter/new**: Form to report a new encounter.
- **POST /report/encounter/new**: Submits the new encounter report.
- **GET /report/encounter/{sen_id}/{jun_id}/{ghoul_id}/{time}**: Details of a specific encounter.
- **GET /report/killing**: Lists all recorded investigator killings of ghouls.
- **GET /report/killing/new**: Form to report a new killing.
- **POST /report/killing/new**: Submits the new killing report.
- **GET /report/killing/{ghoul_id}**: Details of a specific killing.
- **GET /report/{id}**: Details of a specific general report.
- **POST /login**: Handles user login.
- **GET /logout**: Handles user logout.

# Instructions to Run Locally

We have tested this application on Python 3.14. We assume it is
compatible with relatively recent version (3.12+), but there are
no guarantees. If you do not have python 3.14, we recommend using
the [uv package manager](https://docs.astral.sh/uv/) to manage
this application instead.

First, however, you need a working MySQL installation. Run the
`src/schema.sql` and `src/populate.sql` files on your MySQL
instance. It will create a database called `tokyo_ghoul`. You
need to set environment variables for the app to use. You can
do so by copying the `.env.example` file to `.env` and then
editing the variables to their correct values. Here's an
example `.env` file:

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=tokyo_ghoul
MYSQL_USER=dna
MYSQL_PASS=dna

# omit to remove the password lock
SECRET_PHRASE="this is a secret"
```

To run this application, with `uv`, run these two commands:

```python
$ uv sync
$ uv run uvicorn src.main_app:app
```

To use pip instead, do:

```python
$ python3 -m venv venv # create a virtual environment
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ uvicorn src.main_app:app
```

# License

This project is licensed to you under the GNU GPL v3. Please see
`LICENSE` for more details.

## Exception

Some data that we have used in the `populate.sql` file was taken from the
[Tokyo Ghoul wiki](https://tokyoghoul.fandom.com). That content is
licensed under the [CC-BY-SA](https://creativecommons.org/licenses/by-sa/3.0/)
