function [ smoothIM ] = smoothImage( IM, cutOff )
%smoothImage Smooths image in freqeuncy domain
%   

[m,n] = size(IM);
if(cutOff>.99)
    cutOff = .99;
end
if(cutOff<0)
    cutOff = .01;
end
m = m/2;n = n/2;
[x,y] = meshgrid(-(m-.5):(m-.5),-(n-.5):(n-.5));
x = x./m;
y = y./m;
x = sqrt(x.^2 + y.^2);
x = double(x'<cutOff);
h = fspecial('average',50);
x = imfilter(x,h);
smoothIM = abs(ifft2((fftshift(fft2(IM))).*x));

end

