clear all 
close all 

% This file will only works on data collected after January 18. 

addpath('DriftStudyData');
addpath('RawLogs');

% Read in the new data
% cal_data = csvread('16_01_17_raw_log_stationary.csv');
data = csvread('05_03_17_shahid_walk_flat.csv');

time = data(:,1)/1000;
ax = data(:,2);
ay = data(:,3);
az = data(:,4);
gx = data(:,5);
gy = data(:,6);
gz = data(:,7);
mx = data(:,8);
my = data(:,9);
mz = data(:,10);
roll = data(:,11); 
pitch = data(:,12); 
yaw = data(:,13); 

mean_dt = mean(diff(time,[],1)); 
fs = 1/mean_dt; % 100 Hz Sampling

num_pts = length(time); 

acc_raw = [ax ay az]; 

%% Data Processing 
% Axis correction 
% yaw = yaw.*(pi/180); % About z
% roll = roll.*(pi/180); % About y
% pitch = pitch.*(pi/180); % About x
% 
% for i=1:num_pts
%     rz = rotz(yaw(i));
%     ry= rotz(roll(i));
%     rx = rotz(pitch(i));
%     
%     rot = rz*ry*rx;
%     
%     a_temp = [ax(i); ay(i); az(i)];
%     a_new = rot*a_temp;
%     ax(i) = a_new(1);
%     ay(i) = a_new(2);
%     az(i) = a_new(3);
% end

% Highpass filter design 
fc = 0.2;

% d = fdesign.bandstop('Fp1,Fst1,Fst2,Fp2,Ap1,Ast,Ap2', ...
%     0.42,0.44,0.48,0.5,1,60,1);
% Hd = design(d,'equiripple');

[b,a] = butter(6,fc/(fs/2),'high');
[bl,al] = butter(6,20/(fs/2),'low');

ax = filter(b,a,ax); ay = filter(b,a,ay); az = filter(b,a,az);
ax = filter(bl,al,ax); ay = filter(bl,al,ay); az = filter(bl,al,az);
% ax = filter(Hd,ax); ay = filter(Hd,ay); az = filter(Hd,az);
% az = filter(Hd, az); 

L = length(ax);
ax_fft = fft(ax);
ay_fft = fft(ay);
az_fft = fft(az);

P2_x = abs(ax_fft/L);
P1_x = P2_x(1:L/2+1);
P1_x(2:end-1) = 2*P1_x(2:end-1);

P2_y = abs(ay_fft/L);
P1_y = P2_y(1:L/2+1);
P1_y(2:end-1) = 2*P1_y(2:end-1);

P2_z = abs(az_fft/L);
P1_z = P2_z(1:L/2+1);
P1_z(2:end-1) = 2*P1_z(2:end-1);

f = fs*(0:(L/2))/L;
figure(5)
subplot(3,1,1)
plot(f,P1_x); grid on; 
title('Single-Sided Amplitude Spectrum of Stationary IMU Data')
xlabel('Freq (Hz)')
ylabel('X Magnitude')

subplot(3,1,2)
plot(f,P1_y); grid on; 
xlabel('Freq (Hz)')
ylabel('Y Magnitude')

subplot(3,1,3)
plot(f,P1_z); grid on; 
xlabel('Freq (Hz)')
ylabel('Z Magnitude')

% Fix accel with gyro fuse mask
% m = (abs(gx) > 0.08) + (abs(gy) > 0.08) + (abs(gz) > 0.08);
% indices =  find(m==0);
% ax(indices) = 0; 
% ay(indices) = 0; 
% az(indices) = 0; 

% Initializing arrays for numerical integration
vel = zeros(num_pts, 3); pos = zeros(num_pts, 3);

last_acc = [0 0 0]; last_vel = [0 0 0]; last_pos = [0 0 0]; 

vel_rst_ct = 0; 
vel_rst_thd = 5; 
% Velocity Integral [Rectangular]
for i=1:num_pts
    if(i > 1)
        timestep = time(i) - time(i-1);
    else
        timestep = 0;
    end
    vel(i, :) = last_vel + (last_acc*timestep); 
    
    % Velocity reset if no accel for a while 
    if(length( find( abs(last_acc)>0 ) ) == 0 )
        vel_rst_ct = vel_rst_ct + 1; 
    else
        vel_rst_ct = 0; 
    end
    
    if( vel_rst_ct >vel_rst_thd )
        vel(i, :) = zeros(1,3);
        vel_rst_ct = 0; 
    end
    
    last_acc = [ax(i), ay(i), az(i)]; 
    last_vel = vel(i,:); 
end

pos_rst_ct = 0; 
pos_rst_thd = 10; 
% Position Integral [Rectangular]
for i=1:num_pts
    if(i > 1)
        timestep = time(i) - time(i-1);
    else
        timestep = 0;
    end
    pos(i, :) = last_pos + (last_vel*timestep); 
    
    % Position reset if no accel for a while 
%     if(length( find( abs(last_vel)>0 ) ) == 0 )
%         pos_rst_ct = pos_rst_ct + 1; 
%     else
%         pos_rst_ct = 0; 
%     end
%     
%     if( pos_rst_ct >pos_rst_thd )
%         pos(i, :) = zeros(1,3);
%         pos_rst_ct = 0; 
%     end
    
    last_vel = [vel(i, 1), vel(i, 2), vel(i, 3)]; 
    last_pos = pos(i,:); 
end

%% Kalman 
A = [1      mean_dt     -(mean_dt^2)/2;...
     0      1           -mean_dt;...
     0      0           1];
 
B = [mean_dt^2/2; mean_dt; 0];
 
C = [1 mean_dt -(mean_dt^2)/2];
 
D = [(mean_dt^2)/2]; 
 
Plant = ss(A,[B B],C,0,-1,'inputname',{'u' 'w'},'outputname','y');
Q = 1;
R = 1;
[kalmf,L,P,M] = kalman(Plant,Q,R);

a = A;
b = [B B 0*B];
c = [C;C];
d = [0 0 0;0 0 1];
Pl = ss(a,b,c,d,-1,'inputname',{'u' 'w' 'v'},'outputname',{'y' 'yv'});  
sys = parallel(Pl,kalmf,1,1,[],[]);
SimModel = feedback(sys,1,4,2,1);   % Close loop around input #4 and output #2
SimModel = SimModel([1 3],[1 2 3]); % Delete yv from I/O list

% SimModel.InputName
% SimModel.OutputName
n = length(time);
rng default
w = zeros(num_pts, 1); %sqrt(Q)*randn(n,1);
v = zeros(num_pts, 1); %sqrt(R)*randn(n,1);

% [out,x] = lsim(SimModel,[w,v,ax]);
[kpx,x] = lsim(SimModel,[w,v,ax]);
[kpy,y] = lsim(SimModel,[w,v,ay]);
[kpz,z] = lsim(SimModel,[w,v,az]);


yv_x = kpx(:,1) + v;     % measured response
yv_y = kpy(:,1) + v;     % measured response
yv_z = kpz(:,1) + v;     % measured response

%% Plotting
figure(1);
ax1 = subplot(4,1,1); 
hold on; 
grid on; 
plot(time, ax, 'r'); 
plot(time, ay, 'g');
plot(time, az, 'b');
legend('x','y','z');
title('Raw Data'); 

ax2 = subplot(4,1,2); 
hold on; 
grid on; 
plot(time, gx, 'r'); 
plot(time, gy, 'g');
plot(time, gz, 'b');
legend('x','y','z');

ax3 = subplot(4,1,3); 
hold on; 
grid on; 
plot(time, mx, 'r'); 
plot(time, my, 'g');
plot(time, mz, 'b');
legend('x','y','z');

ax4 = subplot(4,1,4); 
hold on; 
grid on; 
plot(time, roll, 'r'); 
plot(time, pitch, 'g');
plot(time, yaw, 'b');
legend('roll','pitch','yaw');

linkaxes([ax1,ax2,ax3, ax4],'x');

figure(2);
ax1 = subplot(3,1,1); 
hold on; 
grid on; 
plot(time, ax, 'r'); 
plot(time, ay, 'g');
plot(time, az, 'b');
legend('x','y','z');
title('Accel to Pos'); 

ax2 = subplot(3,1,2); 
hold on; 
grid on; 
plot(time, vel(:,1), 'r'); 
plot(time, vel(:,2), 'g');
plot(time, vel(:,3), 'b');
legend('x','y','z');

ax3 = subplot(3,1,3); 
hold on; 
grid on; 
plot(time, pos(:,1), 'r'); 
plot(time, pos(:,2) + pos(:,1), 'g');
plot(time, pos(:,3), 'b');
legend('x','y', 'z');

% Temporary plot
figure(3); 
ax1 = subplot(3,1,1); 
hold on; grid on;
plot(time, acc_raw(:,1), 'r');
plot(time, ax, 'b');
legend('Raw x', 'Filtered x'); 
title('Filtered Acceleration'); 

ax2 = subplot(3,1,2); 
hold on; grid on; 
plot(time, acc_raw(:,2), 'r');
plot(time, ay, 'b');
legend('Raw y', 'Filtered y'); 

ax3 = subplot(3,1,3); 
hold on; grid on; 
plot(time, acc_raw(:,3), 'r');
plot(time, az, 'b');
legend('Raw z', 'Filtered z'); 
 
linkaxes([ax1, ax2, ax3], 'x'); 
 
figure(4); 
subplot(3,1,1);
hold on; 
grid on; 
plot(time, yv_x, 'b');
plot(time, pos(:,1), 'r'); 
legend('Kalman Pos x', 'Integration Pos x'); 
title('Kalman Filter Prediction of pos'); 

subplot(3,1,2);
hold on; 
grid on; 
plot(time, yv_y, 'b');
plot(time, pos(:,2), 'r'); 
legend('Kalman Pos y', 'Integration Pos y'); 

subplot(3,1,3);
hold on; 
grid on; 
plot(time, yv_z, 'b');
plot(time, pos(:,3), 'r'); 
legend('Kalman Pos z', 'Integration Pos z'); 
