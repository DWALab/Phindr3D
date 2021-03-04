function [ L ] = resetLabelImage( L )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

uL = unique(L(:));
% L==0 is background. everything else is an object
uL = uL(uL>0);
for i = 1:numel(uL)
    ii = L == uL(i);
    L(ii) = i;
end

end

