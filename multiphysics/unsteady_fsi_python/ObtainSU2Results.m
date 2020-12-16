% \file ObtainSU2Results.m
%  \brief Retrives the SU2-Nastran results
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

Folders = {'Ma01','Ma02','Ma03','Ma0357','Ma0364'};
Ma = [0.1,0.2,0.3,0.357,0.364];
su2 = cell2struct(cell(4, 1),{'U','t','h','alpha'},1);


plot_eig = 1;  % If this is set, we will create a figure with the eigenvalues as a function of Ma
plot_time = 0; % If this is set, we will plot, per each Mach number, time histories
plot_fft = 0;  % If this is set, we will plot the FFT per each Mach number

index=1;
for i = 1:length(Folders)
    filename_modal = strcat(Folders{i},filesep,'StructHistoryModal.dat');
    filename_pch = strcat(Folders{i},filesep,'modal.pch');
    grid_id = 11; % This is the ID of the rotation axis point... check the FEM model to see
    [t,ux,uy,uz,vx,vy,vz,ax,ay,az,uxr,uyr,uzr] = readHistoryNodal(path,filename_modal,filename_pch,grid_id);
    h = uy;
    alpha = uzr;
    su2(i).U = sqrt(1.4*287*273)*Ma(i);
    su2(i).t = t - t(1);
    su2(i).h = h;
    su2(i).alpha = alpha;
    if plot_time
        figure
        title(strcat('Mach = ',num2str(velocities(index)/sqrt(1.4*287*273))))
        subplot(2,1,1)
        plot(time,h)
        xlabel('Time [s]')
        ylabel('Plunge [m]')
        subplot(2,1,2)
        plot(time,alpha*180/pi)
        xlabel('Time [s]')
        ylabel('\alpha [deg]')
    end
    i0 = 352; % You can choose when to start the FFT, we exlude the initial transient
    t = t(i0:end);
    h = h(i0:end);
    alpha = alpha(i0:end);

    % This is the mode shape, in terms of rotation and displacement of the
    % master node, at zero velocity. We use it to track the modes in the
    % FFT and correctly compute the eigenvalues.

    X_h = [-0.976826465486179; -0.214032839362979];
    X_a = [0.133783443383256; -0.991010590395743];
    Fs = 1/(t(2)-t(1));
    L = length(h);
    H = fft(h);
    H = abs(H/L);
    H = H(1:floor(L/2)+1);
    H = 2*H;
    FreqVect = Fs*(0:floor(L/2))/L;
    [pksH,locsH] = findpeaks(H,FreqVect);
    A = fft(alpha);
    A = abs(A/L);
    A = A(1:floor(L/2)+1);
    A = 2*A;
    [pksA,locsA] = findpeaks(A,FreqVect);
    pks = [pksH spline(FreqVect,H,locsA); spline(FreqVect,A,locsH) pksA];
    locs = [locsH,locsA];
    [locs,ia] = unique(locs);
    pks = pks(:,ia);
    n = size(pks,2);
    rr_h = zeros(1,n);
    rr_a = zeros(1,n);

    % After the peaks have been found in the FFT, we project everything
    % using the mode shapes above and extract the correct frequencies for
    % the modes

    for j = 1:n
        rr_h(j) = abs(X_h'*pks(:,j)) / (norm(X_h)*norm(pks(:,j)));
        rr_a(j) = abs(X_a'*pks(:,j)) / (norm(X_a)*norm(pks(:,j)));
    end
    [~,ii_h] = max(rr_h);
    [~,ii_a] = max(rr_a);
    f_h(index)= locs(ii_h);
    f_alpha(index)= locs(ii_a);
    if plot_fft
        figure
        title(strcat('Mach = ',num2str(velocities(index)/sqrt(1.4*287*273))))
        subplot(2,1,1)       
        plot(FreqVect,H)
        xlim([0,20]);
        xlabel('Frequency [Hz]')
        ylabel('Plunge [m]')
        subplot(2,1,2)
        plot(FreqVect,A)
        xlim([0,20]);
        xlabel('Frequency [Hz]')
        ylabel('\alpha [deg]')
    end
        index=index+1;
end

if plot_eig
    figure(1000)
    plot(Ma,f_alpha/wa*2*pi,'o','LineWidth',2)
    hold on
    plot(Ma,f_h/wa*2*pi,'o','LineWidth',2)

end

