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

import pypowersleuth.model.model

class IntelNehalem(pypowersleuth.model.model.Model):

    def __init__(self, cpuinfo, profile):
        self.cpuinfo = cpuinfo
        
        if profile:
                       
            self.c_param_counter_id_map = []
            self.c_param = []
            
            def get_counter_profile_id(name):
                for counter in profile.performance_counters:
                    if counter.name == name:
                        return counter.id
                    
                raise KeyError
            
            # Power
            
            for name, param in self.cpuinfo.model.power.dynamic.c_param_map.iteritems():
                self.c_param_counter_id_map.append(get_counter_profile_id(name))
                self.c_param.append(param)
                
            self.resource_stalls_any_id = \
                get_counter_profile_id("RESOURCE_STALLS.ANY")
                
            # Performance
            
            self.cpu_clk_unhalted_id = \
                get_counter_profile_id("CPU_CLK_UNHALTED")
            
            self.uops_exec_core_stall_cycles_id = \
                get_counter_profile_id("UOPS_EXECUTED.CORE_STALL_CYCLES")
                
            self.longest_lat_cache_miss_id = \
                get_counter_profile_id("LONGEST_LAT_CACHE.MISS")
                
        
    def fix_counter_values(self, f_target, f, events):
        
        events = events[:]
        
        events[self.uops_exec_core_stall_cycles_id] *= \
            self.cpuinfo.model.performance.stall_scaling_factor
        
        events[self.uops_exec_core_stall_cycles_id] = \
            min(
                events[self.uops_exec_core_stall_cycles_id],
                 
                events[self.longest_lat_cache_miss_id] * 
                self.cpuinfo.model.performance.llc_latency * 
                (f_target/self.cpuinfo.cpu.frequencies[-1])
                
                )

        if events[self.resource_stalls_any_id] > \
           events[self.uops_exec_core_stall_cycles_id]:
            
            events[self.resource_stalls_any_id] -= \
                (events[self.uops_exec_core_stall_cycles_id] + 
                 events[self.uops_exec_core_stall_cycles_id] * f_target / f)
                
        return events

        
    def estimate_performance(self, f_target, f, events):

        def _estimate_performance(f_target, f, c, s):
            return (c - s) + s / (f_target / f)
    
        c = events[self.cpu_clk_unhalted_id]
        s = events[self.uops_exec_core_stall_cycles_id]       
       
        return _estimate_performance(f_target, f, c, s)

    def estimate_power(self, f_target, c_est, events):

        def static_power():
            """ Static power = a*f + b """
            return self.cpuinfo.model.power.static.a * f_target + \
                   self.cpuinfo.model.power.static.b

        def dynamic_power():
            """ Dynamic Power = C * f * V^2 """

            # Estimate capacitance
            C = 0.0
            for i in range(len(self.c_param_counter_id_map)):
                C += events[self.c_param_counter_id_map[i]] * self.c_param[i]
            C /= c_est

            # Estimate voltage (V = a*f + b)
            V = self.cpuinfo.model.power.dynamic.a * f_target + \
                self.cpuinfo.model.power.dynamic.b

            # Estimate power
            return C * f_target * (V * V)

        return self.cpuinfo.model.power.k + static_power() + dynamic_power()
    
class IntelWestmere(IntelNehalem):
    
    def __init__(self):
        pass
    

