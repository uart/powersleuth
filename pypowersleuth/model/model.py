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

class Model:

    def estimate_performance(self, f_target, f, events):
        """Estimate performance in executed CPU cycles.

        Args:
            f_target[in]   Target frequency to estimate executed cycles for.
            f[in]          Profile: frequency.
            events[in]     Profile: executed cycles

        Returns:
            Estimated number of executed cycles at target frequency.

        """

        raise NotImplementedError

    def estimate_power(self, f_target, c_est, events):
        """Estimate power in Watts.

        Args:
            f_target[in]   Target frequency (in GHz) to estimate power for.
            c_est[in]      Estimated performance (executed cycles).

            events[in]     Profile: a list of profiles values that
                           correlate with power.

        Returns:
            Estimated power in Watts for the target frequency.

        """    

        raise NotImplementedError
    
    def fix_counter_values(self, f_target, f, events):
        """Fix hardware performance counters"""
        
        raise NotImplementedError
    
    def generate_counter_file(self, filename):
        raise NotImplementedError
    
    def cycles2seconds(self, f_target, c):
        return c / (f_target * 1E9) 
    
    
def load_model(cpuinfo, profile = None):
    
    if cpuinfo.cpu.manufacturer.lower() == "intel":
        if cpuinfo.cpu.architecture.lower() == "nehalem":
            from pypowersleuth.model.intel_nehalem import IntelNehalem
            return IntelNehalem(cpuinfo, profile)
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError
    
