function par = equalTrainingSamplePartition(groups,samplesize)

par.training = false(numel(groups),1);
par.test = false(numel(groups),1);

uniqueGroups = unique(groups(groups>0));
for iGroups = 1: numel(uniqueGroups)
    
    ind = find(groups == uniqueGroups(iGroups));
    p = randperm(numel(ind));
%     p = p(1:samplesize);
    par.training(ind(p(1:samplesize)),1) = true;
    par.test(ind(p(samplesize+1:end)),1) = true;
end
end