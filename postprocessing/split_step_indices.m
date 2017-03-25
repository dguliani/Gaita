function [steps] = split_step_indices(fsr_grid, threshold)
    zero_ind = find(fsr_grid(:,1) < threshold);
    for i=1:length(fsr_grid(1,:))
        curr_fsr = smooth(fsr_grid(:,i),5);
        less = find(curr_fsr < threshold);
        zero_ind = intersect(zero_ind, less);
    end
    
    temp = zeros(length(fsr_grid),1);
    temp(zero_ind) = 10; 
    steps = find(abs(diff(temp)) > 1);     
end