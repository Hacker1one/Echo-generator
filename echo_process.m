function echo_process(input_path, output_path, alpha, delay)
    try
        [x, Fs] = audioread(input_path);
        
        Nd = round(Fs * delay);
        
        y = zeros(size(x));
        y(1:Nd) = x(1:Nd);
        
        for n = (Nd+1):length(x)
            y(n) = x(n) - alpha * y(n - Nd);
        end
        
        y = y / max(abs(y));
        
        audiowrite(output_path, y, Fs);
        
        disp('Audio processing completed successfully');
        
    catch e
        disp(['Error: ' e.message]);
        rethrow(e);
    end
end

