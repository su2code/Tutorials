%!/usr/bin/env matlab

%% \file LUTWriter.m
%  \brief Example MATLAB script for generating a look-up table file 
%   compatible with the CDataDriven_Fluid class in SU2.
%  \author E.C.Bunschoten
%  \version 7.5.1 "Blackbird"
%
% SU2 Project Website: https://su2code.github.io
%
% The SU2 Project is maintained by the SU2 Foundation
% (http://su2foundation.org)
%
% Copyright 2012-2023, SU2 Contributors (cf. AUTHORS.md)
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

% make print(*args) function available in PY2.6+, does'nt work on PY < 2.6

% CoolProp input data file.
input_datafile = "Air_dataset_full.csv";

% Data point frequency (the larger, the coarser the table).
data_freq = 2;

% LUT output file name.
output_LUTfile = "reftable.drg";

%% provide import data file
% space delimited
data_ref = importdata(input_datafile);

% Identify data entries
rho = data_ref.data(1:data_freq:end, 1);
e = data_ref.data(1:data_freq:end, 2);
s = data_ref.data(1:data_freq:end, 3);
ds_de = data_ref.data(1:data_freq:end, 4);
ds_drho = data_ref.data(1:data_freq:end, 5);
d2s_de2 = data_ref.data(1:data_freq:end, 6);
d2s_dedrho = data_ref.data(1:data_freq:end, 7);
d2s_drho2 = data_ref.data(1:data_freq:end, 8);

rho_min = min(rho);
rho_max = max(rho);
e_min = min(e);
e_max = max(e);

% Normalize density and energy
rho_norm = (rho - rho_min)/(rho_max - rho_min);
e_norm = (e - e_min)/(e_max - e_min);

%% Define table connectivity
T = delaunayTriangulation(rho_norm, e_norm);

data_LUT = [rho, e, s, ds_de, ds_drho, d2s_de2, d2s_dedrho, d2s_drho2];

[~, boundNodes] = boundaryFacets(alphaShape(rho_norm, e_norm, 0.05));
hullIDs = find(ismember([rho_norm, e_norm], boundNodes, "rows"));

%% Write table data to output
fid = fopen(output_LUTfile, 'w+');

header = ['Dragon library' newline newline];
    
header = [header '<Header>' newline];

header = [header '[Version]' newline '1.0.1' newline newline];

header = [header '[Number of points]' newline];
header = [header sprintf('%3d',length(rho)) newline newline];
    
header = [header '[Number of triangles]' newline];
header = [header sprintf('%3d',length(T.ConnectivityList)) newline newline];

header = [header '[Number of hull points]' newline];
header = [header sprintf('%3d',length(hullIDs)) newline newline];

header = [header '[Number of variables]' newline];
header = [header sprintf('%3d',8) newline newline];

header = [header '[Variable names]' newline];
header = [header sprintf('1:Density\n2:Energy\n3:s\n4:dsde_rho\n5:dsdrho_e\n6:d2sde2\n7:d2sdedrho\n8:d2sdrho2\n')];

header = [header newline '</Header>' newline newline];
header = [header '<Data>'];

fprintf(fid,'%s', header);
printformat = '\n';
for iTabVar=1:8
    printformat = [printformat '%.14e\t'];
end
fprintf(fid,printformat,data_LUT');
fprintf(fid,'%s', newline);
fprintf(fid,'%s', '</Data>');

fprintf(fid,'%s', newline);
fprintf(fid,'%s', newline);
fprintf(fid,'%s', '<Connectivity>');

printformat = ['\n' '%5i\t' '%5i\t' '%5i\t'];

fprintf(fid,printformat,T.ConnectivityList');

fprintf(fid,'%s', newline);
fprintf(fid,'%s', '</Connectivity>');

%% print hull block
fprintf(fid,'%s', newline);
fprintf(fid,'%s', newline);
fprintf(fid,'%s', '<Hull>');

printformat = ['\n' '%5i\t'];

fprintf(fid,printformat,hullIDs);

fprintf(fid,'%s', newline);
fprintf(fid,'%s', '</Hull>');

%% close .dat file
fclose(fid);