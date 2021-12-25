
% \file readHistoryModal.m

%  \brief Reads the StructHistoryModal.dat file
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

function [t,q,qdot,qddot] = readHistoryModal(filename,nmodes,n,display)

if nargin == 2
    n = false;
end

if nargin == 3
    display = false;
end

if ~islogical(display)
    error('display must be logical');
end

fid = fopen(filename);


% Read the formatted file StructHistoryModal.dat. The first three columns
% are always present. Other 3 are added per each mode

formatSpec = '%f%f%f';
for i = 1:nmodes
    formatSpec = [formatSpec, '%f%f%f'];
end
data = textscan(fid,formatSpec,'HeaderLines',1);
data = cell2mat(data);

fclose(fid);

t = data(:,1);


if ~n
    n = str2double(input('n: ','s'));
end
if n > nmodes
    error(['Mode not found. NMODES = ',num2str(nmodes)]);
end

i = 3+(n-1)*3;
q = data(:,i+1);
qdot = data(:,i+2);
qddot = data(:,i+3);

if display
    figure();
    hold on;
    subplot(3,1,1);
    plot(t,q);
    xlabel('t');
    ylabel('$q$','interpreter','latex','FontSize',14);
    title(['Mode n. ', num2str(n)]);
    subplot(3,1,2);
    plot(t,qdot);
    xlabel('t');
    ylabel('$\dot{q}$','interpreter','latex','FontSize',14);
    subplot(3,1,3);
    plot(t,qddot);
    xlabel('t');
    ylabel('$\ddot{q}$','interpreter','latex','FontSize',14);
end


end

