
% \file readHistoryNodal.m

%  \brief Uses the mode shapes to obtain nodal displacements
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

function [t,ux,uy,uz,vx,vy,vz,ax,ay,az,uxr,uyr,uzr] = readHistoryNodal(path,filename_modal,filename_pch,grid_id,plot_flag)

if nargin < 4
    grid_id = [];
end

if nargin < 5
    plot_flag = false;
end


% Obtain the mode shapes
[ID,GridType,U,Ux,Uy,Uz,K,M,Uxr,Uyr,Uzr,Usp] = readPunchShapes(filename_pch);

% Obtain the mode amplitudes in time

nmodes = size(U,2);
for n = 1:nmodes
    [t,q,qdot,qddot] = readHistoryModal(filename_modal,nmodes,n,false);
    q_mat(n,:) = q';
    qdot_mat(n,:) = qdot';
    qddot_mat(n,:) = qddot';
end


i_G = unique(ID(GridType == 'G',1));
i_S = ID(GridType == 'S',1);




exit_flag = false;

% Multiply the mode shapes for their amplitude to obtian the physical
% coordinates in time

while true
    
    if isempty(grid_id)
        id = str2double(input('ID: ','s'));
    else
        id = grid_id;
        exit_flag = true;
    end
    
    if id == 0
        return;
    end
    
    indexS = find(i_S==id,1);
    indexG = find(i_G==id,1);
    
    if indexS
        figure();
        hold on;
        usp = Usp(indexS,:)*q_mat;
        plot(t,usp);
        xlabel('t');
        ylabel('scalar point');
        title(['ID = ', num2str(id), ': Scalar point']);
        
    elseif indexG
        
        ux = Ux(indexG,:)*q_mat;
        uy = Uy(indexG,:)*q_mat;
        uz = Uz(indexG,:)*q_mat;
        vx = Ux(indexG,:)*qdot_mat;
        vy = Uy(indexG,:)*qdot_mat;
        vz = Uz(indexG,:)*qdot_mat;
        ax = Ux(indexG,:)*qddot_mat;
        ay = Uy(indexG,:)*qddot_mat;
        az = Uz(indexG,:)*qddot_mat;
        uxr = Uxr(indexG,:)*q_mat;
        uyr = Uyr(indexG,:)*q_mat;
        uzr = Uzr(indexG,:)*q_mat;

        if plot_flag
            
            figure();
            hold on;
            subplot(3,1,1);
            plot(t,ux);
            xlabel('t');
            ylabel('ux');
            title(['ID = ', num2str(id), ': Displacement']);
            subplot(3,1,2);
            plot(t,uy);
            xlabel('t');
            ylabel('uy');
            subplot(3,1,3);
            plot(t,uz);
            xlabel('t');
            ylabel('uz');

            figure();
            hold on;
            subplot(3,1,1);
            plot(t,vx);
            xlabel('t');
            ylabel('vx');
            title(['ID = ', num2str(id), ': Velocity']);
            subplot(3,1,2);
            plot(t,vy);
            xlabel('t');
            ylabel('vy');
            subplot(3,1,3);
            plot(t,vz);
            xlabel('t');
            ylabel('vz');

            figure();
            hold on;
            subplot(3,1,1);
            plot(t,ax);
            xlabel('t');
            ylabel('ax');
            title(['ID = ', num2str(id), ': Acceleration']);
            subplot(3,1,2);
            plot(t,ay);
            xlabel('t');
            ylabel('ay');
            subplot(3,1,3);
            plot(t,az);
            xlabel('t');
            ylabel('az');

            figure();
            hold on;
            subplot(3,1,1);
            plot(t,uxr);
            xlabel('t');
            ylabel('uxr');
            title(['ID = ', num2str(id), ': Rotation']);
            subplot(3,1,2);
            plot(t,uyr);
            xlabel('t');
            ylabel('uyr');
            subplot(3,1,3);
            plot(t,uzr);
            xlabel('t');
            ylabel('uzr');
        
        end
        
    else
        fprintf('ID not found\n');
    
    end
    
    if exit_flag
        break
    end


end


