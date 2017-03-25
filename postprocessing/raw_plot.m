function [fig] = raw_plot(data)

    time = data(:,1)/1000; 
    ax = data(:,2); ay = data(:,3); az = data(:,4);
    gx = data(:,5); gy = data(:,6); gz = data(:,7);
    mx = data(:,8); my = data(:,9); mz = data(:,10);
    roll = data(:,11); pitch = data(:,12); yaw = data(:,13); 
    fsr1 = data(:,14); fsr2 = data(:,15); fsr3 = data(:,16); 
    
    figure();
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

end