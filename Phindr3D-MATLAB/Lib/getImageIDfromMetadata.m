function [ imageIDcol ] = getImageIDfromMetadata( metadata,rootDir,exprIM )
%getImageIDfromMetadata Gets unique Image iD
%   Detailed explanation goes here

uCol = metadata(:,1); % First column is always one of the channels
str = uCol{10,:}; % Just pick any row
str = regexprep(str,rootDir,''); % Only retain the file name
m1 = regexpi(str,exprIM,'names');
ff = fieldnames(m1);
stackNuminRegexp = find(or(strcmpi('Stack',ff),strcmpi('Stacks',ff)));
% stackNuminRegexp = find(stackNuminRegexp);
for i = 1:size(uCol)
    str = regexprep(uCol{i,:},rootDir,'');
    mm = regexpi(str,exprIM,'tokenExtents');
    mm = mm{1,1};
    mm = mm(stackNuminRegexp,:);
    uCol{i,:} = str([1:mm(1)-1 mm(2)+1:end]);
end

uUCol = unique(uCol);
imageIDcol = zeros(size(metadata,1),1);
cnt = 1;
h = waitbar(0,'Setting Image IDs');
fprintf('Setting Image IDs ..................');
numUCol = numel(uUCol);
for i = 1:numUCol
    ii = strcmpi(uCol,uUCol{i,:});
    imageIDcol(ii,1) = cnt;
    cnt=cnt+1;
    waitbar(i./numUCol,h);
    fprintf('\b\b\b\b\b\b\b\b%7.3f%%',i*100/numUCol);
end
close(h);
fprintf('\n\n');
end

