clear all 
close all 

% This file will only works on data collected after Feb 6. 

addpath('DriftStudyData');
addpath('RawLogs');

files = {'05_03_17_sherry_walk_flat.csv', '05_03_17_shahid_walk_flat.csv',... 
         '05_03_17_arbaaz_walk_flat.csv'};

     
step_t_total = {};
step_l_total = {}; 
step_h_total = {};

mean_dt = 0.012;
fs = 1/mean_dt;

% Kalman Filter for Positioning    
A = [1      mean_dt     -(mean_dt^2)/2;...
     0      1           -mean_dt;...
     0      0           1];

B = [mean_dt^2/2; mean_dt; 0];
C = [1 mean_dt -(mean_dt^2)/2];

Plant = ss(A,[B B],C,0,-1,'inputname',{'u' 'w'},'outputname','y');
Q = 0.5; % TODO Estimate
% R = [0.1      0     0;...
%      0      0.1     0;...
%      0      0     0.1];

R = 0.2; % TODO Get from Datasheet
[kalmf,L,P,M] = kalman(Plant,Q,R);

a = A;
b = [B B 0*B];
c = [C;C];
d = [0 0 0;0 0 1];
Pl = ss(a,b,c,d,-1,'inputname',{'u' 'w' 'v'},'outputname',{'y' 'yv'});  
sys = parallel(Pl,kalmf,1,1,[],[]);
SimModel = feedback(sys,1,4,2,1);   % Close loop around input #4 and output #2
SimModel = SimModel([1 3],[1 2 3]); % Delete yv from I/O list

for f = 1:length(files)
    file = files{f};
    
    % Read in the new data
    data = csvread(file);

    time = data(:,1)/1000; 
    ax = data(:,2); ay = data(:,3); az = data(:,4);
    gx = data(:,5); gy = data(:,6); gz = data(:,7);
    mx = data(:,8); my = data(:,9); mz = data(:,10);
    roll = data(:,11); pitch = data(:,12); yaw = data(:,13); 
    fsr1 = data(:,14); fsr2 = data(:,15); fsr3 = data(:,16); 

    % Highpass filter design 
    fc = 0.2;
    [b,a] = butter(6,fc/(fs/2),'high');
    ax = filter(b,a,ax); ay = filter(b,a,ay); az = filter(b,a,az);
    filt = tf(b, a);
    
    ind = split_step_indices([fsr1 fsr2 fsr3], 0.5);
   
    % Array of Step Times 
    step_time = [];
    step_length = []; 
    step_height = []; 
    disp('Persons steps')
    for i=1:(length(ind)/2)
        s = ind(i*2 - 1);
        e = ind(i*2);
        
        num_pts = length(time(s:e));

        w = zeros(num_pts, 1); %sqrt(Q)*randn(n,1);
        v = zeros(num_pts, 1); %sqrt(R)*randn(n,1);

        [kpx,x] = lsim(SimModel,[w,v,ax(s:e)]);
        [kpy,y] = lsim(SimModel,[w,v,ay(s:e)]);
        [kpz,z] = lsim(SimModel,[w,v,az(s:e)]);

        ye_x = kpx(:,2); % + v;     % measured response
        ye_y = kpy(:,2); % + v;     % measured response
        ye_z = kpz(:,2); % + v;     % measured response

        sl = sqrt(ye_x.^2 + ye_y.^2);
    
        step_height(i) = max(ye_z);
        step_length(i) = max(sl);
        step_time(i) = time(e) - time(s); 
    
    end 
    step_t_total{f} = step_time; 
    step_l_total{f} = step_length; 
    step_h_total{f} = step_height; 
    
end

figure(1)
scatter(step_h_total{1}, step_l_total{1}, 'r'); 
hold on; 
scatter(step_h_total{2}, step_l_total{2}, 'g'); 
scatter(step_h_total{3}, step_l_total{3}, 'b'); 
legend('Person 1', 'Person 2', 'Person 3'); 
xlabel('Step Height (m)','FontSize', 15); 
ylabel('Step Length (m)','FontSize', 15);
title('Cadence vs Step Length','FontSize', 18);


% figure(2)
% scatter([1:length(step_t_total{1})], step_t_total{1}, 'r'); 
% hold on; 
% scatter([1:length(step_t_total{1})],step_t_total{2}, 'g'); 
% scatter(step_t_total{3}, 'b'); 
% legend('Person 1', 'Person 2', 'Person 3', 'FontSize', 15); 
% xlabel('Steps','FontSize', 15); 
% ylabel('Time Per Step (s)','FontSize', 15);
% title('Real Time Cadence','FontSize', 18);
