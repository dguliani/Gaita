clear all 
close all 

% This file will only works on data collected after Feb 6. 

addpath('DriftStudyData');
addpath('RawLogs');

% Read in the new data
% cal_data = csvread('16_01_17_raw_log_stationary.csv');
data = csvread('05_03_17_sherry_walk_flat.csv');

time = data(:,1)/1000; 
ax = data(:,2); ay = data(:,3); az = data(:,4);
gx = data(:,5); gy = data(:,6); gz = data(:,7);
mx = data(:,8); my = data(:,9); mz = data(:,10);
roll = data(:,11); pitch = data(:,12); yaw = data(:,13); 
fsr1 = data(:,14); fsr2 = data(:,15); fsr3 = data(:,16); 

mean_dt = mean(diff(time,[],1));  
mean_dt = 0.01;
fs = 1/mean_dt;

% Axis correction (fix later) 
% yaw = yaw.*(pi/180); % About z
% roll = roll.*(pi/180); % About y
% pitch = pitch.*(pi/180); % About x
% 
% for i=1:length(ax)
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
[b,a] = butter(6,fc/(fs/2),'high');
% filter = tf(b, a);
% freqz(b,a)
ax = filter(b,a,ax); ay = filter(b,a,ay); az = filter(b,a,az);
filt = tf(b, a);

ind = split_step_indices([fsr1 fsr2 fsr3], 0.5);

% Array of Step Times 
step_time = [];
step_length = []; 
step_height = []; 

% Kalman Filter for Positioning    
A = [1      mean_dt     -(mean_dt^2)/2;...
     0      1           -mean_dt;...
     0      0           1];

B = [mean_dt^2/2; mean_dt; 0];

C = [1 mean_dt -(mean_dt^2)/2];

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


figure(2)
for i=1:(length(ind)/2)
    s = ind(i*2 - 1);
    e = ind(i*2);
    
    % Computing Step Time
    step_time(i) = time(e) - time(s); 
    
    num_pts = length(time(s:e));
    
    rng default
    w = zeros(num_pts, 1); %sqrt(Q)*randn(n,1);
    v = zeros(num_pts, 1); %sqrt(R)*randn(n,1);

    [kpx,x] = lsim(SimModel,[w,v,ax(s:e)]);
    [kpy,y] = lsim(SimModel,[w,v,ay(s:e)]);
    [kpz,z] = lsim(SimModel,[w,v,az(s:e)]);

    ye_x = kpx(:,2); % + v;     % measured response
    ye_y = kpy(:,2); % + v;     % measured response
    ye_z = kpz(:,2); % + v;     % measured response
    
    sl = sqrt(ye_x.^2 + ye_y.^2)
    step_height(i) = max(ye_z);
    step_length(i) = max(sl);
    
    subplot(3,1,1);
    plot(time(s:e) - time(s), ye_x); hold on;
    subplot(3,1,2);
    plot(time(s:e) - time(s), ye_y); hold on;
    subplot(3,1,3);
    plot(time(s:e) - time(s), ye_z); hold on;
end 

mean_dt = mean(diff(time,[],1)); 
fs = 1/mean_dt; % 100 Hz Sampling
num_pts = length(time); 
acc_raw = [ax ay az]; 

figure(1)
subplot(2,1,1); hold on; grid on; 
scatter([1:length(step_time)], step_time, 'r');
xlabel('Step Number'); 
ylabel('Time [s]');  
title('Step Times'); 

subplot(2,1,2); hold on; grid on; 
scatter(step_length, step_height, 'b'); 
xlabel('Step Length'); 
ylabel('Step Height');  
% title('Step Times'); 
% plot(time, fsr2, 'g');
% plot(time, fsr3, 'b');
% plot(time, temp);
% legend('x','y','z');

mean(step_time)
mean(step_length)
mean(step_height)

raw_plot(data);