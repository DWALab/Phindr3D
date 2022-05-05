function [ L ] = removeBorderObjects( L,dis )
%removeBorderObjects Removes objects that are touching the border of the
%image
% label = zeros(size(L));
borderimage = zeros(size(L));
borderimage(:,[1:dis end-dis:end]) = 1;borderimage([1:dis end-dis:end],:) = 1;

L2 = borderimage.*double(L);

uL = unique(L2);
for i = 1:numel(uL)
    
    L(L==uL(i)) = 0;
end


% Reset L to go from 1 to max
L = resetLabelImage(L);
end

