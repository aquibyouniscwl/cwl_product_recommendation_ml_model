import uvicorn
from src.config.settings import settings


def main():
    """
    Launches the recommendation engine API server using Uvicorn.
    """
    uvicorn.run("src.api.app:app", host=settings.HOST, port=settings.PORT, reload=True)


if __name__ == "__main__":
    main()
