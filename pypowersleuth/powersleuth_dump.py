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

import os.path, sys, argparse

import pyscarphase.proto.data
import pyscarphase.proto.meta

import pyscarphase.cmd

import pyscarphase.util.config
import pyscarphase.util.demultiplexer

import pyscarphase.scarphase_dump

import pypowersleuth.model.model

class DumpCmd(pyscarphase.cmd.Cmd):

    def __init__(self, args):
        
        #
        pyscarphase.cmd.Cmd.__init__(self)

        #
        self.parse_arguments(args)

    def parse_arguments(self, args):

        #
        parser = argparse.ArgumentParser(
            prog=' '.join(args[0:2]),
            description='Dump data to other formats.'
            )

        subparsers = parser.add_subparsers(title="What to dump")

        def add_common_args(parser):
            '''Add common arguments to all "dump" sub commands.'''

            parser.add_argument(
                "profile",
                help="Input profile."
                )

            parser.add_argument(
                "--thread", "-t",
                type=int,
                required=True,
                help="Thread to dump."
                )

            parser.add_argument(
                "--format",
                choices=[ "csv", "prettytable" ], default="prettytable",
                help="Thread to dump."
                )

            parser.add_argument(
                "--frequencies", "-f",
                required=True,
                help="Target frequencies."
                )
            
            parser.add_argument(
                "--profile-frequency", 
                type=float,
                required=True,
                help="Profile frequency."
                )

            parser.add_argument(
                "--cpu-info", 
                required=True,
                help="CPU model."
                )

            parser.add_argument(
                "--output-file", "-o",
                type=argparse.FileType('w'), default=sys.stdout,
                help="Output file"
                )         

        def conf_dump_windows():

            # Add new parser
            sub_parser = subparsers.add_parser(
                'windows',
                help="Dump windows")

            # 
            sub_parser.set_defaults(func=self.dump_windows)
            
            # 
            add_common_args(sub_parser)


        conf_dump_windows()

        self.args = parser.parse_args(args[2:])
        

    def run(self):
        self.args.func()

    def dump_windows(self):
        '''Dump windows.

        '''

        # Load meta profile
        profile = pyscarphase.proto.meta.load_profile(self.args.profile)
        
        #
        cpuinfo = pyscarphase.util.config.Config(self.args.cpu_info)
        
        # Load right model
        model = pypowersleuth.model.model.load_model(cpuinfo, profile)
        
        header = [ "WID", "PID"]

        frequencies = []

        for f in self.args.frequencies.split(','):
            header += [ "Power (W) at %sGHz" % f, "Performance (s) at %sGHz" % f, "Energy (J) at %sGHz" % f]
            frequencies.append(float(f))            

        if self.args.format == "csv":
            writer = pyscarphase.scarphase_dump.CsvOutputWrapper(self.args.output_file, header)
        else:
            writer = pyscarphase.scarphase_dump.PrettyTableWrapper(self.args.output_file, header)

        # Get thread to dump
        thread = profile.threads[self.args.thread]

        # Open a reader to that thread's datafile
        reader = pyscarphase.proto.data.DataReader(
            os.path.join(
                os.path.split(self.args.profile)[0],
                thread.profile.filename
                ), 
            uuid=thread.profile.uuid
            )

        dm = pyscarphase.util.demultiplexer.Demultiplexer(reader)

        for i, w in enumerate(dm.read()):
            row = [i, w.phase]

            # Get performance counter data
            values = []
            for c in profile.performance_counters:
                values.append(w.value(c.id)[0])
                
            # 
            for f in frequencies:

                _values = model.fix_counter_values(
                    f, self.args.profile_frequency, values
                    )

                # Estimate executed cycles
                c_est = model.estimate_performance(
                    f, self.args.profile_frequency, _values
                    )
                
                # Convert to seconds
                performance = model.cycles2seconds(f, c_est)
                
                # Estimate power
                power = model.estimate_power(f, c_est, _values)

                # Add data
                row.append(power)
                row.append(performance)
                row.append(power * performance)
            
            writer.write_row(row)


def run(args):
    DumpCmd(args).run();

