
import time
from datetime import datetime, timezone

from app.database.connection import SessionLocal
from app.database.models import Incident, MonitoredWebsite, WebsiteCheck
from app.services.checker import check_website


CHECK_INTERVAL = 60


def monitor_website(url: str) -> dict:
    result = check_website(url)

    with SessionLocal() as session:
        previous = (
            session.query(WebsiteCheck)
            .filter(WebsiteCheck.url == url)
            .order_by(WebsiteCheck.id.desc())
            .first()
        )

        session.add(WebsiteCheck(**result))

        if not result["is_up"]:
            if previous is None or previous.is_up:
                incident = Incident(
                    url=url,
                    started_at=datetime.now(timezone.utc),
                    error=result.get("error")
                    or f"HTTP {result.get('status_code')}",
                )
                session.add(incident)
                print(f"INCIDENT STARTED: {url}")

        elif previous is not None and not previous.is_up:
            incident = (
                session.query(Incident)
                .filter(
                    Incident.url == url,
                    Incident.resolved_at.is_(None),
                )
                .order_by(Incident.id.desc())
                .first()
            )

            if incident:
                incident.resolved_at = datetime.now(timezone.utc)
                print(f"INCIDENT RESOLVED: {url}")

        session.commit()

    status = "UP" if result["is_up"] else "DOWN"

    print(
        f"{datetime.now(timezone.utc).isoformat()} | "
        f"{url} | {status} | "
        f"{result.get('response_time_ms')} ms"
    )

    if result.get("error"):
        print(f"Error: {result['error']}")

    return result


def get_active_websites() -> list[str]:
    with SessionLocal() as session:
        websites = (
            session.query(MonitoredWebsite.url)
            .filter(MonitoredWebsite.is_active.is_(True))
            .all()
        )

        return [website.url for website in websites]


def run_monitor() -> None:
    print("SitePulse monitoring started.")
    print(f"Checking active websites every {CHECK_INTERVAL} seconds.")

    while True:
        websites = get_active_websites()

        if not websites:
            print("No websites added yet.")

        for url in websites:
            try:
                monitor_website(url)
            except Exception as error:
                print(f"Monitoring failed for {url}: {error}")

        print(f"Next check in {CHECK_INTERVAL} seconds.")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run_monitor()
