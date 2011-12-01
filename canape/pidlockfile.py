# -*- coding: utf-8 -*-

# Based on the work of Ben Finney <ben+python@benfinney.id.au>
# pidlockfile.py
#
# Copyright © 2008–2009 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Python Software Foundation License, version 2 or
# later as published by the Python Software Foundation.
# No warranty expressed or implied. See the file LICENSE.PSF-2 for details.
import os
import sys
import errno
import time
import signal

__all__ = ["LockError", "UnlockError", "AlreadyLocked", "LockFailed",
           "NotLocked", "NotMyLock", "LockTimeout", "PIDLockFile",
           "RPIDLockFile", "is_pidfile_stale"]

class LockError(Exception):
    """ Base class for error arising from attempts to acquire the lock. """
    pass
class UnlockError(Exception):
    """ Base class for errors arising from attempts to release the lock. """
    pass

class AlreadyLocked(LockError):
    """ Some other thread/process is locking the file. """
    pass
class LockFailed(LockError):
    """ Lock file creation failed for some other reason. """
    pass
class NotLocked(UnlockError):
    """Raised when an attempt is made to unlock an unlocked file."""
    pass
class NotMyLock(UnlockError):
    """Raised when an attempt is made to unlock a file someone else locked. """
    pass
class LockTimeout(LockError):
    """Raised when lock creation fails within a user-defined period of time."""
    pass

class PIDLockFile(object):
    """ Lockfile implemented as a Unix PID file.

    The lock file is a normal file named by the attribute `path`.
    A lock's PID file contains a single line of text, containing
    the process ID (PID) of the process that acquired the lock.
    """

    def __init__(self, path):

        self.path = path

    def read_pid(self):
        """ Get the PID from the lock file.
            """
        return read_pid_from_pidfile(self.path)

    def is_locked(self):
        """ Test if the lock is currently held.

            The lock is held if the PID file for this lock exists.

            """
        return os.path.exists(self.path)

    def i_am_locking(self):
        """ Test if the lock is held by the current process.

        Returns ``True`` if the current process ID matches the
        number stored in the PID file.
        """
        return self.is_locked() and os.getpid() == self.read_pid()

    def acquire(self, timeout=None):
        """ Acquire the lock.

        Creates the PID file for this lock, or raises an error if
        the lock could not be acquired.
        """
        if self.is_locked():
            raise AlreadyLocked()

        end_time = time.time()
        if timeout is not None and timeout > 0:
            end_time += timeout

        while True:
            try:
                write_pid_to_pidfile(self.path)
            except OSError, exc:
                if exc.errno == errno.EEXIST:
                    # The lock creation failed.  Maybe sleep a bit.
                    if timeout is not None and time.time() > end_time:
                        if timeout > 0:
                            raise LockTimeout()
                        else:
                            raise AlreadyLocked()
                    time.sleep(timeout is not None and timeout/10 or 0.1)
                else:
                    raise LockFailed()
            else:
                return

    def release(self):
        """ Release the lock.

            Removes the PID file to release the lock, or raises an
            error if the current process does not hold the lock.

            """
        if not self.is_locked():
            raise NotLocked
        if not self.i_am_locking():
            raise NotMyLock
        remove_existing_pidfile(self.path)

    def break_lock(self):
        """ Break an existing lock.

            Removes the PID file if it already exists, otherwise does
            nothing.

            """
        remove_existing_pidfile(self.path)

    def __enter__(self):
        """
        Context manager support.
        """
        self.acquire()
        return self

    def __exit__(self, *_exc):
        """
        Context manager support.
        """
        self.release()

class RPIDLockFile(PIDLockFile):
    """ Lockfile implemented as a Unix PID file.

    The lock file is a normal file named by the attribute `path`.
    A lock's PID file contains a single line of text, containing
    the process ID (PID) of the process that acquired the lock.
    """

    locks = 0

    def __init__(self, path):
        PIDLockFile.__init__(self, path)

    def acquire(self, timeout=None):
        """ Acquire the lock.

        Creates the PID file for this lock, or raises an error if
        the lock could not be acquired.
        """
        RPIDLockFile.locks += 1

        if self.is_locked():
            if not self.i_am_locking():
                raise AlreadyLocked()
            return

        end_time = time.time()
        if timeout is not None and timeout > 0:
            end_time += timeout

        while True:
            try:
                write_pid_to_pidfile(self.path)
            except OSError, exc:
                if exc.errno == errno.EEXIST:
                    # The lock creation failed.  Maybe sleep a bit.
                    if timeout is not None and time.time() > end_time:
                        if timeout > 0:
                            raise LockTimeout()
                        else:
                            raise AlreadyLocked()
                    time.sleep(timeout is not None and timeout/10 or 0.1)
                else:
                    raise LockFailed()
            else:
                return

    def release(self):
        """ Release the lock.

            Removes the PID file to release the lock, or raises an
            error if the current process does not hold the lock.

            """
        if RPIDLockFile.locks > 1:
            RPIDLockFile.locks -= 1
            return

        if not self.is_locked():
            raise NotLocked
        if not self.i_am_locking():
            raise NotMyLock
        remove_existing_pidfile(self.path)
        RPIDLockFile.locks -= 1

def read_pid_from_pidfile(pidfile_path):
    """ Read the PID recorded in the named PID file.

        Read and return the numeric PID recorded as text in the named
        PID file. If the PID file cannot be read, or if the content is
        not a valid PID, return ``None``.

        """
    pid = None
    try:
        pidfile = open(pidfile_path, 'r')
    except IOError:
        pass
    else:
        # According to the FHS 2.3 section on PID files in /var/run:
        #
        #   The file must consist of the process identifier in
        #   ASCII-encoded decimal, followed by a newline character.
        #
        #   Programs that read PID files should be somewhat flexible
        #   in what they accept; i.e., they should ignore extra
        #   whitespace, leading zeroes, absence of the trailing
        #   newline, or additional lines in the PID file.

        line = pidfile.readline().strip()
        try:
            pid = int(line)
        except ValueError:
            pass
        pidfile.close()

    return pid


def write_pid_to_pidfile(pidfile_path):
    """ Write the PID in the named PID file.

        Get the numeric process ID (“PID”) of the current process
        and write it to the named file as a line of text.

        """
    open_flags = (os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    open_mode = 0644
    pidfile_fd = os.open(pidfile_path, open_flags, open_mode)
    pidfile = os.fdopen(pidfile_fd, 'w')

    # According to the FHS 2.3 section on PID files in /var/run:
    #
    #   The file must consist of the process identifier in
    #   ASCII-encoded decimal, followed by a newline character. For
    #   example, if crond was process number 25, /var/run/crond.pid
    #   would contain three characters: two, five, and newline.

    line = "%d\n" % os.getpid()
    pidfile.write(line)
    pidfile.close()


def remove_existing_pidfile(pidfile_path):
    """ Remove the named PID file if it exists.

        Removing a PID file that doesn't already exist puts us in the
        desired state, so we ignore the condition if the file does not
        exist.

        """
    try:
        os.remove(pidfile_path)
    except OSError, exc:
        if exc.errno == errno.ENOENT:
            pass
        else:
            raise

def is_pidfile_stale(pidfile):
    """ Determine whether a PID file is stale.

        Return ``True`` (“stale”) if the contents of the PID file are
        valid but do not match the PID of a currently-running process;
        otherwise return ``False``.

        """
    result = False

    pidfile_pid = pidfile.read_pid()
    if pidfile_pid is not None:
        try:
            os.kill(pidfile_pid, signal.SIG_DFL)
        except OSError, exc:
            if exc.errno == errno.ESRCH:
                # The specified PID does not exist
                result = True

    return result
