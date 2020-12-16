% \file Main_compare.m
%  \brief Main function for SU2-Nastran postprocessing
%  \authors Nicola Fonzi, Vittorio Cavalieri
%  \version 7.0.8 "Blackbird"
%
% SU2 Project Website: https://su2code.github.io
%
% The SU2 Project is maintained by the SU2 Foundation
% (http://su2foundation.org)
%
% Copyright 2012-2020, SU2 Contributors (cf. AUTHORS.md)
%
% SU2 is free software; you can redistribute it and/or
% modify it under the terms of the GNU Lesser General Public
% License as published by the Free Software Foundation; either
% version 2.1 of the License, or (at your option) any later version.
%
% SU2 is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
% Lesser General Public License for more details.
%
% You should have received a copy of the GNU Lesser General Public
% License along with SU2. If not, see <http://www.gnu.org/licenses/>.

clear all; close all; clc

% This script uses Theodorsen theory to compute the analytic response of
% the profile as a function of the Mach number
ObtainTheoResults

% This script simply postprocess the results from SU2
ObtainSU2Results

save_flag = true;

U_su2 = [su2.U];
U_theo = [theo.U];
if any(U_su2 ~= U_theo)
    error('Velocities not coincident');
end

Folders = {'Ma01','Ma02','Ma03','Ma0357','Ma0364'};
Ma = [0.1,0.2,0.3,0.357,0.364];

for i = 1:length(U_su2)

h = figure;
title(strcat('Mach = ',num2str(Ma(i))));
hold on;
plot(theo(i).t,theo(i).alpha*180/pi,'LineWidth',1);
plot(su2(i).t,su2(i).alpha*180/pi,'r','LineWidth',1);
xlim([0,4]);
xlabel('Time [s]');
ylabel('\alpha [deg]');
legend('Theodorsen','SU2');
if save_flag
    saveas(h,strcat('alpha_Ma=',num2str(Ma(i)),'.png'));
end

h = figure;
title(strcat('Mach = ',num2str(Ma(i))));
hold on;
plot(theo(i).t,theo(i).h,'LineWidth',1);
xlim([0,4]);
xlabel('Time [s]');
ylabel('Plunge [m]');
plot(su2(i).t,su2(i).h,'r','LineWidth',1);
legend('Theodorsen','SU2');
if save_flag
    saveas(h,strcat('h_Ma=',num2str(Ma(i)),'.png'));
end

h = figure(1000);
legend('Pitch mode Theodorsen','Plunge mode Theodorsen','Pitch mode SU2','Plunge mode SU2','Location','southeast');
ylim([0 1.2])
xlabel('Mach number');
ylabel('\omega/\omega_{\alpha}');
if save_flag
    saveas(h,'Freq.png');
end
end

