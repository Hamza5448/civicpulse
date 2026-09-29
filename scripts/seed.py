# ruff: noqa: I001

import asyncio
import sys
import uuid
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.config import get_settings
from app.core.database import create_engine, create_session_factory
from app.db.models.complaint import Category, Complaint, Priority

SEED_ROWS = [
    ("Water line burst near masjid and pani entering two houses", "Street 12", Category.WATER, Priority.HIGH),
    ("Gutter overflow after rain, dirty water standing outside school", "Block B", Category.SANITATION, Priority.HIGH),
    ("Bijli wires hanging low beside the market entrance", "Main Bazaar", Category.ELECTRICITY, Priority.HIGH),
    ("Deep pothole causing bikes to fall near the bus stop", "Canal Road", Category.ROADS, Priority.NORMAL),
    ("Street light is off and the lane becomes dark after maghrib", "Lane 4", Category.STREETLIGHTS, Priority.NORMAL),
    ("Garbage has not been collected for three days", "Green Colony", Category.SANITATION, Priority.NORMAL),
    ("Low water pressure since morning in the upper floors", "Garden Apartments", Category.WATER, Priority.NORMAL),
    ("Transformer making sparks near the clinic, please check urgently", "Clinic Road", Category.ELECTRICITY, Priority.HIGH),
    ("Road surface broken after recent rain and traffic is slow", "Railway Road", Category.ROADS, Priority.NORMAL),
    ("Lamp post flickering outside the girls school", "School Lane", Category.STREETLIGHTS, Priority.LOW),
    ("Sewer smell and blocked drain beside our gali", "Gali 7", Category.SANITATION, Priority.NORMAL),
    ("Water tanker did not arrive in our mohalla today", "Mohalla Noor", Category.WATER, Priority.NORMAL),
    ("Power outage affecting the small shops since afternoon", "Old Market", Category.ELECTRICITY, Priority.NORMAL),
    ("Open manhole on the road is dangerous for children", "Park Street", Category.SANITATION, Priority.HIGH),
    ("Road sign fallen down at the chowk", "Central Chowk", Category.ROADS, Priority.LOW),
    ("Streetlights not working from gate to community hall", "Community Hall Road", Category.STREETLIGHTS, Priority.NORMAL),
    ("Dirty water coming from tap, please inspect the supply", "House 44", Category.WATER, Priority.HIGH),
    ("Electric pole leaning towards the houses after storm", "Storm Lane", Category.ELECTRICITY, Priority.HIGH),
    ("Footpath tiles broken and elderly people are tripping", "Civic Centre", Category.ROADS, Priority.NORMAL),
    ("Waste collection van skipped our street again", "Street 19", Category.SANITATION, Priority.NORMAL),
    ("No light near the bus stand, women feel unsafe at night", "Bus Stand", Category.STREETLIGHTS, Priority.HIGH),
    ("Pressure pipe leaking beside the mosque entrance", "Mosque Road", Category.WATER, Priority.NORMAL),
    ("Power cable exposed near the park boundary", "Family Park", Category.ELECTRICITY, Priority.HIGH),
    ("Potholes on service road damaging rickshaws", "Service Road", Category.ROADS, Priority.NORMAL),
    ("Drain cover missing after the municipal work", "Model Town", Category.SANITATION, Priority.HIGH),
    ("One lamp working out of four on the main lane", "Main Lane", Category.STREETLIGHTS, Priority.LOW),
    ("Water standing outside the clinic after pipe leakage", "Clinic Block", Category.WATER, Priority.HIGH),
    ("Voltage fluctuating and appliances are at risk", "House 18", Category.ELECTRICITY, Priority.HIGH),
    ("Broken road patch near the cricket ground", "Cricket Ground", Category.ROADS, Priority.LOW),
    ("Please remove mixed waste from the corner shop area", "Shop Corner", Category.SANITATION, Priority.NORMAL),
]


async def seed() -> None:
    settings = get_settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    async with session_factory() as session:
        ids = [uuid.uuid5(uuid.NAMESPACE_URL, f"civicpulse:{text}:{location}") for text, location, _, _ in SEED_ROWS]
        existing = set((await session.scalars(select(Complaint.id).where(Complaint.id.in_(ids)))).all())
        created = 0
        for (text, location, category, priority), complaint_id in zip(SEED_ROWS, ids):
            if complaint_id in existing:
                continue
            cat_val = category.value if hasattr(category, "value") else str(category).lower()
            prio_val = priority.value if hasattr(priority, "value") else str(priority).lower()
            session.add(
                Complaint(
                    id=complaint_id,
                    text=text,
                    location=location,
                    category=cat_val,
                    priority=prio_val,
                    ai_summary=text[:140],
                    triaged_by="rules",
                    triage_latency_ms=0,
                )
            )
            created += 1
        await session.commit()
    await engine.dispose()
    print(f"Seed complete: {created} created, {len(SEED_ROWS) - created} already existed.")


if __name__ == "__main__":
    asyncio.run(seed())