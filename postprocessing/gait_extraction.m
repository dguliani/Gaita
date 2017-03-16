function [] = gait_extraction(file)
    close all 

    % This file will only works on data collected after Feb 6. 
    addpath('Raw');
    
    save_file = 1; 
    % Read in the new data
    % cal_data = csvread('16_01_17_raw_log_stationary.csv');
    data = csvread(file);

    time = data(:,1)/1000; 
    ax = data(:,2); ay = data(:,3); az = data(:,4);
    gx = data(:,5); gy = data(:,6); gz = data(:,7);
    mx = data(:,8); my = data(:,9); mz = data(:,10);
    roll = data(:,11); pitch = data(:,12); yaw = data(:,13); 
    fsr1 = data(:,14); fsr2 = data(:,15); fsr3 = data(:,16); 

    mean_dt = mean(diff(time,[],1));  
    mean_dt = 0.013; % Hacky - fix with own KF
    fs = 1/mean_dt;

    % Highpass filter design 
    fc = 0.2;
    [b,a] = butter(6,fc/(fs/2),'high');
    % filter = tf(b, a);
    % freqz(b,a)
    ax = filter(b,a,ax); ay = filter(b,a,ay); az = filter(b,a,az);
    filt = tf(b, a);

    ind = split_step_indices([fsr1 fsr2 fsr3], 0.5);

    % Array of Gait Factors 
    step_time = [];
    cadence = [];
    step_length = []; 
    step_height = [];
    foot_angle = []; % Records max yaw
    accel_planar = []; 
    accel_vertical = []; 
    
    step_l_time = zeros(length(ax), 1); 
    step_h_time = zeros(length(ax), 1); 

    % Kalman Filter for Positioning    
    A = [1      mean_dt     -(mean_dt^2)/2;...
         0      1           -mean_dt;...
         0      0           1];

    B = [mean_dt^2/2; mean_dt; 0];

    C = [1 mean_dt -(mean_dt^2)/2];

    Plant = ss(A,[B B],C,0,-1,'inputname',{'u' 'w'},'outputname','y');
    Q = 0.03;
    R = 0.02;
    [kalmf,L,P,M] = kalman(Plant,Q,R);

    a = A;
    b = [B B 0*B];
    c = [C;C];
    d = [0 0 0;0 0 1];
    Pl = ss(a,b,c,d,-1,'inputname',{'u' 'w' 'v'},'outputname',{'y' 'yv'});  
    sys = parallel(Pl,kalmf,1,1,[],[]);
    SimModel = feedback(sys,1,4,2,1);   % Close loop around input #4 and output #2
    SimModel = SimModel([1 3],[1 2 3]); % Delete yv from I/O list
    
    count = 1; 
    figure(2)
    for i=1:(length(ind)/2)
        s = ind(i*2 - 1);
        e = ind(i*2);

        yaw_start = yaw(s); 
        yaw_local = yaw(s:e) - yaw(s); 
        % Axis correction (fix later) 
        yaw_local = yaw_local.*(pi/180); % About z
        roll_local = roll(s:e).*(pi/180); % About y
        pitch_local = pitch(s:e).*(pi/180); % About x

        ax_local = ax(s:e);
        ay_local = ay(s:e);
        az_local = az(s:e);

        for j=1:length(s:e)
            rz = rotz(yaw_local(j));
            ry= roty(roll_local(j));
            rx = rotx(pitch_local(j));

            rot = rz*ry*rx;

            a_temp = [ax_local(j); ay_local(j); az_local(j)];
            a_new = rot*a_temp;
            ax_local(j) = a_new(1);
            ay_local(j) = a_new(2);
            az_local(j) = a_new(3);
        end

        num_pts = length(time(s:e));

        w = zeros(num_pts, 1); %sqrt(Q)*randn(n,1);
        v = zeros(num_pts, 1); %sqrt(R)*randn(n,1);

        [kpx,x] = lsim(SimModel,[w,v,ax_local]);
        [kpy,y] = lsim(SimModel,[w,v,ay_local]);
        [kpz,z] = lsim(SimModel,[w,v,az_local]);

        ye_x = kpx(:,2); % + v;     % measured response
        ye_y = kpy(:,2); % + v;     % measured response
        ye_z = kpz(:,2); % + v;     % measured response

        sl = sqrt(ye_x.^2 + ye_y.^2);

        % Saving Gait Factors for Static Plots 
        if((time(e) - time(s)) > 0.1)
            step_height(count) = max(ye_z);
            step_length(count) = max(sl);
            step_time(count) = time(e) - time(s); 
            cadence(count) = 60/step_time(count);
            foot_angle(count) = max(yaw_local);
            accel_planar(count) = max(max(ax_local), max(ay_local));
            accel_vertical(count) = max(az_local); 
            count = count+1;
        end
        
        step_l_time(s:e) = sl; 
        step_h_time(s:e) = ye_z;
        
        % Saving Gait Factors for Live Plots 

        subplot(3,1,1);
        plot(time(s:e) - time(s), ye_x); hold on;
        subplot(3,1,2);
        plot(time(s:e) - time(s), ye_y); hold on;
        subplot(3,1,3);
        plot(time(s:e) - time(s), ye_z); hold on;
    end 
    
    % outlier removal

    mean_dt = mean(diff(time,[],1)); 
    fs = 1/mean_dt; % 100 Hz Sampling
    num_pts = length(time); 
    acc_raw = [ax ay az]; 

    figure(1)
    subplot(4,1,1); hold on; grid on; 
    scatter([1:length(step_time)], step_time, 'r');
    xlabel('Step Number'); 
    ylabel('Step Time [s]');  
    title('Step Times'); 

    subplot(4,1,2); hold on; grid on; 
    scatter(step_length, step_height, 'b'); 
    xlabel('Step Length'); 
    ylabel('Step Height');  
    % title('Step Times'); 
    % plot(time, fsr2, 'g');
    % plot(time, fsr3, 'b');
    % plot(time, temp);
    % legend('x','y','z');

    subplot(4,1,3); hold on; grid on; 
    scatter(foot_angle.*(180/pi), cadence, 'g'); 
    xlabel('Foot Angle'); 
    ylabel('Cadence'); 
    
    subplot(4,1,4); hold on; grid on; 
    scatter(accel_planar, accel_vertical, 'g'); 
    xlabel('Planar Accel'); 
    ylabel('Cadence'); 
    
%     mean(step_time)
%     mean(step_length)
%     mean(step_height)
    
    step_num = transpose([1:length(step_time)]);
     
    figure(5);
    ax1 = subplot(3,1,1);
    plot(time, step_l_time, 'r'); grid on; hold on; 
    plot(time, step_h_time, 'b'); 
    legend('Step Length', 'Step Height'); 
    title('Time domain walk'); 
    w = zeros(length(time), 1); %sqrt(Q)*randn(n,1);
    v = zeros(length(time), 1); %sqrt(R)*randn(n,1);

    [kpx,x] = lsim(SimModel,[w,v,ax]);
    [kpy,y] = lsim(SimModel,[w,v,ay]);
    [kpz,z] = lsim(SimModel,[w,v,az]);

    ye_x = kpx(:,2); % + v;     % measured response
    ye_y = kpy(:,2); % + v;     % measured response
    ye_z = kpz(:,2); % + v;     % measured response
    
    ax2 = subplot(3,1,2);
    plot(time, sqrt(ye_x.^2 + ye_y.^2), 'r'); grid on; hold on; 
    plot(time, ye_z, 'b'); 
    legend('Step Length', 'Step Height'); 
    
    ax3 = subplot(3,1,3); 
    plot(time, pitch); 
    grid on; hold on; 
    legend('Pitch (deg)');
    
    linkaxes([ax1,ax2, ax3], 'x'); 
    raw_plot(data);
    if( save_file )
        
        fsr1 = smooth(fsr1, 15);
        fsr2 = smooth(fsr2, 15);
        fsr3 = smooth(fsr3, 15);
        static_factors = [step_num, transpose(step_time) transpose(step_length),...
                        transpose(step_height), transpose(foot_angle),...
                        transpose(accel_planar), transpose(accel_vertical)]; 

        dyn_factors = [time, step_l_time, step_h_time, pitch, fsr1, fsr2, fsr3];

        static_path = strcat('Processed/static_',file);
        dyn_path = strcat('Processed/dynamic_',file);
        csvwrite(static_path,static_factors);
        csvwrite(dyn_path,dyn_factors);
    end
end