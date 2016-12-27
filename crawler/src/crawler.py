from Fetcher import Fetcher
from Downloader import Downloader
import queue
import config
import logging

logger = logging.getLogger(__name__)


def main():
    # create share queue
    SHARE_Q = queue.Queue()

    # According to configuration, start a thread for fetch
    # history data since last fetch or not.
    if (config.FetchHistory):
        historyFetcher = Fetcher(SHARE_Q)
        historyFetcher.start()

    # Start Fetcher fetch new metadata, and put into share queue
    updateFetcher = Fetcher(SHARE_Q, config.update_interval_sec)
    updateFetcher.start()

    # Start a downloader, get one metadata from queue,
    # then download open data and archive into ckan
    downloader = Downloader(SHARE_Q)
    downloader.start()


if __name__ == "__main__":
    # using python logging in multiple modules
    # Ref: http://stackoverflow.com/questions/15727420/using-python-logging-in-multiple-modules
    import logging.config
    logging.config.fileConfig(config.logging_configure_file,
                              defaults=None,
                              disable_existing_loggers=False)
    main()
