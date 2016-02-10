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
import errno
import select

_logger = logging.getLogger(__name__)


class Reactor(object):
    '''
    This class is used to execute command(s) monitor(s).
    '''

    def __init__(self):
        '''
        Create a new reactor.
        '''
        self.poller = select.poll()
        self.fd_to_cmd = {}

    def register_command(self, cmd):
        '''
        Register a new ``cmd`` on the reactor.

        This will allow reactor to monitor ``cmd`` output
        and execute ``cmd`` monitor accordingly.
        '''
        self.poller.register(cmd.fileno(), select.POLLIN | select.POLLPRI)
        self.fd_to_cmd[cmd.fileno()] = cmd

        _logger.debug('registered %s', cmd)

    def unregister_command(self, cmd):
        '''
        Unregister a ``cmd``.
        '''
        del self.fd_to_cmd[cmd.fileno()]
        self.poller.unregister(cmd)

        _logger.debug('unregistered %s', cmd)

    def _run(self, ms_timeout):
        if not len(self.fd_to_cmd):
            return 0

        count = self.poller.poll(ms_timeout)
        for fd, __ in count:
            cmd = self.fd_to_cmd.get(fd, None)

            _logger.debug('%s has new output', cmd)
            if cmd:
                cmd.process_output()

        return len(count)

    def run(self, ms_timeout):
        '''
        Wait ``ms_timeout`` for some registered command(s) to generate
        output and execute associated monitor(s).

        Returns
        -------
        int
            The count of command that generated output.
        '''
        try:
            return self._run(ms_timeout)
        except select.error as err:
            if err[0] == errno.EINTR:
                return 0
            raise
