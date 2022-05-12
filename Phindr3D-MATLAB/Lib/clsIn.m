function C = clsIn(data,beta,dis)



if(isempty(data))
    disp('Datais empty');
    return;
end

% Initialize 
C.minClsSize = 5;
C.maxCls = 10;
C.minCls = 1;
C.S = [];
C.pmin = 0;
C.pmax = 0;
C.pmed = 0;

if(nargin == 1)
    beta = .05;
    dis = 'Euclidean';
elseif(nargin ==2)
    dis = 'Euclidean';
end


% sim = -1*sqDistance(data',data');

% assignin('base','x_x',x_x)
sim = pdist2(data,data,dis);
if(strcmpi(dis,'Euclidean'))
    sim = -1*sim;
elseif(strcmpi(dis,'Cosine'))
    sim = 1- sim;
elseif(strcmpi(dis,'Hamming'))
    sim = 1- sim;
end
x_x = logical(tril(ones(size(sim,1),size(sim,1)),-1));
C.pmed = median(sim(x_x)); 
[C.pmin, C.pmax] = preferenceRange(sim);
C.S = sim;
end