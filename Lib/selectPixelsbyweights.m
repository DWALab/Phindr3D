function p = selectPixelsbyweights(x)

[n,q] = histc(x,[0:.025:1]); 
n = bsxfun(@rdivide,n,sum(n));
p = zeros(size(q));
% q = 1-q;
for i = 1:size(n,1)
    p(q==i) = n(i); 
end
p = 1-p;
p = sum(p>rand(size(q)),2);
p = p~=0;
p = x(p,:);
end
