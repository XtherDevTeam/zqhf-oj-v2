import time
import sqlite3
import threading

_lock = threading.Lock()


class Database:
    closing_time = 30 * 60  # 30 min
    databaseObject = {}
    databasePath = ""
    timerEvent = {}
    __operating = False

    def unloadDatabase(self):
        # unload database
        if self.__operating:
            return

        if self.checkConnection():
            # close database
            self.databaseObject.commit()
            self.databaseObject.close()

    def reconnect(self):
        self.databaseObject = sqlite3.connect(self.databasePath, check_same_thread=False,
                                              isolation_level=None)

    def checkConnection(self):
        try:
            self.databaseObject.execute("")
        except:
            return False

        return True

    def open(self, path):
        self.databasePath = path
        self.reconnect()
        self.timerEvent = threading.Timer(self.closing_time, self.unloadDatabase, ())
        pass

    def query_db(self, query, args=(), one=False):
        if not self.checkConnection():
            self.reconnect()
        else:
            # reopen database connection
            self.timerEvent.cancel()
            self.timerEvent = threading.Timer(self.closing_time, self.unloadDatabase, ())

        # wait
        while self.__operating:
            time.sleep(0.02)

        self.__operating = True

        cur = self.databaseObject.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        self.databaseObject.commit()

        self.__operating = False

        return (rv[0] if rv else None) if one else rv

    def close(self):
        self.timerEvent.cancel()
        self.databaseObject.close()


# open a database connection
def connect(path):
    db = Database()
    db.open(path)
    return db
