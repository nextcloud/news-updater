import sys
import traceback
import threading
import time
import logging


class Updater:
    """
    Baseclass for implementing your own updater type. Takes care of logging,
    threading and the general workflow
    """

    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def run(self):
        single_run = self.config.mode == 'singlerun'
        if single_run:
            self.logger.info('Running update once with %d threads' %
                             self.config.threads)
        else:
            self.logger.info(('Running update in an interval of %d seconds '
                              'using %d threads') % (self.config.interval,
                                                     self.config.threads))
        while True:
            self.start_time = time.time()  # reset clock
            try:
                self.before_update()
                feeds = self.all_feeds()

                threads = []
                for num in range(0, self.config.threads):
                    thread = self.start_update_thread(feeds)
                    thread.start()
                    threads.append(thread)
                for thread in threads:
                    thread.join()

                self.after_update()

                if single_run:
                    return
                # wait until the interval finished to run again and subtract
                # the update run time from the interval
                update_duration_seconds = int((time.time() - self.start_time))
                timeout = self.config.interval - update_duration_seconds
                if timeout > 0:
                    self.logger.info(('Finished updating in %d seconds, '
                                      'next update in %d seconds') %
                                     (update_duration_seconds, timeout))
                    time.sleep(timeout)
            except (Exception) as e:
                self.logger.error('%s: Trying again in 30 seconds' % e)
                traceback.print_exc(file=sys.stderr)
                time.sleep(30)

    def before_update(self):
        raise NotImplementedError

    def start_update_thread(self, feeds):
        raise NotImplementedError

    def all_feeds(self):
        raise NotImplementedError

    def after_update(self):
        raise NotImplementedError


class UpdateThread(threading.Thread):
    """
    Baseclass for the updating thread which executes the feed updates in
    parallel
    """
    lock = threading.Lock()

    def __init__(self, feeds, logger):
        super().__init__()
        self.feeds = feeds
        self.logger = logger

    def run(self):
        while True:
            with UpdateThread.lock:
                if len(self.feeds) > 0:
                    feed = self.feeds.pop()
                else:
                    return
            try:
                self.logger.info('Updating feed with id %s and user %s' %
                                 (feed.feedId, feed.userId))
                self.update_feed(feed)
            except (Exception) as e:
                self.logger.error(e)
                traceback.print_exc(file=sys.stderr)

    def update_feed(self, feed):
        """
        Updates a single feed
        feed: the feed object containing the feedId and userId
        """
        raise NotImplementedError
