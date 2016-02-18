'''
The MIT License (MIT)

Copyright (c) 2016 EnyxSA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import logging

from .exceptions import AlreadyStartedException
from .execution import Execution
from .reactor import Reactor

_logger = logging.getLogger(__name__)


class RemoteRun(Execution):
    '''
    This class is used to run a shell execution.

    Attributes
    ----------
    result : int
        The return code of the shell execution.
    '''

    def __init__(self, reactor, host, username, cmd, logfile=None):
        '''
        Create a new shell execution without starting it.

        Parameters
        ----------
        reactor : ``Reactor``
            The reactor used to execute monitors.
        host : str
            The host used to run the shell execution.
        username : str
            The username used to to run the shell execution.
        cmd : str
            A binary or bash-compatible expression. (e.g. 'echo ok && sleep 1')
        logfile : stream
            A file object used to log shell execution output.
        '''
        super(RemoteRun, self).__init__(reactor, logfile)

        self.__host = host
        self.__username = username
        self.__cmd = cmd.replace('"', r'\"')

        _logger.debug('created remote run "%s" as on %s@%s',
                      cmd, username, host)

    def start(self):
        '''
        Start the execution.
        '''
        args = ['-o BatchMode=yes',
                '{0}@{1}'.format(self.__username, self.__host),
                'bash -c "({0})< <(cat; pkill -P $$)"'.format(self.__cmd)]
        self._start('ssh', args)

    def stop(self):
        '''
        Stop the execution.
        '''
        self._send_eof()


def remote_run(host, username, cmd, logfile=None, ms_timeout=-1):
    '''
    Run ``cmd`` on ``host`` as ``username``.

    Log execution output into ``logfile`` if not None.
    Wait ``ms_timeout`` for execution to complete.

    Returns:
    int
        The execution result code.
    '''
    r = Reactor()
    c = RemoteRun(r, host, username, cmd, logfile)

    with c:
        while r.run(ms_timeout) > 0:
            pass

    return c.result
