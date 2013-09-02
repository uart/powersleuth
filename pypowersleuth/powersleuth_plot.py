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

import matplotlib.cm 
import matplotlib.pyplot as plt

import pyscarphase.proto.meta
import pyscarphase.proto.data

import pyscarphase.util.config
import pyscarphase.plot.phasebar

import pyscarphase.cmd

import pypowersleuth.model.model

class PlotCmd(pyscarphase.cmd.Cmd):


    def __init__(self, args):
        
        #
        pyscarphase.cmd.Cmd.__init__(self)

        #
        self.parse_arguments(args)

    def parse_arguments(self, args):

        #
        self.parser = argparse.ArgumentParser(
            prog=' '.join(args[0:2]), 
            description='Plot ...'
            )

        #
        subparsers = self.parser.add_subparsers(title="What to plot")

        def add_common_args(parser):

            #
            parser.add_argument(
                "profile",
                help="Input profile."
                )

            parser.add_argument(
                "--thread", "-t",
                type=int,
                help="Threads to plot."
                )
            
            parser.add_argument(
                "--cpu-info", 
                help="CPU model."
                )

            parser.add_argument(
                "--frequencies", "-f",
                help="Target frequencies."
                )

            parser.add_argument(
                "--profile-frequency", 
                type=float,
                required=True,
                help="Profile frequency."
                )

            parser.add_argument(
               "--output-file", "-o",
                help="Output file"
                )

        def add_common_heatmap_args(parser):

            parser.add_argument(
                "--vmin", 
                type=float,
                default=None,
                help="Minimum"
                )
            
            parser.add_argument(
                "--vmax",
                type=float,
                default=None,
                help="Maximum"
                )


        def conf_plot_power_heatmap():

            # Add new parser
            sub_parser = subparsers.add_parser(
                'power-heatmap',
                help="Plot power heatmap")

            # 
            sub_parser.set_defaults(func=self.plot_power_heatmap)
            
            # 
            add_common_args(sub_parser)
            
            #
            add_common_heatmap_args(sub_parser)
            
        def conf_plot_performance_heatmap():

            # Add new parser
            sub_parser = subparsers.add_parser(
                'performance-heatmap',
                help="Plot power heatmap")

            # 
            sub_parser.set_defaults(func=self.plot_performance_heatmap)
            
            # 
            add_common_args(sub_parser)
            
            #
            add_common_heatmap_args(sub_parser)

        def conf_plot_energy_heatmap():

            # Add new parser
            sub_parser = subparsers.add_parser(
                'energy-heatmap',
                help="Plot energy heatmap")

            # 
            sub_parser.set_defaults(func=self.plot_energy_heatmap)

            # 
            add_common_args(sub_parser)
            
            #
            add_common_heatmap_args(sub_parser)
            

        conf_plot_power_heatmap()
        conf_plot_performance_heatmap()
        conf_plot_energy_heatmap()

        #
        self.args = self.parser.parse_args(args[2:])


    def run(self):
        self.args.func()
        
    def _get_data(self):
                               
        # Load meta profile
        self.profile = pyscarphase.proto.meta.load_profile(self.args.profile)
        
        #
        self.cpuinfo = pyscarphase.util.config.Config(self.args.cpu_info)
        
        # Load right model
        self.model = pypowersleuth.model.model.load_model(
            self.cpuinfo, self.profile
            )
        
        #   
        if self.args.frequencies:
            
            #
            self.frequencies = []
             
            #      
            for f in self.args.frequencies.split(','):
                self.frequencies.append(float(f))
                
        else:
            
            #
            self.frequencies = self.cpuinfo.cpu.frequencies
            
        self.frequencies.reverse()
                               
        # Get thread to dump
        thread = self.profile.threads[self.args.thread]

        # Open a reader to that thread's datafile
        reader = pyscarphase.proto.data.DataReader(
            os.path.join(
                os.path.split(self.args.profile)[0],
                thread.profile.filename
                ), 
            uuid=thread.profile.uuid
            )

        dm = pyscarphase.util.demultiplexer.Demultiplexer(reader)

        #
        phase_list = []

        #
        power_data, performance_data, energy_data = [], [], []
        for f in self.frequencies:
            power_data.append([])
            performance_data.append([])
            energy_data.append([])
            

        for i, w in enumerate(dm.read()):           
            phase_list.append(w.phase)

            # Get performance counter data
            values = []
            for c in self.profile.performance_counters:
                values.append(w.value(c.id)[0])
                
            # 
            for j, f in enumerate(self.frequencies):

                _values = self.model.fix_counter_values(
                    f, self.args.profile_frequency, values
                    )

                # Estimate executed cycles
                c_est = self.model.estimate_performance(
                    f, self.args.profile_frequency, _values
                    )
                
                # Convert to seconds
                performance = self.model.cycles2seconds(f, c_est)
                
                # Estimate power
                power = self.model.estimate_power(f, c_est, _values)

                # Add data
                power_data[j].append(power)
                performance_data[j].append(performance)
                energy_data[j].append(power * performance)
                
        #
        if len(phase_list) == 0:
            print("Aborting, nothing to plot (ie, no windows in thread)!")
            exit()
                
        return phase_list, power_data, performance_data, energy_data  
    
    def _plot_heatmap(self, phase_list, data):
        
        # Create axis
        #                    l    b     w      h
        pbar_ax = plt.axes([0.1, 0.9, 0.775, 0.025])
        plot_ax = plt.axes([0.1, 0.1, 0.775, 0.75])
        
        cbar_ax = plt.axes([0.9, 0.1, 0.025, 0.75])

        pyscarphase.plot.phasebar.plot(pbar_ax, plot_ax, phase_list)

        # Plot heatmap
        heatmap = plot_ax.imshow(
            data, 
            aspect='auto', 
            interpolation='nearest',
            vmin=self.args.vmin, vmax=self.args.vmax,
            cmap=matplotlib.cm.jet
            )
        
        plot_ax.set_yticks(range(len(self.frequencies)))
        plot_ax.set_yticklabels(self.frequencies)
        plot_ax.set_ylabel("Frequency (GHz)")
        
        plot_ax.set_xlabel("Time (Windows)")
        
        plt.colorbar(heatmap, cax=cbar_ax)
        
        return plot_ax, pbar_ax, cbar_ax
    
    def _save_or_show_plot(self):
                # 
        if self.args.output_file:
            plt.savefig(self.args.output_file)
        else:
            plt.show()

    def plot_power_heatmap(self):
        '''Plot power heatmap.'''
                           
        phase_list, power, performance, energy = \
            self._get_data()

        plot_ax, pbar_ax, cbar_ax = \
            self._plot_heatmap(phase_list, power)

        cbar_ax.set_ylabel("Power (W)")
        
        self._save_or_show_plot()
        
    def plot_performance_heatmap(self):
        '''Plot performance heatmap.'''
                           
        phase_list, power, performance, energy = \
            self._get_data()

        plot_ax, pbar_ax, cbar_ax = \
            self._plot_heatmap(phase_list, performance)
        
        cbar_ax.set_ylabel("Performance (s)")
        
        self._save_or_show_plot()

    def plot_energy_heatmap(self):
        '''Plot energy heatmap.'''
                           
        phase_list, power, performance, energy = \
            self._get_data()

        plot_ax, pbar_ax, cbar_ax = \
            self._plot_heatmap(phase_list, energy)
        
        cbar_ax.set_ylabel("Energy (J)")
        
        self._save_or_show_plot()


def run(args):
    PlotCmd(args).run()


