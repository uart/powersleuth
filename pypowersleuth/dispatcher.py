# Copyright (c) 2012-2013 Andreas Sembrant
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#  - Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  - Neither the name of the copyright holders nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Andreas Sembrant

import sys

import pyscarphase.dispatcher

class Dispatcher(pyscarphase.dispatcher.Dispatcher):

    def __init__(self):
        pyscarphase.dispatcher.Dispatcher.__init__(self)

        import powersleuth_dump
        import powersleuth_plot
        
        self.subcommands["raw-dump"] = self.CmdData(
            func = self.subcommands["dump"].func,
            help = "Dump raw performance counter data"
            )

        self.subcommands["dump"] = self.CmdData(
            func = powersleuth_dump.run,
            help = "Dump power and performance data"
            )
        
        self.subcommands["raw-plot"] = self.CmdData(
            func = self.subcommands["plot"].func,
            help = "Plot raw performance counter data"
            )

        self.subcommands["plot"] = self.CmdData(
            func = powersleuth_plot.run,
            help = "Plot power and performance data"
            )

def run():
    Dispatcher().dispatch(sys.argv)
