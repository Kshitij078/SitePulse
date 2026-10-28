
from app.database.connection import Base, SessionLocal, engine
from app.database.models import WebsiteCheck
from app.services.checker import check_website


def main():
    Base.metadata.create_all(bind=engine)

    url = input("Enter website URL: ").strip()

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    result = check_website(url)

    with SessionLocal() as session:
        record = WebsiteCheck(**result)
        session.add(record)
        session.commit()
        session.refresh(record)

        print("\nSitePulse Health Report")
        print("-" * 30)
        print(f"Check ID: {record.id}")
        print(f"Website: {record.url}")
        print(f"Status: {'UP' if record.is_up else 'DOWN'}")
        print(f"HTTP Code: {record.status_code}")
        print(f"Response Time: {record.response_time_ms} ms")
        print(f"Saved to database: Yes")

        if record.error:
            print(f"Error: {record.error}")


if __name__ == "__main__":
    main()
