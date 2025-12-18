from contextlib import asynccontextmanager
from fastapi import (
    FastAPI,
    Depends,
    Path,
    Query,
    Request,
    Form,
    Response,
    Cookie,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Annotated, Literal
import random
import string

from src import template_filters

from .db import connect_to_db, get_db, Cur
from .config import get_config, Config
from . import queries


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await connect_to_db()
    yield
    if app.state.db:
        await app.state.db.close()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="src/templates")
templates.env.filters["pretty_rank"] = template_filters.pretty_rank
sessions = set()

app.mount("/static", StaticFiles(directory="src/static"), "static")


@app.middleware("http")
async def check_login(req: Request, call_next):
    config = get_config()
    if (
        config.secret_phrase is not None
        and not req.url.path.startswith("/login")
        and not req.url.path.startswith("/static")
        and req.cookies.get("session") not in sessions
    ):
        return templates.TemplateResponse(req, "login.html")
    return await call_next(req)


@app.exception_handler(StarletteHTTPException)
async def handle_starlette_http_exception(
    req: Request, e: StarletteHTTPException
):
    return templates.TemplateResponse(
        req,
        "error.html",
        dict(status=e.status_code, detail=e.detail),
        status_code=e.status_code,
    )


@app.get("/", response_class=HTMLResponse)
async def index(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.GET_GHOUL_COUNTS)
    ghouls = await cur.fetchone()
    await cur.execute(queries.GET_INVESTIGATOR_COUNTS)
    investigators = await cur.fetchone()
    await cur.execute(queries.GET_HUMAN_COUNTS)
    humans = await cur.fetchone()
    return templates.TemplateResponse(
        req,
        "dashboard.html",
        dict(
            ghouls=ghouls,
            humans=humans,
            investigators=investigators,
            is_logged_in=session is not None,
        ),
    )


@app.get("/ghouls", response_class=HTMLResponse)
async def ghouls(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
    ward: Annotated[int | Literal[""] | None, Query()] = None,
):
    if ward is not None and ward != "":
        await cur.execute(queries.GHOULS_OF_WARD, (ward,))
    else:
        await cur.execute(queries.GHOULS)
    ghouls = await cur.fetchall()
    await cur.execute(queries.WARDS)
    wards = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "ghouls.html",
        dict(
            is_logged_in=session is not None,
            ghouls=ghouls,
            wards=wards,
            ward=ward,
        ),
    )


@app.get("/ghouls/{id}", response_class=HTMLResponse)
async def ghoul(
    req: Request,
    id: Annotated[str, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.GHOUL_BY_ID, (id,))
    ghoul = await cur.fetchone()
    await cur.execute(queries.GHOUL_CHIMERA, (id,))
    maybe_chimera = await cur.fetchmany()
    if len(maybe_chimera) > 0:
        chimera = maybe_chimera[0]
    else:
        chimera = None
    await cur.execute(queries.GHOUL_ONE_EYED, (id,))
    maybe_one_eyed_ghoul = await cur.fetchmany()
    if len(maybe_one_eyed_ghoul) > 0:
        one_eyed_ghoul = maybe_one_eyed_ghoul[0]
    else:
        one_eyed_ghoul = None
    await cur.execute(queries.GHOUL_MURDERS, (id,))
    murders = await cur.fetchall()
    await cur.execute(queries.GHOUL_ENCOUNTERS, (id,))
    encounters = await cur.fetchall()
    killer = None
    if ghoul["deceased"] == 1:
        await cur.execute(queries.GHOUL_KILLER, (id,))
        killer = await cur.fetchmany()
        if len(killer) == 1:
            killer = killer[0]
    await cur.execute(queries.WARDS)
    wards = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "ghoul.html",
        dict(
            is_logged_in=session is not None,
            ghoul=ghoul,
            chimera=chimera,
            one_eyed_ghoul=one_eyed_ghoul,
            murders=murders,
            encounters=encounters,
            killer=killer,
            wards=wards,
        ),
    )


@app.post("/ghouls/{id}/update", response_class=HTMLResponse)
async def update_ghoul(
    req: Request,
    id: Annotated[str, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    name: str = Form(...),
    gender: str = Form(...),
    birth_date: str = Form(...),
    rc_type: str = Form(...),
    ward: int = Form(...),
):
    await cur.execute(
        queries.UPDATE_GHOUL, (name, gender, birth_date, ward, id)
    )
    await cur.execute(queries.UPDATE_GHOUL_KAGUNE, (rc_type, id))
    await cur._connection.commit()
    return RedirectResponse(url=f"/ghouls/{id}", status_code=303)


@app.get("/wards", response_class=HTMLResponse)
async def wards(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.WARDS)
    wards = await cur.fetchall()
    return templates.TemplateResponse(
        req, "wards.html", dict(is_logged_in=session is not None, wards=wards)
    )


@app.get("/wards/new")
async def wards_new(
    req: Request,
    session: Annotated[str | None, Cookie()] = None,
):
    return templates.TemplateResponse(
        req,
        "new_ward.html",
        dict(is_logged_in=session is not None, wards=wards),
    )


@app.post("/wards/new")
async def create_ward(
    cur: Annotated[Cur, Depends(get_db)],
    name: str = Form(...),
    boundary: str = Form(...),
    number: int = Form(...),
    city: str = Form(...),
):
    await cur.execute(queries.INSERT_WARD, (name, boundary, number, city))
    await cur._connection.commit()
    return RedirectResponse(url="/wards", status_code=303)


# INVESTIGATORS
@app.get("/investigators", response_class=HTMLResponse)
async def investigators(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.INVESTIGATORS)
    investigators = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "investigators.html",
        dict(
            is_logged_in=session is not None,
            investigators=investigators,
        ),
    )


@app.get("/investigators/{id}", response_class=HTMLResponse)
async def investigator(
    req: Request,
    id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.INVESTIGATOR_BY_ID, (id,))
    investigator = await cur.fetchone()
    if not investigator:
        raise StarletteHTTPException(
            status_code=404, detail="Investigator not found"
        )

    await cur.execute(queries.INVESTIGATOR_QUINQUES, (id,))
    quinques = await cur.fetchall()

    await cur.execute(queries.INVESTIGATOR_ENCOUNTERS, (id, id))
    encounters = await cur.fetchall()

    await cur.execute(queries.INVESTIGATOR_KILLINGS, (id,))
    killings = await cur.fetchall()

    killer = None
    if investigator["deceased"] == 1:
        await cur.execute(queries.HUMAN_KILLER, (id,))
        killer = await cur.fetchone()

    return templates.TemplateResponse(
        req,
        "investigator.html",
        dict(
            is_logged_in=session is not None,
            investigator=investigator,
            quinques=quinques,
            encounters=encounters,
            killings=killings,
            killer=killer,
        ),
    )


# HUMANS
@app.get("/humans", response_class=HTMLResponse)
async def humans(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.HUMANS)
    humans = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "humans.html",
        dict(
            is_logged_in=session is not None,
            humans=humans,
        ),
    )


@app.get("/humans/{id}", response_class=HTMLResponse)
async def human(
    req: Request,
    id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.HUMAN_BY_ID, (id,))
    human = await cur.fetchone()
    if not human:
        raise StarletteHTTPException(status_code=404, detail="Human not found")
    killer = None
    if human["deceased"] == 1:
        await cur.execute(queries.HUMAN_KILLER, (id,))
        killer = await cur.fetchone()

    return templates.TemplateResponse(
        req,
        "human.html",
        dict(is_logged_in=session is not None, human=human, killer=killer),
    )


# QUINQUES
@app.get("/quinque", response_class=HTMLResponse)
async def quinques(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.QUINQUES)
    quinques = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "quinques.html",
        dict(
            is_logged_in=session is not None,
            quinques=quinques,
        ),
    )


@app.get("/quinque/{id}/transfer", response_class=HTMLResponse)
async def transfer_quinque_page(
    req: Request,
    id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    # Get the quinque info for the title
    await cur.execute(queries.QUINQUE_BY_ID, (id,))
    quinque = await cur.fetchone()
    if not quinque:
        raise StarletteHTTPException(
            status_code=404, detail="Quinque not found"
        )

    # Get list of investigators to choose from
    await cur.execute(queries.INVESTIGATORS)
    investigators = await cur.fetchall()

    return templates.TemplateResponse(
        req,
        "transfer_quinque.html",
        dict(
            is_logged_in=session is not None,
            quinque=quinque,
            investigators=investigators,
        ),
    )


@app.post("/quinque/{id}/transfer")
async def transfer_quinque(
    id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    new_owner_id: int = Form(...),
):
    await cur.execute(queries.UPDATE_QUINQUE_OWNER, (new_owner_id, id))
    await cur._connection.commit()
    return RedirectResponse(url=f"/quinque/{id}", status_code=303)


@app.get("/quinque/{id}/upgrade", response_class=HTMLResponse)
async def upgrade_quinque_page(
    req: Request,
    id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    # Get quinque info
    await cur.execute(queries.QUINQUE_BY_ID, (id,))
    quinque = await cur.fetchone()
    if not quinque:
        raise StarletteHTTPException(
            status_code=404, detail="Quinque not found"
        )

    # Get investigators (who performed the upgrade)
    await cur.execute(queries.INVESTIGATORS)
    investigators = await cur.fetchall()

    # Get Deceased Ghouls (Potential Donors)
    await cur.execute(queries.DECEASED_GHOULS_FOR_QUINQUE_UPGRADE)
    available_kagune = await cur.fetchall()

    return templates.TemplateResponse(
        req,
        "upgrade_quinque.html",
        dict(
            is_logged_in=session is not None,
            quinque=quinque,
            investigators=investigators,
            kagune=available_kagune,
        ),
    )


@app.post("/quinque/{id}/upgrade")
async def upgrade_quinque(
    id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    investigator_id: int = Form(...),
    kagune_id: int = Form(...),  # Now receiving the existing Kagune ID
):
    # Insert the Upgrade record using the selected existing Kagune ID
    # Note: The database will ensure uniqueness (one Kagune cannot be used for multiple upgrades)
    await cur.execute(
        queries.INSERT_QUINQUE_UPGRADE, (id, investigator_id, kagune_id)
    )

    await cur._connection.commit()
    return RedirectResponse(url=f"/quinque/{id}", status_code=303)


@app.get("/quinque/{id}", response_class=HTMLResponse)
async def quinque(
    req: Request,
    id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.QUINQUE_BY_ID, (id,))
    quinque = await cur.fetchone()
    if not quinque:
        raise StarletteHTTPException(
            status_code=404, detail="Quinque not found"
        )

    await cur.execute(queries.QUINQUE_UPGRADES, (id,))
    upgrades = await cur.fetchall()

    return templates.TemplateResponse(
        req,
        "quinque.html",
        dict(
            is_logged_in=session is not None,
            quinque=quinque,
            upgrades=upgrades,
        ),
    )


# REPORTS


@app.get("/report", response_class=HTMLResponse)
async def reports(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.REPORTS)
    reports = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "reports.html",
        dict(
            is_logged_in=session is not None,
            reports=reports,
        ),
    )


@app.get("/report/new")
async def report_new(
    req: Request,
    session: Annotated[str | None, Cookie()] = None,
):
    return templates.TemplateResponse(
        req,
        "new_report.html",
        dict(is_logged_in=session is not None),
    )


@app.post("/report/new")
async def create_report(
    cur: Annotated[Cur, Depends(get_db)],
    date: str = Form(...),
    text: str = Form(...),
):
    await cur.execute(queries.INSERT_REPORT, (date, text))
    await cur._connection.commit()
    return RedirectResponse(url="/report", status_code=303)


@app.get("/report/delete")
async def report_delete_page(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.REPORTS)
    reports = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "delete_report.html",
        dict(
            is_logged_in=session is not None,
            reports=reports,
        ),
    )


@app.post("/report/delete")
async def delete_report(
    cur: Annotated[Cur, Depends(get_db)],
    report_id: int = Form(...),
):
    await cur.execute(queries.DELETE_REPORT, (report_id,))
    await cur._connection.commit()
    return RedirectResponse(url="/report", status_code=303)


# GHOUL MURDERS
@app.get("/report/murder")
async def murders(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.MURDERS)
    murders = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "murders.html",
        dict(
            is_logged_in=session is not None,
            murders=murders,
        ),
    )


@app.get("/report/murder/new")
async def murder_new(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.GHOULS)
    ghouls = await cur.fetchall()
    await cur.execute(queries.HUMANS)
    humans = await cur.fetchall()
    await cur.execute(queries.WARDS)
    wards = await cur.fetchall()

    return templates.TemplateResponse(
        req,
        "new_murder.html",
        dict(
            is_logged_in=session is not None,
            ghouls=ghouls,
            humans=humans,
            wards=wards,
        ),
    )


@app.post("/report/murder/new")
async def create_murder(
    cur: Annotated[Cur, Depends(get_db)],
    murderer_id: int = Form(...),
    victim_id: int = Form(...),
    ward_id: int = Form(...),
    time: str = Form(...),
):
    await cur.execute(
        queries.INSERT_MURDER, (murderer_id, victim_id, ward_id, time)
    )
    await cur._connection.commit()
    return RedirectResponse(url="/report/murder", status_code=303)


@app.get("/report/murder/{murderer_id}/{victim_id}")
async def murder_detail(
    req: Request,
    murderer_id: Annotated[int, Path()],
    victim_id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.MURDER_BY_ID, (murderer_id, victim_id))
    murder = await cur.fetchone()
    if not murder:
        raise StarletteHTTPException(
            status_code=404, detail="Murder record not found"
        )

    return templates.TemplateResponse(
        req,
        "murder.html",
        dict(
            is_logged_in=session is not None,
            murder=murder,
        ),
    )


# ENCOUNTERS
@app.get("/report/encounter")
async def encounters(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.ENCOUNTERS)
    encounters = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "encounters.html",
        dict(
            is_logged_in=session is not None,
            encounters=encounters,
        ),
    )


@app.get("/report/encounter/new")
async def encounter_new(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.INVESTIGATORS)
    all_investigators = await cur.fetchall()

    senior_investigators = [
        inv for inv in all_investigators if inv["is_senior"]
    ]
    junior_investigators = [
        inv for inv in all_investigators if not inv["is_senior"]
    ]

    await cur.execute(queries.GHOULS)
    ghouls = await cur.fetchall()

    await cur.execute(queries.QUINQUES)
    quinques = await cur.fetchall()

    return templates.TemplateResponse(
        req,
        "new_encounter.html",
        dict(
            is_logged_in=session is not None,
            senior_investigators=senior_investigators,
            junior_investigators=junior_investigators,
            ghouls=ghouls,
            quinques=quinques,
        ),
    )


@app.post("/report/encounter/new")
async def create_encounter(
    cur: Annotated[Cur, Depends(get_db)],
    senior_id: int = Form(...),
    junior_id: int = Form(...),
    ghoul_id: int = Form(...),
    time: str = Form(...),
    death_senior: str = Form(None),
    death_junior: str = Form(None),
    death_ghoul: str = Form(None),
    senior_quinque: int = Form(...),
    junior_quinque: int = Form(...),
):
    # Convert checkbox values to boolean
    death_senior_bool = death_senior == "true"
    death_junior_bool = death_junior == "true"
    death_ghoul_bool = death_ghoul == "true"

    await cur.execute(
        queries.INSERT_ENCOUNTER,
        (
            senior_id,
            junior_id,
            ghoul_id,
            time,
            death_senior_bool,
            death_junior_bool,
            death_ghoul_bool,
            junior_quinque,
            senior_quinque,
        ),
    )
    await cur._connection.commit()
    return RedirectResponse(url="/report/encounter", status_code=303)


@app.get("/report/encounter/{senior_id}/{junior_id}/{ghoul_id}/{time}")
async def encounter_detail(
    req: Request,
    senior_id: Annotated[int, Path()],
    junior_id: Annotated[int, Path()],
    ghoul_id: Annotated[int, Path()],
    time: Annotated[str, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(
        queries.ENCOUNTER_BY_ID, (senior_id, junior_id, ghoul_id, time)
    )
    encounter = await cur.fetchone()
    if not encounter:
        raise StarletteHTTPException(
            status_code=404, detail="Encounter not found"
        )

    return templates.TemplateResponse(
        req,
        "encounter.html",
        dict(
            is_logged_in=session is not None,
            encounter=encounter,
        ),
    )


# KILLINGS
@app.get("/report/killing")
async def killings(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.KILLINGS)
    killings = await cur.fetchall()
    return templates.TemplateResponse(
        req,
        "killings.html",
        dict(
            is_logged_in=session is not None,
            killings=killings,
        ),
    )


@app.post("/report/killing/new")
async def create_killing(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    investigator_id: int = Form(...),
    ghoul_id: int = Form(...),
    quinque_id: int = Form(...),
    ward_id: int = Form(...),
):
    await cur.execute(
        queries.INSERT_KILLING, (investigator_id, ghoul_id, quinque_id, ward_id)
    )
    await cur._connection.commit()
    return RedirectResponse(url="/report/killing", status_code=303)


@app.get("/report/killing/new")
async def killing_new(
    req: Request,
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.INVESTIGATORS)
    investigators = await cur.fetchall()

    await cur.execute(queries.GHOULS)
    ghouls = await cur.fetchall()

    await cur.execute(queries.QUINQUES)
    quinques = await cur.fetchall()

    await cur.execute(queries.WARDS)
    wards = await cur.fetchall()

    return templates.TemplateResponse(
        req,
        "new_killing.html",
        dict(
            is_logged_in=session is not None,
            investigators=investigators,
            ghouls=ghouls,
            quinques=quinques,
            wards=wards,
        ),
    )


@app.get("/report/killing/{ghoul_id}", response_class=HTMLResponse)
async def killing_detail(
    req: Request,
    ghoul_id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.KILLING_BY_GHOUL, (ghoul_id,))
    killing = await cur.fetchone()
    if not killing:
        raise StarletteHTTPException(
            status_code=404, detail="Killing record not found"
        )

    return templates.TemplateResponse(
        req,
        "killing.html",
        dict(
            is_logged_in=session is not None,
            killing=killing,
        ),
    )


@app.get("/report/{id}", response_class=HTMLResponse)
async def report(
    req: Request,
    id: Annotated[int, Path()],
    cur: Annotated[Cur, Depends(get_db)],
    session: Annotated[str | None, Cookie()] = None,
):
    await cur.execute(queries.REPORT_BY_ID, (id,))
    report = await cur.fetchone()
    if not report:
        raise StarletteHTTPException(status_code=404, detail="Report not found")

    return templates.TemplateResponse(
        req,
        "report.html",
        dict(
            is_logged_in=session is not None,
            report=report,
        ),
    )


@app.post("/login")
async def login(
    req: Request,
    secret_phrase: str = Form(...),
    config: Config = Depends(get_config),
):
    if secret_phrase == config.secret_phrase:
        response = RedirectResponse(url="/", status_code=303)
        sid = "".join(random.choice(string.ascii_letters) for _ in range(32))
        sessions.add(sid)
        response.set_cookie(key="session", value=sid, httponly=True)
        return response
    else:
        return templates.TemplateResponse(
            req, "login.html", {"error": "Invalid secret phrase"}
        )


@app.get("/logout")
async def logout(
    response: Response, sid: Annotated[str | None, Cookie()] = None
):
    response = RedirectResponse(url="/", status_code=303)
    if sid is not None and sid in sessions:
        sessions.remove(sid)
    response.delete_cookie(key="session")
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main_app:app", log_level="info", reload=True)
