% \file ObtainTheoResults.m

%  \brief Use Theodorsen theory for the flutter of a flat plate
%  \authors Giampiero Bindolino, Nicola Fonzi, Vittorio Cavalieri
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

% Mach numbers for the analysis
velocities = sqrt(1.4*287*273)*[0.1 0.2 0.3 0.357 0.364];
% velocities = sqrt(1.4*287*273)*linspace(0.1,0.45,10); % Fine vector

theo = cell2struct(cell(4, 1),{'U','t','h','alpha'},1);


plot_time = 0; % If this is set, we will plot, per each Mach number, time histories
plot_fft = 0;  % If this is set, we will plot the FFT per each Mach number
plot_eig = 1;  % If this is set, we will create a figure with the eigenvalues as a function of Ma

ww1 = [];
ww2 = [];
index=1;
for U = velocities
    % Structural definition

    c = 1; % Chord
    b = c/2;
    xf = c/4; % Rotation axis
    xac= c/4; % Aerodynamic center
    e = (xf-xac)/c; %Distance between aerodynamic center and center of rotation, normalised by the chord
    T = 273; % Temperature
    Re = 4e6; % Reynolds number
    muref = 1.716e-5; % Reference viscosity (dynamic) for viscosity model
    Tref = 273.15; % Reference temperature for viscosity model
    SutherlandC = 110.4; %Constant for viscosity model
    visc_dyn= muref*(T/Tref)^1.5*((Tref+SutherlandC)/(T+SutherlandC));
    rho(index) = Re*visc_dyn/U/c;
    Ma(index) = U/sqrt(1.4*287*T);
    % Adimensional parameters
    X = 0.25;
    ra = 0.5;
    wa = 45;
    w_bar = 0.3185;
    % Real parameters of the mechanic system
    wh = w_bar*wa;

    mu = 100;
    M = mu*pi*rho(index)*b^2;
    I = ra^2*M*b^2;
    CI =  0;
    CM =  0;
    KI = wa^2*I;
    KM = wh^2*M;
    Stat = X*M*b;

    % Structural matrices, the first equation is the one for h, then alpha

    MS = [M -Stat ; -Stat I];
    CS = [CM 0 ; 0 CI];
    KS = [KM 0 ; 0 KI];
    AS = [zeros(2,2) eye(2) ; -inv(MS)*KS  -inv(MS)*CS];
    % Aerodynamic definition
    S=c;
    Pdyn = 0.5*rho(index)*U*U;

    % Input matrix from structure to aerodynamic forces
    BUS = .5*rho(index)*U^2*c*[ 0; 0; 2*pi ; 2*pi*(xf - xac)];
    % Aerodynamic matrices given by the added mass effect

    MA = rho(index)*pi*c^2/4*[ -1               -(xf-.5*c) ; ...
        -(xf-.5*c) -(c^2/32+(xf-.5*c)^2)];
    CA = rho(index)*pi*c^2/4*U*[ 0  1 ;  ...
        0 -(.75*c-xf)];
    KA = zeros(2,2);

    % Aeroelastic matrices given by combination of structure and
    % aerodynamics
    MAE = MS-MA;
    CAE = CS-CA;
    KAE = KS-KA;
    % State space approximation of unsteady part of aerodynamics

    A1 = .165;
    b1 = .0455;
    A2 = .335;
    b2 = .30;
    AAS = [0    1 ; -b1*b2*(2*U/c)^2  -(b1+b2)*(2*U/c)];
    BAS = [0;1];
    CAS = [b1*b2/2*(U/b)^2 (A1*b1+A2*b2)*(U/b)];
    DAS = [.5];
    AQS= [0   1   -1/U  (c*.75-xf)/U];
    LA = [eye(2)      zeros(2,2)  zeros(2,2); ...
        zeros(2,2)     MAE      zeros(2,2); ...
        zeros(2,2)  zeros(2,2)  eye(2)];
    RA = [zeros(2,2)  eye(2)  zeros(2,2); ...
        -KAE       -CAE   zeros(2,2) ; ...
        zeros(2,4)         AAS];
    RAA = [BUS*DAS*AQS BUS*CAS ;  BAS*AQS  zeros(2,2)];

    % Total A matric of the aeroelastic system (\dot{x_ae} = AT x_ae + BT u)
    AT=inv(LA)*(RA+RAA);
    % Initial condition for aerodynamcis, as given by no plunge and 5 degrees of pitch
    ZI=-inv(AAS)*BAS*5*pi/180;
    BT=inv(LA)*[0; 0; 0; KI ; 0; 0];DT=[ 0 0 .5*2*pi]';
    CT=[ 1 0 0 0 0 0 ; 0 1 0 0 0 0 ; AQS*pi 2*pi*b1*b2/2*(U/b)^2 2*pi*(A1*b1+A2*b2)*(U/b)];
    % Build the state-space system
    sa=ss(AT,BT,CT,DT);
    Fs=10000;
    % Simulate the system for 10 seconds with sampling frequency Fs

    [Y,T,X]=initial(sa,[0; 5/180*pi; 0 ;0; ZI],0:(1/Fs):10);
    h=-Y(:,1);
    alpha = Y(:,2);
    time = T;
    theo(index).U = velocities(index);
    theo(index).t = time;
    theo(index).h = h;
    theo(index).alpha = alpha;
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
    i0 = 1; % A different starting point for FFT can be decided
    time = time(i0:end);
    h = h(i0:end);
    alpha = alpha(i0:end);
    L = length(h);
    H = fft(h);
    H = abs(H/L);
    H = H(1:floor(L/2)+1);
    H = 2*H;
    A = fft(alpha);
    A = abs(A/L);
    A = A(1:floor(L/2)+1);
    A = 2*A;
    FreqVect = Fs*(0:floor(L/2))/L;
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
    lambda = eig(AT);
    if any(real(lambda)>0)
        fprintf('Warning: eigenvalue has positive real part @ Ma=%.3f\n',Ma(end));
    end

    % In this case the eigenvalues can be computed analitically

    ww = abs(imag(lambda)/45);
    [~,i1] = min(abs(ww-0.3));
    [~,i2] = min(abs(ww-1.1));
    ww1 = [ww1; ww(i1)];
    ww2 = [ww2; ww(i2)];
    index=index+1;
end
if plot_eig
    figure(1000)
    plot(Ma,ww2,'--','LineWidth',2)
    hold on
    plot(Ma,ww1,'--','LineWidth',2)
end



